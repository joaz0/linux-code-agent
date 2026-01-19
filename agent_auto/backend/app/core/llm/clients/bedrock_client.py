# app/core/llm/clients/bedrock_client.py
import asyncio
import json
import boto3
from typing import Optional
from botocore.config import Config
from .base_client import BaseLLMClient
from app.config import settings


class BedrockClient(BaseLLMClient):
    """Cliente para AWS Bedrock API."""
    
    def __init__(self):
        super().__init__(
            provider="bedrock",
            model=settings.bedrock_model_id,
            timeout=settings.llm_timeout
        )
        
        # Configuração do cliente boto3
        config = Config(
            read_timeout=self.timeout,
            retries={'max_attempts': 3}
        )
        
        self.client = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_default_region,
            config=config
        )
    
    async def call(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        try:
            # Formato para Claude no Bedrock
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}]
                    }
                ]
            }
            
            if system_prompt:
                request_body["system"] = system_prompt
            
            # Bedrock não tem cliente async nativo, usamos run_in_executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(request_body),
                    contentType='application/json',
                    accept='application/json'
                )
            )
            
            response_body = json.loads(response['body'].read())
            
            # Estimar tokens
            output_text = response_body['content'][0]['text']
            prompt_tokens = len(prompt.split())  # Simplificado
            completion_tokens = len(output_text.split())
            
            self.update_metrics(prompt_tokens, completion_tokens)
            return output_text
            
        except Exception as e:
            self.record_error()
            self.logger.error(f"Bedrock API error: {e}")
            raise
    
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Custo do Claude no Bedrock: $0.003/1K input, $0.015/1K output"""
        input_cost = (prompt_tokens / 1000) * 0.003
        output_cost = (completion_tokens / 1000) * 0.015
        return input_cost + output_cost