# 📘 Linux Code Agent - Documentação Completa

**Versão:** 0.1.0  
**Status:** MVP Funcional  
**Última Atualização:** Janeiro 2026

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Instalação](#instalação)
4. [Configuração](#configuração)
5. [Uso da API](#uso-da-api)
6. [Desenvolvimento](#desenvolvimento)
7. [Segurança](#segurança)
8. [Roadmap](#roadmap)
9. [Troubleshooting](#troubleshooting)
10. [Contribuindo](#contribuindo)

---

## 🎯 Visão Geral

### O que é?

Linux Code Agent é um **agente de desenvolvimento autônomo e local** que combina:

- 🧠 **Inteligência Artificial** (LLM) para planejamento
- 🔧 **Execução Real** de ações no sistema
- 🌐 **API REST** completa e documentada
- 🔐 **Controle Total** - 100% local, sem upload de código

### Posicionamento no Mercado

| Feature | Amazon Q | GitHub Copilot | Cursor | **Linux Code Agent** |
|---------|----------|----------------|--------|---------------------|
| Execução Local | ❌ | ❌ | ❌ | ✅ |
| Ações Reais no Sistema | ⚠️ Cloud | ❌ | ⚠️ Limitado | ✅ |
| Planning Inteligente | ✅ | ❌ | ✅ | ✅ |
| API REST | ❌ | ❌ | ❌ | ✅ |
| Open Source | ❌ | ❌ | ❌ | ✅ |
| Extensível | ❌ | ❌ | ⚠️ | ✅ |
| Background Tasks | ✅ | ❌ | ⚠️ | ✅ |
| Auditável | ⚠️ | ❌ | ⚠️ | ✅ |
| Sem Vendor Lock-in | ❌ | ❌ | ❌ | ✅ |

### Casos de Uso

#### ✅ Implementados

- Automação de tarefas repetitivas
- Manipulação de arquivos e diretórios
- Execução de comandos shell
- Operações git básicas
- Geração de código e documentação

#### 🔜 Planejados

- Debugging assistido
- Refatoração inteligente
- Testes automatizados
- Deploy e CI/CD
- Code review automatizado

---

## 🏗️ Arquitetura

### Visão Geral

```
┌─────────────────────────────────────────┐
│         CLIENTE (HTTP/REST)              │
│  cURL | Python | VSCode | Web UI         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         API LAYER (FastAPI)              │
│  • Routes (tasks.py)                     │
│  • Validation (Pydantic)                 │
│  • OpenAPI/Swagger                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       SERVICE LAYER                      │
│  • TaskService                           │
│  • State Management                      │
│  • Lifecycle Control                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       CORE LAYER (Agent)                 │
│  • Agent (Orchestrator)                  │
│  • Planner (LLM Decision)                │
│  • Executor (Tool Runner)                │
│  • Registry (Tool Manager)               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       TOOLS LAYER                        │
│  • Shell (commands)                      │
│  • FileSystem (I/O)                      │
│  • Git (version control)                 │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│       OPERATING SYSTEM                   │
└─────────────────────────────────────────┘
```

### Camadas e Responsabilidades

#### 1. API Layer (`app/api/`)

**Responsabilidade:** Interface HTTP

- Receber requests HTTP
- Validar entrada via Pydantic schemas
- Chamar services apropriados
- Retornar responses formatadas
- **NÃO** contém lógica de negócio

**Arquivos:**
- `routes/tasks.py` - Endpoints de tasks

**Endpoints:**
```
POST   /tasks              - Criar task
GET    /tasks              - Listar tasks
GET    /tasks/{id}         - Buscar task
POST   /tasks/{id}/cancel  - Cancelar task
GET    /tasks/stats        - Estatísticas
GET    /health             - Health check
```

#### 2. Service Layer (`app/services/`)

**Responsabilidade:** Gerenciamento de estado

- Criar e registrar tasks
- Atualizar status (pending → running → completed/failed)
- Armazenar logs e resultados
- Controlar ciclo de vida
- **NÃO** executa ações

**Arquivos:**
- `task_service.py` - Gerenciador principal

**Métodos principais:**
```python
create_task(task_data) -> TaskStatus
get_task(task_id) -> TaskStatus
update_state(task_id, new_state)
complete_task(task_id, result)
cancel_task(task_id)
add_step(task_id, description)
```

#### 3. Core Layer (`app/core/`)

**Responsabilidade:** Inteligência e orquestração

- Decidir ações via LLM
- Orquestrar execução
- Gerenciar tools
- **NÃO** conhece HTTP

**Arquivos:**
- `agent.py` - Orquestrador principal
- `planner.py` - Decisões via LLM
- `executor.py` - Execução de tools
- `registry.py` - Registro de tools

**Fluxo:**
```python
Agent.execute(objective)
  → Planner.create_plan(objective)
    → LLM decide qual tool usar
  → Executor.execute_plan(plan)
    → Chama tools via Registry
  → Retorna TaskResult
```

#### 4. Tools Layer (`app/tools/`)

**Responsabilidade:** Ações reais no sistema

- Executar comandos
- Manipular arquivos
- Interagir com git
- **NÃO** decide quando executar

**Arquivos:**
- `shell.py` - Execução de comandos
- `fs.py` - FileSystem operations
- `git.py` - Git operations

**Interface padrão:**
```python
def tool_function(params) -> str:
    """Executa ação e retorna resultado"""
    pass
```

#### 5. Schemas Layer (`app/schemas/`)

**Responsabilidade:** Contratos de dados

- Validação de entrada
- Serialização/deserialização
- Geração de OpenAPI
- **NÃO** contém lógica

**Arquivos:**
- `task_base.py` - Input da API
- `task_status.py` - Estado da task
- `task_execution.py` - Resultado

### Modelo de Dados

#### TaskStatus

```python
{
  "id": "uuid",
  "objective": "string",
  "context": {...},
  "state": "pending|running|completed|failed|cancelled",
  "created_at": "datetime",
  "updated_at": "datetime",
  "logs": [
    {"timestamp": "...", "message": "..."}
  ],
  "steps": [
    {"timestamp": "...", "description": "..."}
  ],
  "result": {
    "success": bool,
    "output": "string",
    "error": "string",
    "actions_taken": [...]
  }
}
```

#### Ciclo de Vida de uma Task

```
CREATE
  ↓
PENDING (aguardando execução)
  ↓
RUNNING (executando em background)
  ↓
  ├─→ COMPLETED (sucesso)
  ├─→ FAILED (erro)
  └─→ CANCELLED (cancelada pelo usuário)
```

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.10+
- pip
- git
- API Key (OpenAI ou Anthropic)

### Instalação Rápida

```bash
# 1. Clone/navegue até o projeto
cd ~/Documentos/agent_autonomo/agent_auto/backend

# 2. Criar virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
nano .env  # Editar com suas API keys

# 5. Iniciar servidor
python3 -m app.app
```

### Estrutura de Diretórios

```
backend/
├── .env                    # Configuração (API keys)
├── requirements.txt        # Dependências Python
├── venv/                   # Virtual environment
│
├── app/
│   ├── __init__.py
│   ├── app.py             # FastAPI application
│   ├── config.py          # Configuração centralizada
│   │
│   ├── api/
│   │   └── routes/
│   │       └── tasks.py   # Endpoints HTTP
│   │
│   ├── core/
│   │   ├── agent.py       # Orquestrador
│   │   ├── planner.py     # LLM planning
│   │   ├── executor.py    # Executor de tools
│   │   └── registry.py    # Registro de tools
│   │
│   ├── tools/
│   │   ├── shell.py       # Comandos shell
│   │   ├── fs.py          # FileSystem
│   │   └── git.py         # Git operations
│   │
│   ├── services/
│   │   └── task_service.py # Gerenciador de tasks
│   │
│   └── schemas/
│       ├── task_base.py
│       ├── task_execution.py
│       └── task_status.py
│
└── tests/
    └── test_integration.py
```

---

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# ==========================================
# API KEYS (configure pelo menos uma)
# ==========================================
OPENAI_API_KEY=sk-proj-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# ==========================================
# LLM CONFIGURATION
# ==========================================
# Provider: openai | anthropic
LLM_PROVIDER=anthropic

# Models disponíveis:
# OpenAI: gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo
# Anthropic: claude-sonnet-4-20250514, claude-opus-4-5-20251101
LLM_MODEL=claude-sonnet-4-20250514

# ==========================================
# API SETTINGS
# ==========================================
API_HOST=0.0.0.0
API_PORT=8000

# ==========================================
# SECURITY (futuro)
# ==========================================
# ALLOWED_COMMANDS=ls,cat,git
# SANDBOX_MODE=false
# READ_ONLY_MODE=false
```

### Configuração do LLM

#### Usar OpenAI

```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
OPENAI_API_KEY=sk-proj-your-key
```

#### Usar Anthropic (Claude)

```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-20250514
ANTHROPIC_API_KEY=sk-ant-your-key
```

### Validação da Configuração

```bash
# Testar se config está OK
python3 -c "from app.config import config; config.validate()"

# Ver configuração atual
python3 << EOF
from app.config import config
print(f"Provider: {config.LLM_PROVIDER}")
print(f"Model: {config.LLM_MODEL}")
print(f"API Host: {config.API_HOST}:{config.API_PORT}")
EOF
```

---

## 🌐 Uso da API

### Documentação Interativa

Após iniciar o servidor:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints

#### 1. Health Check

```bash
GET /health

curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "tasks": {
    "total": 10,
    "pending": 2,
    "running": 1,
    "completed": 6,
    "failed": 1,
    "cancelled": 0
  }
}
```

#### 2. Criar Task

```bash
POST /tasks

curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Criar arquivo README.md com documentação",
    "context": {
      "project": "my-app",
      "language": "python"
    }
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "objective": "Criar arquivo README.md com documentação",
  "context": {"project": "my-app"},
  "state": "pending",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T10:00:00Z",
  "logs": [
    {
      "timestamp": "2026-01-18T10:00:00Z",
      "message": "Task criada: Criar arquivo README.md"
    }
  ],
  "steps": [],
  "result": null
}
```

#### 3. Buscar Task

```bash
GET /tasks/{id}

curl http://localhost:8000/tasks/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "completed",
  "logs": [...],
  "steps": [
    {
      "timestamp": "2026-01-18T10:00:05Z",
      "description": "write_file: README.md"
    }
  ],
  "result": {
    "success": true,
    "output": "Arquivo README.md criado com sucesso",
    "error": null,
    "actions_taken": [...]
  }
}
```

#### 4. Listar Tasks

```bash
GET /tasks?state=completed&limit=10

curl "http://localhost:8000/tasks?state=completed&limit=10"
```

**Response:**
```json
{
  "tasks": [...],
  "total": 5
}
```

#### 5. Cancelar Task

```bash
POST /tasks/{id}/cancel

curl -X POST http://localhost:8000/tasks/550e8400.../cancel
```

#### 6. Estatísticas

```bash
GET /tasks/stats

curl http://localhost:8000/tasks/stats
```

**Response:**
```json
{
  "total": 10,
  "pending": 2,
  "running": 1,
  "completed": 6,
  "failed": 1,
  "cancelled": 0
}
```

### Exemplos de Uso

#### Python

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# Criar task
response = requests.post(
    f"{BASE_URL}/tasks",
    json={
        "objective": "Listar arquivos .py no diretório atual",
        "context": None
    }
)
task = response.json()
task_id = task["id"]

print(f"Task criada: {task_id}")

# Aguardar execução
time.sleep(3)

# Ver resultado
result = requests.get(f"{BASE_URL}/tasks/{task_id}")
print(result.json())
```

#### JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function createTask(objective) {
  const response = await axios.post(`${BASE_URL}/tasks`, {
    objective,
    context: null
  });
  return response.data;
}

async function getTask(taskId) {
  const response = await axios.get(`${BASE_URL}/tasks/${taskId}`);
  return response.data;
}

// Uso
(async () => {
  const task = await createTask('Criar arquivo test.txt');
  console.log('Task ID:', task.id);
  
  // Aguardar
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  const result = await getTask(task.id);
  console.log('Resultado:', result);
})();
```

---

## 💻 Desenvolvimento

### Adicionar uma Nova Tool

#### 1. Criar arquivo da tool

```python
# app/tools/docker.py
"""Docker operations tool"""

def docker_ps(all: bool = False) -> str:
    """List docker containers"""
    import subprocess
    cmd = ["docker", "ps"]
    if all:
        cmd.append("-a")
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )
    return result.stdout

def docker_build(path: str, tag: str) -> str:
    """Build docker image"""
    import subprocess
    result = subprocess.run(
        ["docker", "build", "-t", tag, path],
        capture_output=True,
        text=True
    )
    return result.stdout
```

#### 2. Registrar no registry

```python
# app/core/registry.py
from app.tools import docker

TOOLS = {
    # ... existing tools
    "docker_ps": docker.docker_ps,
    "docker_build": docker.docker_build,
}
```

#### 3. Usar via agent

```python
agent = Agent()
result = agent.execute("Listar containers docker ativos")
```

### Executar Testes

```bash
# Testes de integração
python test_integration.py

# Testes unitários (futuro)
pytest tests/

# Coverage
pytest --cov=app tests/
```

### Debug

```python
# Ativar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Ou via .env
LOG_LEVEL=DEBUG
```

### Hot Reload

```bash
# Uvicorn com auto-reload
uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```

---

## 🔐 Segurança

### Implementado (v0.1.0)

✅ **Execução Local**
- Nenhum código sai do ambiente
- API keys armazenadas localmente

✅ **Thread-Safe**
- Gerenciamento de estado com locks
- Seguro para requests concorrentes

✅ **Validação de Entrada**
- Pydantic schemas
- Type checking automático

### Planejado (v0.2.0+)

🔜 **Allowlist de Comandos**
```env
ALLOWED_COMMANDS=ls,cat,git,python
BLOCKED_COMMANDS=rm,mkfs,dd
```

🔜 **Sandbox de Execução**
- Execução em container isolado
- Limite de recursos (CPU, RAM)
- Timeout configurável

🔜 **Confirmação de Ações Destrutivas**
```python
# Agent solicita confirmação antes de:
# - Deletar arquivos
# - Modificar código existente
# - Executar comandos perigosos
```

🔜 **Read-Only Mode**
```env
READ_ONLY_MODE=true  # Agent só pode ler, não modificar
```

🔜 **Audit Logs**
- Log persistente de todas as ações
- Rastreabilidade completa
- Exportação para SIEM

### Boas Práticas

1. **Nunca commitar .env**
   ```gitignore
   .env
   .env.local
   *.key
   ```

2. **Usar API keys com escopo mínimo**
   - OpenAI: Apenas "Model usage"
   - Anthropic: Apenas "Messages API"

3. **Executar em ambiente isolado**
   - VM dedicada
   - Container Docker
   - Sandbox local

4. **Revisar logs regularmente**
   ```bash
   GET /tasks?state=failed  # Ver falhas
   GET /tasks/stats         # Monitorar uso
   ```

---

## 🗺️ Roadmap

### ✅ Fase 1 - MVP Funcional (CONCLUÍDA)

**Status:** v0.1.0 - Janeiro 2026

- [x] Arquitetura modular enterprise
- [x] API REST completa
- [x] TaskService com estado
- [x] Agent com planning via LLM
- [x] Tools básicas (shell, fs, git)
- [x] Background execution
- [x] Documentação OpenAPI
- [x] Logs e status em tempo real

### 🔄 Fase 2 - Autonomia Avançada (EM DESENVOLVIMENTO)

**Target:** v0.2.0 - Fevereiro 2026

#### Core Enhancements
- [ ] **Multi-step Planning**
  - Quebrar objetivos complexos em subtasks
  - Dependências entre tasks
  - Execução paralela quando possível

- [ ] **Self-Correction Loop**
  - Observe → Act → Evaluate → Refine
  - Retry inteligente em caso de falha
  - Aprendizado de erros anteriores

- [ ] **Tool Chaining**
  - Composição automática de tools
  - Pipeline de transformação de dados
  - Otimização de sequência

#### Memory & Context
- [ ] **Memória Persistente**
  - SQLite/PostgreSQL backend
  - Histórico de tasks
  - Context window management

- [ ] **Context Awareness**
  - Análise do projeto atual
  - Detecção de padrões de código
  - Sugestões baseadas em histórico

#### Tools Expansion
- [ ] **Code Analysis**
  - AST parsing
  - Dependency analysis
  - Complexity metrics

- [ ] **Testing Tools**
  - Unit test generation
  - Integration test scaffolding
  - Coverage analysis

- [ ] **Refactoring Tools**
  - Extract method/class
  - Rename symbols
  - Dead code elimination

### 🚀 Fase 3 - Produção Enterprise (PLANEJADO)

**Target:** v0.3.0 - Março 2026

#### Infrastructure
- [ ] **Distributed Workers**
  - Celery task queue
  - Redis for coordination
  - Horizontal scaling

- [ ] **Monitoring & Observability**
  - Prometheus metrics
  - Grafana dashboards
  - Distributed tracing (Jaeger)

- [ ] **High Availability**
  - Load balancing
  - Failover automático
  - Health checks avançados

#### Security
- [ ] **Authentication & Authorization**
  - JWT tokens
  - Role-based access control
  - API key management

- [ ] **Sandbox Execution**
  - Docker containers por task
  - Resource limits
  - Network isolation

- [ ] **Audit & Compliance**
  - Audit trail completo
  - GDPR compliance
  - SOC 2 readiness

#### Performance
- [ ] **Caching Layer**
  - Redis cache
  - LLM response caching
  - Tool result memoization

- [ ] **Rate Limiting**
  - Per-user limits
  - Token bucket algorithm
  - Graceful degradation

### 🎨 Fase 4 - Interfaces de Usuário (PLANEJADO)

**Target:** v0.4.0 - Abril 2026

#### VSCode Extension
- [ ] **Core Features**
  - Palette commands
  - Inline suggestions
  - Status bar integration
  - Task panel

- [ ] **Advanced Features**
  - Diff preview
  - Multi-file refactoring
  - Test runner integration

#### Web UI
- [ ] **Dashboard**
  - Task history
  - Real-time logs
  - Statistics & charts

- [ ] **Interactive Editor**
  - Code preview
  - Accept/reject changes
  - Manual intervention

#### CLI Tool
- [ ] **Command Line Interface**
  ```bash
  code-agent run "create REST API"
  code-agent list
  code-agent status <task-id>
  code-agent cancel <task-id>
  ```

### 🌟 Fase 5 - AI Superpowers (FUTURO)

**Target:** v1.0.0 - Q3 2026

#### Advanced AI
- [ ] **Multi-Agent Collaboration**
  - Specialized agents (frontend, backend, devops)
  - Agent negotiation protocol
  - Consensus decision making

- [ ] **Fine-tuned Models**
  - Project-specific fine-tuning
  - Code style learning
  - Pattern recognition

- [ ] **Proactive Suggestions**
  - Code smell detection
  - Performance optimization hints
  - Security vulnerability scanning

#### Ecosystem
- [ ] **Plugin System**
  - Community tools marketplace
  - Custom LLM providers
  - Integration with IDEs

- [ ] **Cloud Offering**
  - Managed hosting
  - SaaS deployment
  - Enterprise support

---

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Erro: "No module named 'app.config'"

**Causa:** Arquivo `app/config.py` não existe

**Solução:**
```bash
# Criar app/config.py
nano app/config.py
# Cole o conteúdo do artifact "env_config"
```

#### 2. Erro: "API key not configured"

**Causa:** .env não tem API keys válidas

**Solução:**
```bash
# Editar .env
nano .env

# Remover "sk-your" e colocar chave real
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
```

#### 3. Task fica em "running" indefinidamente

**Causa:** Erro durante execução do agent

**Solução:**
```bash
# Ver logs detalhados
curl http://localhost:8000/tasks/{id}

# Verificar logs do servidor
# (no terminal onde rodou python3 -m app.app)
```

#### 4. "AssertionError" no load_dotenv

**Causa:** Versão antiga do código sem app/config.py

**Solução:**
```bash
# Atualizar app.py para usar config
# (use artifact "main_app" atualizado)
```

#### 5. Virtual environment não ativa

**Solução:**
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# Verificar
which python3  # Deve mostrar path do venv
```

### Diagnóstico

Execute este script de diagnóstico:

```bash
#!/bin/bash
cd ~/Documentos/agent_autonomo/agent_auto/backend

echo "=== DIAGNÓSTICO COMPLETO ==="
echo ""

echo "1. Virtual Environment:"
which python3
python3 --version
echo ""

echo "2. Dependências instaladas:"
pip list | grep -E "fastapi|uvicorn|pydantic|openai|anthropic"
echo ""

echo "3. Estrutura de arquivos:"
ls -lh .env requirements.txt 2>/dev/null
ls -lh app/config.py app/app.py 2>/dev/null
echo ""

echo "4. API Keys configuradas:"
python3 -c "
from app.config import config
print('OpenAI:', '✅' if config.OPENAI_API_KEY and not config.OPENAI_API_KEY.startswith('sk-your') else '❌')
print('Anthropic:', '✅' if config.ANTHROPIC_API_KEY and not config.ANTHROPIC_API_KEY.startswith('sk-ant-your') else '❌')
" 2>/dev/null || echo "❌ Erro ao carregar config"
echo ""

echo "5. Servidor respondendo:"
curl -s http://localhost:8000/health 2>/dev/null || echo "❌ Servidor não está rodando"
```

### Logs e Debug

#### Ativar logs detalhados

```python
# app/app.py
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### Ver logs por task

```bash
curl http://localhost:8000/tasks/{id} | jq '.logs'
```

#### Monitorar em tempo real

```bash
# Terminal 1: Servidor
python3 -m app.app

# Terminal 2: Criar task e monitorar
TASK_ID=$(curl -s -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"objective": "test"}' | jq -r '.id')

watch -n 1 "curl -s http://localhost:8000/tasks/$TASK_ID | jq '.state, .logs[-1]'"
```

---

## 🤝 Contribuindo

### Como Contribuir

1. **Fork o repositório**
2. **Crie uma branch** (`git checkout -b feature/amazing-feature`)
3. **Commit suas mudanças** (`git commit -m 'Add amazing feature'`)
4. **Push para a branch** (`git push origin feature/amazing-feature`)
5. **Abra um Pull Request**

### Guia de Estilo

#### Python (PEP 8)

```python
# Imports
from typing import Optional, List
import os

# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Functions
def process_task(task_id: str, retry: bool = False) -> Optional[TaskResult]:
    """
    Process a task with optional retry.
    
    Args:
        task_id: Unique task identifier
        retry: Whether to retry on failure
        
    Returns:
        TaskResult if successful, None otherwise
    """
    pass

# Classes
class TaskProcessor:
    """Processes tasks asynchronously"""
    
    def __init__(self, config: Config):
        self.config = config
```

#### Commits (Conventional Commits)

```
feat: adiciona suporte a Docker tools
fix: corrige memory leak no TaskService
docs: atualiza README com exemplos
test: adiciona testes de integração
refactor: simplifica planner logic
```

### Áreas para Contribuição

#### 🔴 Alta Prioridade

- [ ] Multi-step planning
- [ ] Persistência em banco de dados
- [ ] Sandbox de segurança
- [ ] Extensão VSCode

#### 🟡 Média Prioridade

- [ ] Novas tools (Docker, Kubernetes, etc)
- [ ] Testes automatizados
- [ ] UI web
- [ ] Documentação expandida

#### 🟢 Baixa Prioridade

- [ ] Otimizações de performance
- [ ] Suporte a mais LLMs
- [ ] Internacionalização
- [ ] Themes/customização

---

## 📞 Suporte

### Recursos

- **Documentação:** Este arquivo
- **Issues:** GitHub Issues
- **Discussões:** GitHub Discussions
- **Chat:** Discord (em breve)

### Reportar Bugs

Ao reportar bugs, inclua:

1. **Descrição do problema**
2. **Passos para reproduzir**
3. **Comportamento esperado vs atual**
4. **Logs relevantes** (`curl /tasks/{id}`)
5. **Ambiente** (OS, Python version, etc)

**Template:**

```markdown
## Bug Description
[Descrição clara do problema]

## Steps to Reproduce
1. Execute `curl -X POST...`
2. Observe que...

## Expected Behavior
[O que deveria acontecer]

## Actual Behavior
[O que realmente acontece]

## Logs
```
[Cole logs aqui]
```

## Environment
- OS: Ubuntu 22.04
- Python: 3.11.0
- Agent Version: 0.1.0
```

---

## 📜 Licença

MIT License - veja arquivo LICENSE para detalhes

---

## 🎓 Referências e Inspirações

### Papers

- "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et al., 2022)
- "Toolformer: Language Models Can Teach Themselves to Use Tools" (Schick et al., 2023)
- "AutoGPT: An Autonomous GPT-4 Experiment" (2023)

### Projetos Relacionados

- **LangChain** - Framework para LLM applications
- **AutoGPT** - Autonomous AI agent
- **Semantic Kernel** - Microsoft's AI orchestration
- **Amazon Q** - AWS's AI assistant (closed source)

### Diferencial

Este projeto combina:
- ✅ **Controle total** (execução local)
- ✅ **Ações reais** (não apenas sugestões)
- ✅ **API-first** (extensível e integrável)
- ✅ **Open source** (transparente e customizável)

---

## 📊 Métricas do Projeto

### Status Atual (v0.1.0)

- **Linhas de Código:** ~2,500
- **Arquivos Python:** 15
- **Endpoints API:** 6
- **Tools Implementadas:** 3 (shell, fs, git)
- **Coverage de Testes:** 0% (MVP)
- **Documentação:** 95% completa

### Objetivos v1.0

- **Coverage:** >80%
- **Performance:** <500ms por task simples
- **Tools:** >20 implementadas
- **Uptime:** >99.9%
- **Documentação:** 100%

---

## 🙏 Agradecimentos

- **OpenAI** & **Anthropic** - Por democratizar acesso a LLMs
- **FastAPI** - Framework incrível
- **Comunidade Python** - Por ferramentas excelentes
- **Você** - Por usar e contribuir! 🚀

---

**Documentação atualizada em:** Janeiro 2026  
**Versão do Agent:** 0.1.0  
**Próxima atualização:** Fevereiro 2026 (v0.2.0)

---

Para mais informações, visite:
- **GitHub:** [repositório]
- **Docs Online:** [docs.site]
- **Swagger:** http://localhost:8000/docs (quando rodando)