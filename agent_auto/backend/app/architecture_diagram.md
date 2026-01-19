# 🏗️ ARQUITETURA - Linux Code Agent

## 📊 Visão Geral

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENTE                               │
│  (cURL / Python / VSCode Extension / Web UI)                │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER (FastAPI)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ routes/tasks.py                                       │  │
│  │ • POST   /tasks          → Criar task                │  │
│  │ • GET    /tasks          → Listar tasks              │  │
│  │ • GET    /tasks/{id}     → Status da task            │  │
│  │ • POST   /tasks/{id}/cancel → Cancelar task          │  │
│  │ • GET    /tasks/stats    → Estatísticas              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ Schemas (Pydantic)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   SERVICE LAYER                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ task_service.py                                       │  │
│  │ • create_task()      → Registra task                 │  │
│  │ • get_task()         → Busca status                  │  │
│  │ • update_state()     → Atualiza estado               │  │
│  │ • complete_task()    → Finaliza com resultado        │  │
│  │ • cancel_task()      → Cancela execução              │  │
│  │ • add_step()         → Registra passo                │  │
│  │ • _add_log()         → Adiciona log                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                   In-Memory Storage (Thread-safe)            │
└────────────────────────┬────────────────────────────────────┘
                         │ Background Execution
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     CORE LAYER (Agent)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ agent.py - Orquestrador Principal                     │  │
│  │                                                        │  │
│  │  execute(objective) {                                 │  │
│  │    1. plan = planner.create_plan(objective)          │  │
│  │    2. result = executor.execute_plan(plan)           │  │
│  │    3. return result                                   │  │
│  │  }                                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│         ┌───────────────┴───────────────┐                   │
│         ▼                               ▼                    │
│  ┌──────────────┐              ┌──────────────┐            │
│  │ planner.py   │              │ executor.py  │            │
│  │              │              │              │            │
│  │ • Chama LLM  │              │ • Executa    │            │
│  │ • Decide tool│              │   tools      │            │
│  │ • Retorna    │              │ • Captura    │            │
│  │   plan       │              │   output     │            │
│  └──────────────┘              └──────────────┘            │
│         │                               │                    │
│         ▼                               ▼                    │
│  ┌────────────────────────────────────────────────────┐    │
│  │ registry.py - Registro Central de Tools            │    │
│  │ • get_tool()                                        │    │
│  │ • list_tools()                                      │    │
│  │ • register_tool()                                   │    │
│  └────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │ Tool Invocation
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    TOOLS LAYER                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  shell.py    │  │   fs.py      │  │   git.py     │     │
│  │              │  │              │  │              │     │
│  │ • run_cmd()  │  │ • read_file()│  │ • git_status │     │
│  │              │  │ • write_file │  │ • git_commit │     │
│  │              │  │ • list_dir() │  │ • git_log    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬────────────────────────────────────┘
                         │ System Calls
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  OPERATING SYSTEM                            │
│              (Filesystem, Shell, Git)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Fluxo de Execução Completo

### 1️⃣ Usuário cria task

```
POST /tasks
{
  "objective": "Criar arquivo README.md",
  "context": {"project": "my-app"}
}
```

### 2️⃣ API Layer

```python
# routes/tasks.py
async def create_task(task_data):
    # Valida via Pydantic
    task_status = task_service.create_task(task_data)
    
    # Agenda execução em background
    background_tasks.add_task(execute_task, task_status.id)
    
    # Retorna imediatamente
    return task_status  # state: "pending"
```

### 3️⃣ Service Layer

```python
# task_service.py
def create_task(task_data):
    task_id = uuid4()
    task_status = TaskStatus(
        id=task_id,
        state="pending",
        objective=task_data.objective,
        logs=[]
    )
    self._tasks[task_id] = task_status
    return task_status
```

### 4️⃣ Background Execution

```python
async def execute_task_background(task_id):
    # Marcar como running
    task_service.update_state(task_id, "running")
    
    # Executar via agent
    result = agent.execute(objective)
    
    # Salvar resultado
    task_service.complete_task(task_id, result)
```

### 5️⃣ Core Layer - Agent

```python
# agent.py
def execute(objective):
    # Planejar
    plan = planner.create_plan(objective)
    
    # Executar cada ação
    for action in plan.actions:
        result = executor.execute_action(action)
    
    return TaskResult(success=True, output=...)
```

### 6️⃣ Planner (LLM)

```python
# planner.py
def create_plan(objective):
    prompt = f"""
    Objetivo: {objective}
    Tools: {registry.list_tools()}
    
    Retorne JSON com ações necessárias.
    """
    
    response = llm.complete(prompt)
    return parse_plan(response)
```

### 7️⃣ Executor

```python
# executor.py
def execute_action(action):
    tool = registry.get_tool(action.tool)
    result = tool(**action.params)
    return result
```

### 8️⃣ Tools

```python
# fs.py
def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)
    return f"Arquivo {path} criado"
```

### 9️⃣ Usuário consulta status

```
GET /tasks/{id}
{
  "id": "...",
  "state": "completed",
  "logs": [...],
  "result": {
    "success": true,
    "output": "README.md criado"
  }
}
```

---

## 🧩 Responsabilidades das Camadas

### API Layer (`routes/`)
- ✅ Receber HTTP requests
- ✅ Validar entrada via Pydantic
- ✅ Chamar services
- ✅ Retornar HTTP responses
- ❌ **NÃO** contém lógica de negócio

### Service Layer (`services/`)
- ✅ Gerenciar estado das tasks
- ✅ Controlar ciclo de vida
- ✅ Armazenar logs e resultados
- ✅ Fornecer API interna
- ❌ **NÃO** executa ações

### Core Layer (`core/`)
- ✅ Orquestrar execução
- ✅ Planejar ações via LLM
- ✅ Executar plan
- ✅ Decidir próximos passos
- ❌ **NÃO** conhece HTTP

### Tools Layer (`tools/`)
- ✅ Executar ações reais
- ✅ Interagir com OS
- ✅ Retornar resultados
- ✅ Ser extensível
- ❌ **NÃO** decide quando executar

---

## 🔐 Segurança & Controle

### Atual
- ✅ Execução local (sem upload)
- ✅ API Keys via `.env`
- ✅ Thread-safe storage
- ✅ Estado isolado por task

### Planejado
- 🔜 Allowlist de comandos
- 🔜 Sandbox de execução
- 🔜 Confirmação de ações destrutivas
- 🔜 Rate limiting
- 🔜 Audit logs persistentes

---

## 📈 Escalabilidade

### Atual (MVP)
- In-memory storage
- Single process
- Suporta: desenvolvimento local

### Futuro
- PostgreSQL/SQLite para persistência
- Celery para workers distribuídos
- Redis para queue
- Suporta: produção enterprise

---

## 🆚 Comparação com Concorrentes

| Feature              | Amazon Q | Copilot | **Nosso Agent** |
|----------------------|----------|---------|-----------------|
| **Execução Local**   | ❌       | ❌       | ✅              |
| **Ações Reais**      | ⚠️ Cloud | ❌       | ✅              |
| **Planning**         | ✅       | ❌       | ✅              |
| **Extensível**       | ❌       | ❌       | ✅              |
| **Open Source**      | ❌       | ❌       | ✅              |
| **API First**        | ❌       | ❌       | ✅              |
| **Auditável**        | ⚠️       | ❌       | ✅              |
| **Controle Total**   | ❌       | ❌       | ✅              |

**Diferencial**: Somos o único que combina **autonomia + controle + local**.

---

## ✅ Status Atual

🟢 **Implementado**
- API completa (CRUD tasks)
- Service com estado
- Agent com planner + executor
- 3 tools funcionais
- Background execution
- Logs e status em tempo real

🟡 **Em desenvolvimento**
- Multi-step planning
- Loop observe → act → refine
- Error recovery inteligente

🔴 **Planejado**
- Persistência (DB)
- UI web
- VSCode extension
- Distribuição (pip/binary)

---

## 🎯 Próximo Milestone

**Objetivo**: Agent totalmente autônomo

**Tasks**:
1. ✅ Core funcional (CONCLUÍDO)
2. 🔜 Loop de refinamento
3. 🔜 Multi-step planning
4. 🔜 Self-correction
5. 🔜 Tool chaining

**Meta**: Agent que executa tarefas complexas sem intervenção humana.

---

**Arquitetura enterprise, pronta para escalar! 🚀**
