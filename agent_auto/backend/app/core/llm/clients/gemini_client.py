# app/core/llm/clients/gemini_client.py
import google.generativeai as genai
from typing import Optional, Dict, Any
import logging

from app.config import settings
from app.core.llm.clients.base_client import BaseClient

logger = logging.getLogger(__name__)

class GeminiClient(BaseClient):
    """Cliente para interagir com Google Gemini 1.5 Pro via SDK oficial"""
    
    def __init__(self):
        if not settings.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY não configurada no .env")
            
        # Configura a chave API
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
        
        # Configurações de segurança "permissivas" para não bloquear código
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        logger.info(f"Gemini Client inicializado com modelo: {self.model_name}")

    async def call(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        **kwargs
    ) -> str:
        """
        Executa chamada ao Gemini.
        """
        try:
            # Configura o modelo
            # Nota: O Gemini 1.5 aceita 'system_instruction' na inicialização
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt,
                safety_settings=self.safety_settings
            )
            
            # Configuração de geração
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=8192,  # Janela de output grande
                candidate_count=1
            )

            # Executa a geração (a chamada padrão do SDK é síncrona, mas rápida)
            response = model.generate_content(
                prompt, 
                generation_config=generation_config
            )
            
            # Retorna o texto gerado
            return response.text

        except Exception as e:
            logger.error(f"Erro ao chamar Gemini: {str(e)}")
            raise Exception(f"Erro na chamada Gemini: {str(e)}")

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas básicas do cliente"""
        return {
            "provider": "gemini",
            "model": self.model_name
        }
        
    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Estima o custo baseado na tabela oficial do Gemini 1.5 Pro (Preços < 128k context)
        Input: $1.25 / 1M tokens
        Output: $5.00 / 1M tokens
        """
        input_cost = (prompt_tokens / 1_000_000) * 1.25
        output_cost = (completion_tokens / 1_000_000) * 5.00
        return input_cost + output_cost

    @property
    def model(self) -> str:
        return self.model_name