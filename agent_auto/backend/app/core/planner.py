# app/core/planner.py
import os
import json
from typing import Dict, Optional
import logging
from datetime import datetime

# Importações condicionais para evitar erros se APIs não estiverem configuradas
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

# Sistema multi-provider
from app.core.multi_llm import MultiLLMProvider, ComplexityLevel
from app.core.aws_toolkit import AWSToolkitDetector

logger = logging.getLogger(__name__)

class Planner:
    def __init__(self, use_aws_toolkit: bool = True):
        """
        Inicializa o planner com suporte a multi-provider.
        
        Args:
            use_aws_toolkit: Se True, tenta usar AWS Toolkit antes de variáveis de ambiente
        """
        self.use_aws_toolkit = use_aws_toolkit
        self.aws_detector = AWSToolkitDetector() if use_aws_toolkit else None
        
        # Inicializa provedores LLM
        self._init_clients()
        
        # Sistema multi-provider
        self.multi_provider = MultiLLMProvider(
            use_aws_toolkit=use_aws_toolkit
        )
        
        logger.info(f"Planner inicializado. AWS Toolkit: {use_aws_toolkit}")
        logger.info(f"Provedores disponíveis: {self.multi_provider.get_available_providers()}")
    
    def _init_clients(self):
        """Inicializa clientes LLM com fallback para AWS Toolkit."""
        self.clients = {}
        
        # OpenAI
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.clients["openai"] = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Anthropic
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            self.clients["anthropic"] = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # AWS Bedrock (via Toolkit ou variáveis)
        if self.use_aws_toolkit and self.aws_detector:
            bedrock_creds = self.aws_detector.get_credentials()
            if bedrock_creds:
                import boto3
                self.clients["bedrock"] = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=bedrock_creds.get('access_key'),
                    aws_secret_access_key=bedrock_creds.get('secret_key'),
                    region_name=bedrock_creds.get('region', 'us-east-1')
                )
        elif os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            import boto3
            self.clients["bedrock"] = boto3.client(
                'bedrock-runtime',
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            )
    
    def plan(self, task: str, tools: dict, force_provider: Optional[str] = None) -> dict:
        """
        Retorna um plano usando o provedor mais adequado.
        
        Args:
            task: Descrição da tarefa
            tools: Dicionário de ferramentas disponíveis
            force_provider: Força uso de um provedor específico
            
        Returns:
            Dict com plano no formato {"tool": "...", "params": {...}}
        """
        prompt = self._build_prompt(task, tools)
        
        # Determina complexidade para seleção de provider
        complexity = self._estimate_complexity(task)
        
        try:
            if force_provider:
                # Usa provider forçado
                response = self._call_specific_provider(force_provider, prompt)
                provider_used = force_provider
            else:
                # Usa multi-provider com seleção inteligente
                response, provider_used = self.multi_provider.call(
                    prompt=prompt,
                    system_prompt="Você é um agente de sistema autônomo.",
                    complexity=complexity
                )
            
            # Parse seguro da resposta
            result = self._safe_parse_response(response)
            
            # Adiciona metadados
            result["_metadata"] = {
                "provider": provider_used,
                "complexity": complexity.value,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Plano gerado com provedor: {provider_used}")
            return result
            
        except Exception as e:
            logger.error(f"Erro no planejamento: {e}")
            # Fallback para OpenAI se disponível
            if "openai" in self.clients and not force_provider:
                logger.info("Tentando fallback para OpenAI...")
                return self.plan(task, tools, force_provider="openai")
            raise
    
    def _build_prompt(self, task: str, tools: dict) -> str:
        """Constrói prompt otimizado para LLM."""
        tools_str = json.dumps(tools, indent=2)
        
        return f"""Você é um agente de sistema autônomo.

OBJETIVO:
{task}

FERRAMENTAS DISPONÍVEIS:
{tools_str}

INSTRUÇÕES:
1. Analise o objetivo cuidadosamente
2. Escolha UMA ferramenta por vez
3. Forneça parâmetros específicos e acionáveis
4. Seja conciso e direto

RESPONDA APENAS EM JSON VÁLIDO:
{{"tool": "nome_da_ferramenta", "params": {{}}}}

NÃO inclua markdown, explicações ou texto adicional."""

    def _estimate_complexity(self, task: str) -> ComplexityLevel:
        """Estima complexidade da tarefa para seleção de provider."""
        task_lower = task.lower()
        
        # Heurística simples baseada em keywords
        simple_keywords = ["list", "show", "get", "read", "find", "ls", "pwd", "whoami"]
        medium_keywords = ["edit", "modify", "update", "add", "remove", "create", "write"]
        complex_keywords = ["refactor", "debug", "optimize", "implement", "multi", "system"]
        
        if any(keyword in task_lower for keyword in complex_keywords):
            return ComplexityLevel.COMPLEX
        elif any(keyword in task_lower for keyword in medium_keywords):
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.SIMPLE
    
    def _call_specific_provider(self, provider: str, prompt: str) -> str:
        """Chama um provedor específico."""
        if provider == "openai" and "openai" in self.clients:
            response = self.clients["openai"].chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        
        elif provider == "anthropic" and "anthropic" in self.clients:
            response = self.clients["anthropic"].messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        
        elif provider == "bedrock" and "bedrock" in self.clients:
            import json
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt}]
                    }
                ]
            }
            
            response = self.clients["bedrock"].invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20241022-v2:0",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
        
        else:
            raise ValueError(f"Provedor {provider} não disponível")
    
    def _safe_parse_response(self, raw_response: str) -> dict:
        """Parse seguro da resposta JSON com fallback para eval."""
        try:
            # Tenta json.loads primeiro
            cleaned = raw_response.strip()
            
            # Remove possíveis code blocks
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Fallback para eval (com segurança básica)
            try:
                # Verifica se parece seguro (apenas contém estruturas Python básicas)
                if all(c.isalnum() or c in ' {":,._-}' for c in cleaned):
                    result = eval(cleaned)
                    if isinstance(result, dict):
                        return result
            except:
                pass
            
            # Último recurso: extrair JSON com regex
            import re
            json_match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            raise ValueError(f"Não foi possível parsear resposta: {raw_response[:100]}...")
    
    def get_metrics(self) -> dict:
        """Retorna métricas de uso dos provedores."""
        return self.multi_provider.get_metrics()


# Função de compatibilidade com código existente
def plan(task: str, tools: dict) -> dict:
    """Função legacy para compatibilidade."""
    planner = Planner()
    return planner.plan(task, tools)
