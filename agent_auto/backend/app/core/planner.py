# app/core/planner.py
import os
import json
import logging
import re
from typing import Dict, Optional, Any
from datetime import datetime

# Enums e Configurações
from app.config import settings, TaskComplexity, LLMProvider
from app.core.aws_toolkit import AWSToolkitDetector
from app.core.llm.multi_provider import MultiProviderLLM

logger = logging.getLogger(__name__)

class Planner:
    def __init__(self, use_aws_toolkit: bool = True):
        """
        Inicializa o planner com suporte a multi-provider e rotacionamento inteligente.
        
        Args:
            use_aws_toolkit: Se True, ativa detecção de credenciais da AWS
        """
        self.use_aws_toolkit = use_aws_toolkit
        
        # 1. Tenta detectar credenciais AWS se solicitado (Zero-Config)
        self.aws_detector = AWSToolkitDetector() if use_aws_toolkit else None
        
        # 1.5 Garante que as variáveis de ambiente estão carregadas
        self._ensure_env_variables()
        
        # 2. Inicializa o cérebro central (Multi-Provider)
        # O MultiProvider já carrega as configs do .env e gerencia os clientes (Sonnet, DeepSeek, etc)
        self.multi_provider = MultiProviderLLM()
        
        logger.info(f"Planner inicializado. Providers ativos: {self.multi_provider.available_providers}")


    def _ensure_env_variables(self):
        """Garante que as variáveis de ambiente estão setadas a partir das settings."""
        import os
        from app.config import settings
        
        # Mapeamento de variáveis de ambiente
        env_mappings = {
            'OPENAI_API_KEY': settings.openai_api_key,
            'ANTHROPIC_API_KEY': settings.anthropic_api_key,
            'OPENROUTER_API_KEY': settings.openrouter_api_key,
            'GOOGLE_API_KEY': settings.gemini_api_key,
            'AWS_ACCESS_KEY_ID': settings.aws_access_key_id,
            'AWS_SECRET_ACCESS_KEY': settings.aws_secret_access_key,
            'AWS_DEFAULT_REGION': settings.aws_default_region
        }
        
        for env_var, value in env_mappings.items():
            if value and not os.getenv(env_var):
                os.environ[env_var] = value
                logger.debug(f"Setado {env_var} no ambiente a partir das settings")
                

    def _handle_fallback(self, task: str):
        """Fallback para tarefas simples quando LLM falha."""
        task_lower = task.lower().strip()
        
        simple_fallbacks = {
            "listar arquivos": {
                "tool": "execute_command",
                "params": {"command": "ls -la"},
                "_metadata": {"status": "planned", "source": "fallback"}
            },
            "verificar sistema": {
                "tool": "execute_command", 
                "params": {"command": "uname -a && echo 'Python:' && python3 --version"},
                "_metadata": {"status": "planned", "source": "fallback"}
            },
            "testar conexão": {
                "tool": "execute_command",
                "params": {"command": "echo 'Conectado ao sistema:' && whoami && pwd"},
                "_metadata": {"status": "planned", "source": "fallback"}
            },
            "verificar espaço": {
                "tool": "execute_command",
                "params": {"command": "df -h"},
                "_metadata": {"status": "planned", "source": "fallback"}
            }
        }
        
        for pattern, plan in simple_fallbacks.items():
            if pattern in task_lower:
                print(f"⚠️  Usando fallback para: {task}")
                return plan
        
        return None


    def plan(self, task: str, tools: dict, **kwargs) -> dict:
        """
        Gera um plano de execução para a tarefa.
        
        Args:
            task: A descrição do que deve ser feito.
            tools: As ferramentas disponíveis.
            **kwargs: Suporta 'complexity', 'force_provider', etc.
        """
        # 1. Determina a Complexidade (Argumento > Estimativa Automática > Padrão)
        complexity_arg = kwargs.get('complexity')
        if complexity_arg:
            try:
                # Tenta converter string para Enum (ex: "simple" -> TaskComplexity.SIMPLE)
                complexity = TaskComplexity(str(complexity_arg).lower())
            except ValueError:
                complexity = TaskComplexity.MEDIUM
        else:
            # Se não foi passado, estima baseado no texto da tarefa
            complexity = self._estimate_complexity(task)
        if complexity == TaskComplexity.SIMPLE:
            fallback_result = self._handle_fallback(task)
            if fallback_result:
                return fallback_result

        # 2. Verifica se há um provedor forçado (ex: force_provider='openai')
        force_provider_arg = kwargs.get('force_provider')
        force_provider = None
        if force_provider_arg:
            try:
                force_provider = LLMProvider(str(force_provider_arg).lower())
            except ValueError:
                logger.warning(f"Provider forçado inválido: {force_provider_arg}. Ignorando.")

        logger.info(f"📅 Planejando: '{task[:40]}...' [Complexidade: {complexity.value}] [Provider: {force_provider or 'AUTO'}]")

        # 3. Constrói o Prompt Otimizado
        prompt = self._build_prompt(task, tools)
        
        try:
            # 4. Executa via MultiProvider (Roteamento Inteligente)
            # O método generate_text do MultiProvider deve lidar com a escolha do modelo
            response_text = self.multi_provider.generate_text(
                prompt=prompt,
                complexity=complexity,
                provider=force_provider
            )
            
            # 5. Parse e Validação da Resposta
            plan_json = self._safe_parse_response(response_text)
            
            # Adiciona metadados úteis para debug
            plan_json["_metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "complexity": complexity.value,
                "provider_used": force_provider.value if force_provider else "auto_routed"
            }
            
            return plan_json

        except Exception as e:
            logger.error(f"❌ Falha crítica no planejamento: {e}")
            # Retorna um plano vazio/erro em vez de quebrar a aplicação
            return {
                "error": str(e),
                "tool": None,
                "params": {},
                "_metadata": {"status": "failed"}
            }

    def _build_prompt(self, task: str, tools: dict) -> str:
        """Constrói o prompt para o LLM."""
        tools_str = json.dumps(tools, indent=2) if tools else "Nenhuma ferramenta disponível."
        
        return (
            f"Você é um Agente Autônomo Especialista (SOTA 2026).\n\n"
            f"OBJETIVO: {task}\n\n"
            f"FERRAMENTAS DISPONÍVEIS:\n{tools_str}\n\n"
            f"INSTRUÇÕES:\n"
            f"1. Analise o objetivo e escolha a MELHOR ferramenta.\n"
            f"2. Retorne APENAS um JSON válido. Nada de markdown.\n"
            f"3. Formato obrigatório:\n"
            f'{{"tool": "nome_da_ferramenta", "params": {{ "param1": "valor" }} }}\n'
        )

    def _estimate_complexity(self, task: str) -> TaskComplexity:
        """Estima a complexidade da tarefa baseada em keywords."""
        task_lower = task.lower()
        
        # Keywords para Complexo (Refatoração, Debug, Arquitetura) -> Sonnet 4.5
        complex_keywords = ["refator", "debug", "otimiz", "implement", "arquitet", "fix", "corrig", "complex"]
        
        # Keywords para Simples (Leitura, Listagem) -> Bedrock/Flash
        simple_keywords = ["list", "mostr", "ver", "lê", "read", "show", "get", "ls", "cat"]
        
        if any(k in task_lower for k in complex_keywords):
            return TaskComplexity.COMPLEX
        elif any(k in task_lower for k in simple_keywords):
            return TaskComplexity.SIMPLE
        
        return TaskComplexity.MEDIUM

    def _safe_parse_response(self, raw_response: str) -> dict:
        """Limpa e converte a resposta do LLM para JSON de forma segura."""
        if not raw_response:
            raise ValueError("Resposta do LLM vazia")

        try:
            cleaned = raw_response.strip()
            
            # Remove blocos de código Markdown (```json ... ```)
            if "```" in cleaned:
                # Regex para extrair conteúdo dentro de ```json ... ``` ou apenas ``` ... ```
                match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
                if match:
                    cleaned = match.group(1)
            
            return json.loads(cleaned)
            
        except json.JSONDecodeError:
            logger.warning("Falha no JSONDecode direto. Tentando Regex fallback.")
            # Fallback: Tenta encontrar o primeiro objeto JSON válido na string
            try:
                match = re.search(r'\{.*\}', cleaned, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
            except Exception:
                pass
            
            # Se tudo falhar, loga o erro e o conteúdo bruto
            logger.error(f"Conteúdo inválido recebido: {raw_response[:100]}...")
            raise ValueError("LLM não retornou um JSON válido.")

    def get_metrics(self) -> dict:
        """Retorna métricas de uso acumuladas."""
        return self.multi_provider.get_metrics()


# ==============================================================================
# WRAPPER STANDALONE (Compatibilidade Legada)
# ==============================================================================
def plan(task: str, tools: dict, **kwargs) -> dict:
    """
    Função wrapper para manter compatibilidade com chamadas antigas.
    
    Agora suporta **kwargs para passar 'complexity' e 'force_provider' 
    para a nova classe Planner.
    """
    try:
        # Instancia o planner (que agora gerencia o multi-provider internamente)
        planner_instance = Planner()
        
        # Delega a execução passando todos os argumentos
        return planner_instance.plan(task, tools, **kwargs)
        
    except Exception as e:
        logger.error(f"Erro no wrapper plan(): {e}")
        return {"error": str(e), "tool": None, "params": {}}