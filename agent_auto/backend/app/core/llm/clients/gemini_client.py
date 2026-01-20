# app/core/llm/clients/gemini_client.py
import logging
from typing import Optional, Dict, Any

# SDK moderno do Google (2026)
from google import genai
from google.genai import types

from app.config import settings, LLMProvider
# ✅ CORREÇÃO: Usando o nome correto da classe base
from app.core.llm.clients.base_client import BaseLLMClient

logger = logging.getLogger(__name__)

class GeminiClient(BaseLLMClient):
    """Cliente para interagir com Google Gemini via SDK moderno (google-genai)"""
    
    def __init__(self):
        # ✅ Inicializa a classe pai para métricas e logs padronizados
        super().__init__(
            provider=LLMProvider.GEMINI,
            model=settings.gemini_model,
            timeout=settings.llm_timeout
        )

        if not settings.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY não configurada no .env")
            
        # Inicialização do novo cliente
        self.client = genai.Client(api_key=settings.gemini_api_key)
        
        logger.info(f"Gemini Client (v2) inicializado: {self.model}")

    async def call(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        **kwargs
    ) -> str:
        """
        Executa chamada ao Gemini usando o novo formato de API.
        """
        try:
            # Configuração de inferência
            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=8192,
                system_instruction=system_prompt,
                # Safety settings permissivos para coding
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_NONE"
                    ),
                ]
            )

            # Chamada simplificada do novo SDK
            # A maioria dos frameworks async roda isso em threadpool se a lib for síncrona,
            # mas o novo SDK do Google tem bom suporte.
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            # Coleta métricas de uso se disponível na resposta
            if hasattr(response, 'usage_metadata'):
                self.update_metrics(
                    prompt_tokens=response.usage_metadata.prompt_token_count,
                    completion_tokens=response.usage_metadata.candidates_token_count
                )
            
            return response.text

        except Exception as e:
            self.record_error()
            logger.error(f"Erro Gemini API: {str(e)}")
            raise

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Custo via Gemini 3.0 (Configuração central)."""
        # Pega custo do config.py
        base_input = settings.cost_per_1k_input.get(LLMProvider.GEMINI, 0.00125)
        
        input_cost = (prompt_tokens / 1000) * base_input
        output_cost = (completion_tokens / 1000) * (base_input * 4.0)
        return input_cost + output_cost