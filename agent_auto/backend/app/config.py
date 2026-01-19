"""Configuração centralizada do sistema"""
import os
from pathlib import Path
from dotenv import load_dotenv

backend_dir = Path(__file__).parent.parent
env_path = backend_dir / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

class Config:
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY', '')
    LLM_PROVIDER: str = os.getenv('LLM_PROVIDER', 'anthropic')
    LLM_MODEL: str = os.getenv('LLM_MODEL', 'claude-sonnet-4-20250514')
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    
    @classmethod
    def validate(cls) -> bool:
        has_openai = cls.OPENAI_API_KEY and not cls.OPENAI_API_KEY.startswith('sk-your')
        has_anthropic = cls.ANTHROPIC_API_KEY and not cls.ANTHROPIC_API_KEY.startswith('sk-ant-your')
        if not (has_openai or has_anthropic):
            print("❌ Configure pelo menos uma API key no .env")
            return False
        if cls.LLM_PROVIDER == 'openai' and not has_openai:
            print("❌ LLM_PROVIDER=openai mas OPENAI_API_KEY não configurada!")
            return False
        if cls.LLM_PROVIDER == 'anthropic' and not has_anthropic:
            print("❌ LLM_PROVIDER=anthropic mas ANTHROPIC_API_KEY não configurada!")
            return False
        return True
    
    @classmethod
    def get_llm_client(cls):
        if cls.LLM_PROVIDER == 'openai':
            from openai import OpenAI
            return OpenAI(api_key=cls.OPENAI_API_KEY)
        elif cls.LLM_PROVIDER == 'anthropic':
            from anthropic import Anthropic
            return Anthropic(api_key=cls.ANTHROPIC_API_KEY)
        else:
            raise ValueError(f"LLM_PROVIDER inválido: {cls.LLM_PROVIDER}")

config = Config()
