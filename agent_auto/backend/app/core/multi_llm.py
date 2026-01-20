# app/core/multi_llm.py
import os
import json
import time
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Importações condicionais
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)


class ComplexityLevel(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


@dataclass
class ProviderConfig:
    name: str
    model: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    priority: int  # 1 = mais prioritário


class MultiLLMProvider:
    """Sistema de rotacionamento inteligente entre múltiplos provedores LLM."""
    
    def __init__(self, use_aws_toolkit: bool = True):
        self.use_aws_toolkit = use_aws_toolkit
        self.providers = self._init_providers()
        self.metrics = {
            "total_calls": 0,
            "total_cost": 0.0,
            "calls_by_provider": {},
            "errors_by_provider": {},
            "response_times": {}
        }
        
        # Configuração de preferência por complexidade
        # Adicionado Gemini como opção em todas as categorias
        self.complexity_mapping = {
            ComplexityLevel.SIMPLE: ["openrouter", "gemini", "bedrock", "anthropic"],
            ComplexityLevel.MEDIUM: ["openrouter", "gemini", "bedrock", "anthropic"],
            ComplexityLevel.COMPLEX: ["openrouter", "anthropic", "gemini", "bedrock"]
        }
        
        logger.info(f"MultiLLMProvider inicializado com {len(self.providers)} provedores")
    
    def _init_providers(self) -> Dict[str, ProviderConfig]:
        """Inicializa provedores baseado na configuração disponível."""
        providers = {}
        
        # OpenAI
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            providers["openai"] = ProviderConfig(
                name="openai",
                model="gpt-4o",  # Atualizado para GPT-4o conforme config
                cost_per_1k_input=0.0025,
                cost_per_1k_output=0.010,
                priority=3
            )
        
        # Anthropic
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            providers["anthropic"] = ProviderConfig(
                name="anthropic",
                model="claude-3-5-sonnet-20241022",
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                priority=1
            )
        
        # Gemini (Novo)
        # Verifica GOOGLE_API_KEY conforme definido no config.py
        if GEMINI_AVAILABLE and os.getenv("GOOGLE_API_KEY"):
            providers["gemini"] = ProviderConfig(
                name="gemini",
                model="gemini-1.5-pro-latest",
                cost_per_1k_input=0.00125,
                cost_per_1k_output=0.005,
                priority=2
            )
        
        # AWS Bedrock (checa disponibilidade)
        bedrock_available = False
        if self.use_aws_toolkit:
            try:
                from app.core.aws_toolkit import AWSToolkitDetector
                detector = AWSToolkitDetector()
                if detector.detect_credentials():
                    bedrock_available = True
            except:
                pass
        
        if not bedrock_available and os.getenv("AWS_ACCESS_KEY_ID"):
            bedrock_available = True
        
        if bedrock_available:
            providers["bedrock"] = ProviderConfig(
                name="bedrock",
                model="anthropic.claude-3-5-sonnet-20241022-v2:0",
                cost_per_1k_input=0.003,
                cost_per_1k_output=0.015,
                priority=2
            )
        
        # OpenRouter (se configurado)
        if os.getenv("OPENROUTER_API_KEY"):
            providers["openrouter"] = ProviderConfig(
                name="openrouter",
                model="deepseek/deepseek-r1:free",
                cost_per_1k_input=0.0024,
                cost_per_1k_output=0.012,
                priority=2
            )
        
        return providers
    
    def get_available_providers(self) -> List[str]:
        """Retorna lista de provedores disponíveis."""
        return list(self.providers.keys())
    
    def select_provider(self, complexity: ComplexityLevel) -> Optional[str]:
        """Seleciona o melhor provedor para a complexidade."""
        preferred = self.complexity_mapping.get(complexity, [])
        
        # Filtra apenas provedores disponíveis
        for provider in preferred:
            if provider in self.providers:
                return provider
        
        # Fallback: usa qualquer provedor disponível
        if self.providers:
            return list(self.providers.keys())[0]
        
        return None
    
    def call(self, prompt: str, system_prompt: str, complexity: ComplexityLevel) -> Tuple[str, str]:
        """
        Chama o LLM usando o provedor mais adequado.
        
        Returns:
            Tuple[resposta, provedor_usado]
        """
        start_time = time.time()
        
        # Seleciona provedor
        provider_name = self.select_provider(complexity)
        if not provider_name:
            raise ValueError("Nenhum provedor LLM disponível. Verifique suas API Keys no .env")
        
        try:
            response = self._call_provider(provider_name, prompt, system_prompt)
            
            # Calcula métricas
            elapsed = time.time() - start_time
            self._update_metrics(provider_name, elapsed, prompt, response)
            
            logger.info(f"Chamada LLM bem-sucedida com {provider_name} ({elapsed:.2f}s)")
            return response, provider_name
            
        except Exception as e:
            logger.error(f"Erro com provedor {provider_name}: {e}")
            self._record_error(provider_name)
            
            # Tenta fallback
            if len(self.providers) > 1:
                logger.info(f"Tentando fallback para outro provedor...")
                available = [p for p in self.providers.keys() if p != provider_name]
                for fallback_provider in available:
                    try:
                        logger.info(f"Tentando fallback com: {fallback_provider}")
                        response = self._call_provider(fallback_provider, prompt, system_prompt)
                        elapsed = time.time() - start_time
                        self._update_metrics(fallback_provider, elapsed, prompt, response)
                        logger.info(f"Fallback bem-sucedido com {fallback_provider}")
                        return response, fallback_provider
                    except Exception as fallback_error:
                        logger.error(f"Erro no fallback {fallback_provider}: {fallback_error}")
                        continue
            
            raise Exception(f"Todos os provedores falharam: {e}")
    
    def _call_provider(self, provider_name: str, prompt: str, system_prompt: str) -> str:
        """Executa chamada para um provedor específico."""
        if provider_name == "openai":
            return self._call_openai(prompt, system_prompt)
        elif provider_name == "anthropic":
            return self._call_anthropic(prompt, system_prompt)
        elif provider_name == "bedrock":
            return self._call_bedrock(prompt, system_prompt)
        elif provider_name == "openrouter":
            return self._call_openrouter(prompt, system_prompt)
        elif provider_name == "gemini":
            return self._call_gemini(prompt, system_prompt)
        else:
            raise ValueError(f"Provedor não suportado: {provider_name}")
    
    def _call_openai(self, prompt: str, system_prompt: str) -> str:
        """Chama OpenAI API."""
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=self.providers["openai"].model,
            messages=messages,
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str, system_prompt: str) -> str:
        """Chama Anthropic API."""
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model=self.providers["anthropic"].model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text

    def _call_gemini(self, prompt: str, system_prompt: str) -> str:
        """Chama Google Gemini API."""
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        model = genai.GenerativeModel(
            model_name=self.providers["gemini"].model,
            system_instruction=system_prompt,
            safety_settings=[
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        )
        
        generation_config = genai.GenerationConfig(
            temperature=0.1,
            max_output_tokens=8192
        )
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text
    
    def _call_bedrock(self, prompt: str, system_prompt: str) -> str:
        """Chama AWS Bedrock API."""
        import boto3
        import json
        
        # Tenta primeiro com AWS Toolkit
        client = None
        if self.use_aws_toolkit:
            from app.core.aws_toolkit import AWSToolkitDetector
            detector = AWSToolkitDetector()
            creds = detector.get_credentials()
            
            if creds:
                client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=creds['access_key'],
                    aws_secret_access_key=creds['secret_key'],
                    region_name=creds.get('region', 'us-east-1')
                )
        
        if not client:
            # Fallback para variáveis de ambiente
            client = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            )
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]
                }
            ]
        }
        
        response = client.invoke_model(
            modelId=self.providers["bedrock"].model,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    def _call_openrouter(self, prompt: str, system_prompt: str) -> str:
        """Chama OpenRouter API."""
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=self.providers["openrouter"].model,
            messages=messages,
            temperature=0.1
        )
        
        return response.choices[0].message.content
    
    def _update_metrics(self, provider: str, response_time: float, prompt: str, response: str):
        """Atualiza métricas após chamada bem-sucedida."""
        self.metrics["total_calls"] += 1
        
        if provider not in self.metrics["calls_by_provider"]:
            self.metrics["calls_by_provider"][provider] = 0
            self.metrics["response_times"][provider] = []
        
        self.metrics["calls_by_provider"][provider] += 1
        self.metrics["response_times"][provider].append(response_time)
        
        # Estima custo (aproximado)
        prompt_tokens = len(prompt.split()) // 0.75  # Aproximação
        response_tokens = len(response.split()) // 0.75
        
        if provider in self.providers:
            config = self.providers[provider]
            cost = (prompt_tokens / 1000 * config.cost_per_1k_input +
                   response_tokens / 1000 * config.cost_per_1k_output)
            self.metrics["total_cost"] += cost
    
    def _record_error(self, provider: str):
        """Registra erro para um provedor."""
        if provider not in self.metrics["errors_by_provider"]:
            self.metrics["errors_by_provider"][provider] = 0
        self.metrics["errors_by_provider"][provider] += 1
    
    def get_metrics(self) -> dict:
        """Retorna métricas detalhadas."""
        metrics = self.metrics.copy()
        
        # Calcula médias
        for provider, times in metrics.get("response_times", {}).items():
            if times:
                metrics["response_times"][provider] = {
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "total_calls": len(times)
                }
        
        # Adiciona timestamp
        metrics["timestamp"] = datetime.now().isoformat()
        
        return metrics
    
    def get_cost_estimate(self, task: str) -> dict:
        """Estima custo para diferentes provedores."""
        word_count = len(task.split())
        estimated_tokens = word_count * 1.3  # Aproximação
        
        estimates = {}
        for provider, config in self.providers.items():
            cost = (estimated_tokens / 1000 * config.cost_per_1k_input +
                   (estimated_tokens * 0.5) / 1000 * config.cost_per_1k_output)
            
            estimates[provider] = {
                "estimated_cost_usd": round(cost, 4),
                "estimated_tokens": int(estimated_tokens),
                "model": config.model
            }
        
        return estimates