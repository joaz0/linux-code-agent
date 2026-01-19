# 🤖 Linux Code Agent

<div align="center">

**O futuro do desenvolvimento de software está aqui.**

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://github.com/yourusername/linux-code-agent)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-cyan.svg)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[**Documentação**](docs/DOCUMENTATION.md) • [**API Reference**](docs/API_REFERENCE.md) • [**Exemplos**](docs/EXAMPLES.md) • [**Roadmap**](#-roadmap)

---

### Um agente de IA que não apenas **sugere** código, mas **executa ações reais** no seu sistema.

**Pense em Amazon Q + GitHub Copilot, mas:**
- ✅ **100% Local** - Seu código nunca sai da sua máquina
- ✅ **Ações Reais** - Cria arquivos, executa comandos, faz commits
- ✅ **Planning Inteligente** - LLM decide a melhor estratégia
- ✅ **API First** - Integre com qualquer ferramenta
- ✅ **Open Source** - Controle total, sem vendor lock-in

</div>

---

## 🎬 Demo Rápida

```bash
# Instalar
git clone https://github.com/yourusername/linux-code-agent.git
cd linux-code-agent/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configurar API key
echo "ANTHROPIC_API_KEY=sk-ant-sua-chave" > .env

# Rodar
python3 -m app.app
```

```python
# Usar
import requests

# Criar task
response = requests.post("http://localhost:8000/tasks", json={
    "objective": "Criar API REST para gerenciar produtos com CRUD completo"
})

task_id = response.json()["id"]

# Aguardar 30 segundos...
# O agent vai: planejar → criar arquivos → escrever código → testar

result = requests.get(f"http://localhost:8000/tasks/{task_id}")
print(result.json()["result"]["output"])
# >>> "✅ API criada com sucesso! Arquivos: models/product.py, routes/products.py, tests/test_products.py"
```

**[📹 Ver demo em vídeo](#)** • **[🚀 Experimentar online](#)**

---

## 🌟 Por Que Linux Code Agent?

### O Problema

Ferramentas atuais de IA para código são limitadas:

| Ferramenta | Problema |
|------------|----------|
| **GitHub Copilot** | Apenas sugere código, você precisa executar manualmente |
| **Amazon Q** | Cloud-only, seu código vai para servidores da AWS |
| **Cursor** | Limitado ao editor, não executa ações do sistema |
| **ChatGPT Code Interpreter** | Sandbox restrito, não acessa seu projeto real |

### Nossa Solução

**Linux Code Agent** é um **verdadeiro agente autônomo**:

```
Você: "Refatore este módulo para usar async/await"
       ↓
Agent: 🧠 Analisa o código
       🎯 Decide estratégia (planner)
       🔧 Executa ferramentas (executor)
       ✅ Retorna resultado
       
Resultado: Código refatorado + testes atualizados + git commit
```

---

## ✨ Features

### 🎯 Atual (v0.1.0)

#### Core Funcional
- [x] **Planning via LLM** - GPT-4 ou Claude decidem as ações
- [x] **Execução Real** - Shell, filesystem, git operations
- [x] **API REST Completa** - FastAPI com OpenAPI/Swagger
- [x] **Background Tasks** - Execução assíncrona
- [x] **Status em Tempo Real** - Logs e progresso
- [x] **Cancelamento** - Interrompa tasks em execução

#### Tools Disponíveis
- [x] **Shell** - Execute comandos bash
- [x] **FileSystem** - Crie, edite, delete arquivos
- [x] **Git** - Status, commit, log, diff

#### Arquitetura
- [x] **Modular** - Camadas bem definidas (API → Service → Core → Tools)
- [x] **Thread-Safe** - Gerenciamento seguro de estado
- [x] **Extensível** - Adicione novas tools facilmente
- [x] **Documentado** - OpenAPI automático + docs completas

### 🔮 Futuro Próximo (v0.2.0 - Fevereiro 2026)

#### Multi-Agent System 🚀 **NOVO!**

O agente atual é apenas o **começo**. Estamos construindo um **sistema multi-agente** onde agentes especializados colaboram:

```
Você: "Criar aplicação web completa com backend e frontend"
       ↓
┌─────────────────────────────────────────────────────┐
│         ORCHESTRATOR AGENT (Coordenador)            │
│  Analisa tarefa e distribui para agentes especializados │
└──────────────┬──────────────────────────────────────┘
               │
      ┌────────┴────────┬──────────┬──────────┐
      ▼                 ▼          ▼          ▼
┌──────────┐   ┌──────────┐  ┌──────────┐  ┌──────────┐
│ BACKEND  │   │ FRONTEND │  │  DEVOPS  │  │    QA    │
│  AGENT   │   │  AGENT   │  │  AGENT   │  │  AGENT   │
└──────────┘   └──────────┘  └──────────┘  └──────────┘
     │              │             │             │
     ├─ FastAPI    ├─ React     ├─ Docker    ├─ Testes
     ├─ SQLAlchemy ├─ Tailwind  ├─ CI/CD     ├─ Coverage
     └─ Endpoints  └─ Componentes└─ Deploy   └─ E2E

Cada agente tem:
- 🎯 Especialização própria
- 🧠 Modelo fine-tuned para seu domínio
- 🔧 Ferramentas específicas
- 💬 Comunicação via protocolo interno
```

**Agentes Planejados:**

| Agente | Especialidade | Status |
|--------|---------------|--------|
| 🎼 **Orchestrator** | Coordena outros agentes, divide tarefas complexas | 🔜 v0.2.0 |
| ⚙️ **Backend Agent** | APIs REST/GraphQL, databases, microservices | 🔜 v0.2.0 |
| 🎨 **Frontend Agent** | React, Vue, Angular, UI/UX | 🔜 v0.3.0 |
| 🔧 **DevOps Agent** | Docker, K8s, CI/CD, monitoring | 🔜 v0.3.0 |
| ✅ **QA Agent** | Testes (unit, integration, E2E), coverage | 🔜 v0.3.0 |
| 📊 **Data Agent** | ETL, ML pipelines, analytics | 🔜 v0.4.0 |
| 🔐 **Security Agent** | Vulnerability scanning, SAST, secrets detection | 🔜 v0.4.0 |
| 📱 **Mobile Agent** | React Native, Flutter, Swift, Kotlin | 🔜 v0.5.0 |
| 🤖 **AI/ML Agent** | Model training, fine-tuning, deployment | 🔜 v0.5.0 |

**Exemplo de Colaboração:**

```python
# Você cria uma task complexa
task = create_task("""
Criar e-commerce completo:
- Backend: API REST com autenticação JWT
- Frontend: Dashboard admin + Loja
- DevOps: Docker + CI/CD
- QA: Testes automatizados
""")

# Internamente, o Orchestrator divide:
orchestrator.delegate([
    {"agent": "backend", "task": "API REST com JWT"},
    {"agent": "frontend", "task": "Dashboard + Loja"},
    {"agent": "devops", "task": "Docker + CI/CD"},
    {"agent": "qa", "task": "Testes E2E"}
])

# Agentes trabalham em paralelo e se comunicam:
backend_agent → "API pronta na porta 8000"
frontend_agent → "OK, configurando proxy para :8000"
devops_agent → "Criando docker-compose com ambos"
qa_agent → "Testando integração frontend ↔ backend"

# Resultado final: Aplicação completa funcionando! 🎉
```

#### Outras Features v0.2.0

- [ ] **Multi-Step Planning** - Tarefas complexas em múltiplos passos
- [ ] **Self-Correction** - Agent corrige seus próprios erros
- [ ] **Memory Persistente** - SQLite para histórico
- [ ] **Context Awareness** - Entende estrutura do projeto
- [ ] **Novas Tools** - Docker, Kubernetes, npm/pip, etc

### 🚀 Roadmap Completo

#### v0.3.0 - Produção (Março 2026)
- [ ] **Workers Distribuídos** - Celery + Redis
- [ ] **Autenticação** - JWT + RBAC
- [ ] **Sandbox Execution** - Containers isolados
- [ ] **Monitoring** - Prometheus + Grafana
- [ ] **Rate Limiting** - Proteção contra abuso

#### v0.4.0 - Interfaces (Abril 2026)
- [ ] **VSCode Extension** - Integração nativa
- [ ] **Web UI** - Dashboard React
- [ ] **CLI Tool** - `code-agent run "criar API"`
- [ ] **Slack/Discord Bot** - Controle via chat

#### v1.0.0 - AI Superpowers (Q3 2026)
- [ ] **Multi-Agent Orchestration** - Sistema completo de agentes especializados
- [ ] **Fine-Tuned Models** - Modelos customizados por projeto
- [ ] **Proactive Suggestions** - Agent sugere melhorias
- [ ] **Plugin Marketplace** - Comunidade de tools
- [ ] **Cloud Offering** - Managed hosting opcional

---

## 🏗️ Arquitetura

### Visão Geral

```
┌─────────────────────────────────────────────┐
│  CLIENTE (cURL, Python, VSCode, Web UI)     │
└──────────────────┬──────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────┐
│  API LAYER (FastAPI)                        │
│  • Routes  • Validation  • OpenAPI          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  SERVICE LAYER                              │
│  • TaskService (estado, lifecycle)          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  CORE LAYER (Agent)                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ Planner │→ │Executor │→ │Registry │    │
│  │  (LLM)  │  │ (Runner)│  │ (Tools) │    │
│  └─────────┘  └─────────┘  └─────────┘    │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  TOOLS LAYER                                │
│  🐚 Shell  📁 FileSystem  🔀 Git  🐳 Docker│
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  OPERATING SYSTEM                           │
└─────────────────────────────────────────────┘
```

### Fluxo de Execução

```python
# 1. Usuário cria task via API
POST /tasks {"objective": "Criar README.md"}

# 2. TaskService registra (state: pending)
task_id = "550e8400-..."

# 3. Background worker pega task
# 4. Agent.execute() orquestra:

Agent
  ↓
Planner (LLM)
  → Analisa objetivo
  → Decide: usar tool "write_file"
  → Retorna plano JSON
  ↓
Executor
  → Busca tool no Registry
  → Executa: write_file("README.md", "# Projeto...")
  → Captura resultado
  ↓
TaskService
  → Atualiza state: completed
  → Salva resultado
  ↓
# 5. Usuário consulta resultado
GET /tasks/550e8400-...
```

**[📖 Arquitetura Detalhada](docs/DOCUMENTATION.md#-arquitetura)**

---

## 🚀 Quick Start

### Pré-requisitos

- Python 3.10+
- API Key (OpenAI **ou** Anthropic)
- Git

### Instalação (5 minutos)

```bash
# 1. Clone
git clone https://github.com/yourusername/linux-code-agent.git
cd linux-code-agent/backend

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Dependências
pip install -r requirements.txt

# 4. Configuração
cat > .env << EOF
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-20250514
EOF

# 5. Iniciar
python3 -m app.app
```

**Servidor rodando em:** http://localhost:8000

**Docs interativas:** http://localhost:8000/docs

### Primeiro Teste

```bash
# Criar uma task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Listar todos os arquivos Python no diretório atual"
  }'

# Resposta
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "state": "pending",
  ...
}

# Aguardar alguns segundos, depois consultar
curl http://localhost:8000/tasks/550e8400-e29b-41d4-a716-446655440000

# Resultado
{
  "state": "completed",
  "result": {
    "success": true,
    "output": "app.py\nconfig.py\n..."
  }
}
```

**[📚 Guia Completo de Instalação](docs/DOCUMENTATION.md#-instalação)**

---

## 📖 Documentação

### 📘 Guias Principais

| Documento | Descrição |
|-----------|-----------|
| [**DOCUMENTATION.md**](docs/DOCUMENTATION.md) | Documentação completa (arquitetura, uso, desenvolvimento) |
| [**API_REFERENCE.md**](docs/API_REFERENCE.md) | Referência da API REST (endpoints, schemas, exemplos) |
| [**DEPLOYMENT.md**](docs/DEPLOYMENT.md) | Deploy em produção (Linux, Docker, Kubernetes, Cloud) |
| [**EXAMPLES.md**](docs/EXAMPLES.md) | Casos de uso práticos e código de exemplo |

### 🎓 Tutoriais

- [Como adicionar uma nova tool](docs/DEVELOPMENT.md#adicionar-tool)
- [Integração com VSCode](docs/EXAMPLES.md#vscode-extension)
- [Deploy em produção](docs/DEPLOYMENT.md#produção-checklist)
- [Configurar multi-step planning](docs/DOCUMENTATION.md#multi-step) *(em breve)*

### 🔗 Links Rápidos

- **Swagger UI:** http://localhost:8000/docs (quando rodando)
- **Health Check:** http://localhost:8000/health
- **Métricas:** http://localhost:8000/metrics *(futuro)*

---

## 💡 Exemplos de Uso

### 1. Criar Estrutura de Projeto

```python
import requests

response = requests.post("http://localhost:8000/tasks", json={
    "objective": """
    Criar estrutura de projeto FastAPI:
    - app/ com __init__, main, routers, models
    - tests/ com conftest e test_main
    - .env.example
    - requirements.txt
    - README.md
    - .gitignore
    Inicializar git e fazer primeiro commit
    """
})

print(f"Projeto sendo criado... {response.json()['id']}")
```

### 2. Refatorar Código

```python
response = requests.post("http://localhost:8000/tasks", json={
    "objective": "Refatorar app/services/user.py para usar async/await",
    "context": {
        "file": "app/services/user.py",
        "maintain_tests": True
    }
})
```

### 3. Setup DevOps

```python
response = requests.post("http://localhost:8000/tasks", json={
    "objective": """
    Configurar CI/CD completo:
    - GitHub Actions para testes
    - Dockerfile multi-stage
    - docker-compose.yml com app + postgres + redis
    - Makefile com comandos úteis
    """
})
```

### 4. Gerar Testes

```python
response = requests.post("http://localhost:8000/tasks", json={
    "objective": "Gerar testes unitários para app/core/agent.py com 90% coverage"
})
```

**[📚 Mais 15+ exemplos completos](docs/EXAMPLES.md)**

---

## 🆚 Comparação

### vs GitHub Copilot

| Feature | Copilot | Linux Code Agent |
|---------|---------|------------------|
| Sugestões de código | ✅ Excelente | ✅ Via LLM |
| Execução de ações | ❌ Não | ✅ **Sim** |
| Criação de arquivos | ❌ Manual | ✅ Automático |
| Git operations | ❌ Não | ✅ Sim |
| API disponível | ❌ Não | ✅ REST completa |
| Local-first | ✅ Sim | ✅ Sim |
| Open source | ❌ Não | ✅ Sim |

### vs Amazon Q

| Feature | Amazon Q | Linux Code Agent |
|---------|----------|------------------|
| Planning inteligente | ✅ Sim | ✅ Sim |
| Execução de ações | ⚠️ Cloud only | ✅ **Local** |
| Controle total | ❌ AWS-locked | ✅ **Total** |
| Custo | 💰 $20/mês | ✅ **Free** (só API LLM) |
| Vendor lock-in | ❌ Sim | ✅ **Não** |
| Extensível | ❌ Não | ✅ **Sim** |

### vs Cursor

| Feature | Cursor | Linux Code Agent |
|---------|--------|------------------|
| Editor integrado | ✅ IDE próprio | 🔜 VSCode extension |
| Multi-file editing | ✅ Sim | ✅ Sim |
| Sistema completo | ⚠️ Limitado | ✅ **Shell, git, etc** |
| API externa | ❌ Não | ✅ **REST API** |
| Customização | ⚠️ Limitada | ✅ **Total** |

### Nosso Diferencial

🎯 **Somos o único que combina:**
- ✅ Autonomia (planning + execução)
- ✅ Controle total (100% local)
- ✅ Extensibilidade (API + tools customizáveis)
- ✅ Open source (código aberto, sem lock-in)

---

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
backend/
├── app/
│   ├── api/          # Endpoints HTTP
│   ├── core/         # Agent, Planner, Executor
│   ├── tools/        # Shell, FS, Git
│   ├── services/     # TaskService
│   ├── schemas/      # Pydantic models
│   └── config.py     # Configuração
│
├── tests/            # Testes
├── docs/             # Documentação
├── .env              # Config local
└── requirements.txt  # Dependências
```

### Adicionar uma Tool

```python
# 1. Criar app/tools/docker.py
def docker_ps(all: bool = False) -> str:
    """List docker containers"""
    import subprocess
    cmd = ["docker", "ps"]
    if all:
        cmd.append("-a")
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

# 2. Registrar em app/core/registry.py
from app.tools import docker

TOOLS = {
    # ... existing
    "docker_ps": docker.docker_ps,
}

# 3. Usar!
requests.post("/tasks", json={
    "objective": "Listar containers docker"
})
```

### Executar Testes

```bash
# Testes de integração
python test_integration.py

# Testes unitários (futuro)
pytest tests/ -v

# Coverage
pytest --cov=app tests/
```

### Contribuir

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/amazing`)
3. Commit (`git commit -m 'feat: add amazing feature'`)
4. Push (`git push origin feature/amazing`)
5. Abra um Pull Request

**[📖 Guia de Contribuição Completo](CONTRIBUTING.md)**

---

## 🔐 Segurança

### ✅ Implementado

- **Execução local** - Código nunca sai do ambiente
- **API keys locais** - Armazenadas em .env
- **Thread-safe** - Gerenciamento seguro de estado
- **Validação de entrada** - Pydantic schemas

### 🔜 Planejado

- **Sandbox de execução** - Containers isolados (v0.3.0)
- **Allowlist de comandos** - Restringir ações perigosas (v0.2.0)
- **Audit logs** - Rastreabilidade completa (v0.3.0)
- **Read-only mode** - Agent só lê, não modifica (v0.2.0)

### ⚠️ Disclaimer

Este é um agente **autônomo** que executa ações reais no seu sistema. Use com responsabilidade:

- ✅ Teste primeiro em ambiente isolado
- ✅ Revise código gerado antes de usar em produção
- ✅ Faça backup antes de operações destrutivas
- ✅ Use API keys com permissões mínimas

---

## 📊 Status do Projeto

### Métricas

- **Versão:** 0.1.0 (MVP Funcional)
- **Linhas de Código:** ~2,500
- **Arquivos Python:** 15
- **Tools Disponíveis:** 3 (shell, fs, git)
- **Endpoints API:** 6
- **Coverage:** 0% (MVP - testes em v0.2.0)
- **Documentação:** 95% completa

### Atividade

![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/linux-code-agent)
![GitHub issues](https://img.shields.io/github/issues/yourusername/linux-code-agent)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/linux-code-agent)
![GitHub stars](https://img.shields.io/github/stars/yourusername/linux-code-agent?style=social)

---

## 🤝 Comunidade

### Junte-se a nós!

- **GitHub Discussions:** [Fórum da comunidade](#)
- **Discord:** [Chat em tempo real](#) *(em breve)*
- **Twitter:** [@LinuxCodeAgent](#) *(em breve)*

### Contribuidores

<a href="https://github.com/yourusername/linux-code-agent/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=yourusername/linux-code-agent" />
</a>

Feito com [contrib.rocks](https://contrib.rocks).

### Agradecimentos

- **OpenAI & Anthropic** - Por democratizar LLMs
- **FastAPI** - Framework incrível
- **Comunidade Python** - Ferramentas excelentes
- **Você** - Por usar e contribuir! 🙏

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

Isso significa que você pode:
- ✅ Usar comercialmente
- ✅ Modificar livremente
- ✅ Distribuir
- ✅ Usar em projetos privados

**Único requisito:** Manter o aviso de copyright.

---

## 🗺️ Roadmap Detalhado

### Q1 2026 (Jan-Mar)

- [x] **v0.1.0** - MVP Funcional *(Janeiro)*
  - Core agent com planning
  - API REST completa
  - Tools básicas

- [ ] **v0.2.0** - Autonomia Avançada *(Fevereiro)*
  - Multi-step planning
  - Multi-agent orchestration (Orchestrator + Backend Agent)
  - Self-correction
  - Memory persistente

- [ ] **v0.3.0** - Produção *(Março)*
  - Frontend Agent + DevOps Agent
  - Workers distribuídos
  - Autenticação + RBAC
  - Sandbox execution

### Q2 2026 (Abr-Jun)

- [ ] **v0.4.0** - Interfaces *(Abril)*
  - QA Agent
  - VSCode extension
  - Web UI (React)
  - CLI tool

- [ ] **v0.5.0** - Expansão *(Maio)*
  - Data Agent + Security Agent
  - Mobile Agent
  - Plugin marketplace
  - Fine-tuned models

- [ ] **v0.6.0** - Enterprise *(Junho)*
  - Multi-tenancy
  - SSO integration
  - Advanced monitoring
  - SLA guarantees

### Q3 2026 (Jul-Set)

- [ ] **v1.0.0** - AI Superpowers *(Q3)*
  - Sistema completo de 9 agentes especializados
  - Multi-agent collaboration protocol
  - Proactive suggestions
  - Cloud offering (managed)
  - AI/ML Agent para fine-tuning

---

## 🎯 Visão de Futuro

### 2026: **O Ano do Agente Autônomo**

Imaginamos um futuro onde:

> "Você tem uma ideia → Descreve para o agent → Aplicação pronta em minutos"

**Exemplo:** *Sistema de e-commerce completo*

```
Você → "Criar e-commerce com pagamentos, admin dashboard e app mobile"
        ↓
Multi-Agent System trabalha em paralelo:
  
  Backend Agent     → API REST + PostgreSQL + Stripe
  Frontend Agent    → React dashboard + Landing page
  Mobile Agent      → React Native app (iOS + Android)
  DevOps Agent      → Docker + Kubernetes + CI/CD
  QA Agent          → Testes E2E + Load tests
  Security Agent    → OWASP compliance + Secrets scan
        ↓
30 minutos depois:
  ✅ 15 microservices
  ✅ 3 frontends (web admin, web loja, mobile)
  ✅ 200+ testes automatizados
  ✅ Deploy completo em produção
  ✅ Monitoramento configurado
```

### 2027+: **AGI para Desenvolvimento**

- **Agentes que aprendem** com seu estilo de código
- **Colaboração humano-IA** em tempo real
- **Manutenção proativa** - Agent detecta e corrige bugs antes de aparecerem
- **Auto-otimização** - Performance melhorando continuamente

**Queremos chegar em um ponto onde:**
- 90% do código repetitivo é gerado
- Desenvolvedores focam em arquitetura e regras de negócio
- Deploy de produção em < 1 hora para qualquer aplicação
- Zero bugs em produção (agent testa tudo antes)

---

## 📞 Suporte

### Precisa de ajuda?

- **📖 Documentação:** [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)
- **🐛 Bug reports:** [GitHub Issues](https://github.com/yourusername/linux-code-agent/issues)
- **💬 Discussões:** [GitHub Discussions](https://github.com/yourusername/linux-code-agent/discussions)
- **📧 Email:** support@linuxcodeagent.dev *(em breve)*

### FAQ

**P: É grátis?**
R: Sim! Open source com licença MIT. Você só paga pelas chamadas à API do LLM (OpenAI/Anthropic).

**P: Funciona offline?**
R: Não completamente - precisa de internet para o LLM. Mas estamos trabalhando em suporte a modelos locais (Llama, Mistral).

**P: É seguro?**
R: Tudo roda localmente, seu código nunca sai da máquina. Mas sempre revise código gerado antes de usar em produção.

**P: Posso usar em projetos comerciais?**
R: Sim! Licença MIT permite uso comercial sem restrições.

**P: Como contribuir?**
R: Veja [CONTRIBUTING.md](CONTRIBUTING.md). PRs são muito bem-vindos!

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/linux-code-agent&type=Date)](https://star-history.com/#yourusername/linux-code-agent&Date)

---

## 🚀 Call to Action

### Experimente Agora!

```bash
# 3 comandos e você está rodando
git clone https://github.com/yourusername/linux-code-agent.git
cd linux-code-agent/backend && pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=sua-key" > .env && python3 -m app.app
```

### Contribua!

- ⭐ **Star** este repo se você acha útil
- 🐛 **Reporte bugs** via Issues
- 💡 **Sugira features** via Discussions
- 🔧 **Contribua código** via Pull Requests
- 📢 **Compartilhe** com sua rede

### Próximos Passos

1. **[📖 Leia a documentação completa](docs/DOCUMENTATION.md)**
2. **[🚀 Siga o Quick Start](#-quick-start)**
3. **[💡 Veja exemplos práticos](docs/EXAMPLES.md)**
4. **[🤝 Junte-se à comunidade](#-comunidade)**

---

<div align="center">

**Construído com ❤️ para desenvolvedores que querem automatizar tudo**

**[⬆ Voltar ao topo](#-linux-code-agent)**

---

*"O melhor código é aquele que você não precisa escrever." - Linux Code Agent*

</div>