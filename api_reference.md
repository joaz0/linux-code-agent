# 🌐 API Reference - Linux Code Agent

**Base URL:** `http://localhost:8000`  
**Version:** v1 (implícito)  
**Content-Type:** `application/json`

---

## 📋 Índice

1. [Autenticação](#autenticação)
2. [Endpoints](#endpoints)
3. [Schemas](#schemas)
4. [Códigos de Status](#códigos-de-status)
5. [Rate Limiting](#rate-limiting)
6. [Exemplos](#exemplos)

---

## 🔐 Autenticação

**Atual:** Nenhuma (execução local)

**Futuro (v0.3.0):**
```http
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
```

---

## 🎯 Endpoints

### Health & Status

#### `GET /`

Root endpoint com informações básicas.

**Response:**
```json
{
  "status": "online",
  "service": "Linux Code Agent",
  "version": "0.1.0",
  "docs": "/docs"
}
```

---

#### `GET /health`

Health check detalhado com estatísticas.

**Response:**
```json
{
  "status": "healthy",
  "tasks": {
    "total": 42,
    "pending": 3,
    "running": 2,
    "completed": 35,
    "failed": 2,
    "cancelled": 0
  }
}
```

**Status Codes:**
- `200` - Sistema saudável
- `503` - Sistema com problemas (futuro)

---

### Tasks

#### `POST /tasks`

Cria uma nova task para o agente executar.

**Request Body:**
```json
{
  "objective": "string (3-1000 chars)",
  "context": {
    // objeto opcional com contexto adicional
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "objective": "string",
  "context": {...},
  "state": "pending",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T10:00:00Z",
  "logs": [
    {
      "timestamp": "2026-01-18T10:00:00Z",
      "message": "Task criada: <objective>"
    }
  ],
  "steps": [],
  "result": null
}
```

**Validation Errors:** `422 Unprocessable Entity`
```json
{
  "detail": [
    {
      "loc": ["body", "objective"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "objective": "Criar arquivo README.md com documentação do projeto",
    "context": {
      "project_name": "my-app",
      "language": "python"
    }
  }'
```

---

#### `GET /tasks`

Lista tasks com filtros opcionais.

**Query Parameters:**
| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `state` | string | No | null | Filtrar por estado (pending, running, completed, failed, cancelled) |
| `limit` | integer | No | 50 | Máximo de tasks a retornar (1-100) |

**Response:** `200 OK`
```json
{
  "tasks": [
    {
      "id": "uuid",
      "objective": "string",
      "state": "completed",
      "created_at": "...",
      "updated_at": "...",
      // ... campos completos de TaskStatus
    }
  ],
  "total": 42
}
```

**Exemplos:**
```bash
# Todas as tasks (max 50)
curl http://localhost:8000/tasks

# Apenas completadas
curl http://localhost:8000/tasks?state=completed

# Últimas 10
curl http://localhost:8000/tasks?limit=10

# Completadas, últimas 5
curl "http://localhost:8000/tasks?state=completed&limit=5"
```

---

#### `GET /tasks/stats`

Estatísticas agregadas das tasks.

**Response:** `200 OK`
```json
{
  "total": 100,
  "pending": 5,
  "running": 2,
  "completed": 85,
  "failed": 6,
  "cancelled": 2
}
```

**Exemplo:**
```bash
curl http://localhost:8000/tasks/stats
```

---

#### `GET /tasks/{task_id}`

Busca uma task específica por ID.

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `task_id` | string (uuid) | ID único da task |

**Response:** `200 OK`
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "objective": "Criar arquivo test.txt",
  "context": null,
  "state": "completed",
  "created_at": "2026-01-18T10:00:00Z",
  "updated_at": "2026-01-18T10:00:15Z",
  "logs": [
    {
      "timestamp": "2026-01-18T10:00:00Z",
      "message": "Task criada"
    },
    {
      "timestamp": "2026-01-18T10:00:05Z",
      "message": "Iniciando execução..."
    },
    {
      "timestamp": "2026-01-18T10:00:15Z",
      "message": "Task finalizada com sucesso"
    }
  ],
  "steps": [
    {
      "timestamp": "2026-01-18T10:00:10Z",
      "description": "write_file: test.txt"
    }
  ],
  "result": {
    "success": true,
    "output": "Arquivo test.txt criado com sucesso",
    "error": null,
    "actions_taken": [
      {
        "tool": "write_file",
        "params": {
          "path": "test.txt",
          "content": "Hello World"
        },
        "result": "File written successfully"
      }
    ]
  }
}
```

**Errors:**
- `404 Not Found` - Task não existe

```json
{
  "detail": "Task 550e8400-... não encontrada"
}
```

**Exemplo:**
```bash
curl http://localhost:8000/tasks/550e8400-e29b-41d4-a716-446655440000
```

---

#### `POST /tasks/{task_id}/cancel`

Cancela uma task em execução ou pendente.

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `task_id` | string (uuid) | ID da task a cancelar |

**Response:** `200 OK`
```json
{
  "id": "550e8400-...",
  "state": "cancelled",
  "updated_at": "2026-01-18T10:05:00Z",
  "logs": [
    // ... logs anteriores
    {
      "timestamp": "2026-01-18T10:05:00Z",
      "message": "Task cancelada pelo usuário"
    }
  ]
}
```

**Errors:**

`404 Not Found` - Task não existe
```json
{
  "detail": "Task 550e8400-... não encontrada"
}
```

`400 Bad Request` - Task não pode ser cancelada
```json
{
  "detail": "Task 550e8400-... não pode ser cancelada (estado atual: completed)"
}
```

**Notas:**
- Apenas tasks `pending` ou `running` podem ser canceladas
- Tasks `completed`, `failed` ou `cancelled` não podem ser canceladas

**Exemplo:**
```bash
curl -X POST http://localhost:8000/tasks/550e8400-.../cancel
```

---

#### `DELETE /tasks/{task_id}`

Deleta uma task do histórico.

**Status:** `501 Not Implemented` (futuro)

**Planejado para v0.2.0:**
```bash
curl -X DELETE http://localhost:8000/tasks/550e8400-...
```

---

## 📦 Schemas

### TaskBase (Input)

```typescript
{
  objective: string;      // 3-1000 chars
  context?: object;       // qualquer estrutura JSON
}
```

**Exemplos válidos:**
```json
{
  "objective": "Criar teste",
  "context": null
}

{
  "objective": "Analisar código",
  "context": {
    "file": "main.py",
    "line": 42
  }
}
```

**Validações:**
- `objective` é obrigatório
- `objective` deve ter 3-1000 caracteres
- `context` é opcional

---

### TaskStatus (Output)

```typescript
{
  id: string;                    // UUID v4
  objective: string;
  context?: object;
  state: "pending" | "running" | "completed" | "failed" | "cancelled";
  created_at: string;            // ISO 8601 datetime
  updated_at: string;            // ISO 8601 datetime
  logs: Array<{
    timestamp: string;           // ISO 8601
    message: string;
  }>;
  steps: Array<{
    timestamp: string;           // ISO 8601
    description: string;
  }>;
  result?: TaskResult;           // null se ainda não completou
}
```

---

### TaskResult

```typescript
{
  success: boolean;
  output: string;
  error?: string;                // null se success=true
  actions_taken: Array<{
    tool: string;
    params: object;
    result: string;
  }>;
}
```

---

### TaskState (Enum)

```typescript
enum TaskState {
  PENDING = "pending",         // Aguardando execução
  RUNNING = "running",         // Em execução
  COMPLETED = "completed",     // Completada com sucesso
  FAILED = "failed",          // Falhou durante execução
  CANCELLED = "cancelled"      // Cancelada pelo usuário
}
```

**Transições válidas:**
```
PENDING → RUNNING
PENDING → CANCELLED

RUNNING → COMPLETED
RUNNING → FAILED
RUNNING → CANCELLED

COMPLETED → (final)
FAILED → (final)
CANCELLED → (final)
```

---

## 🔢 Códigos de Status HTTP

| Code | Significado | Quando ocorre |
|------|-------------|---------------|
| `200` | OK | Request bem sucedido |
| `201` | Created | Task criada com sucesso |
| `204` | No Content | Deleção bem sucedida (futuro) |
| `400` | Bad Request | Operação inválida (ex: cancelar task completed) |
| `404` | Not Found | Task não encontrada |
| `422` | Unprocessable Entity | Validação falhou |
| `500` | Internal Server Error | Erro no servidor |
| `501` | Not Implemented | Feature ainda não implementada |
| `503` | Service Unavailable | Sistema indisponível (futuro) |

---

## ⏱️ Rate Limiting

**Atual:** Sem limite

**Futuro (v0.3.0):**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
```

Limites planejados:
- **Requests:** 100/minuto por IP
- **Tasks concorrentes:** 5 por usuário
- **LLM calls:** 50/minuto

---

## 💡 Exemplos Avançados

### Polling de Status

```python
import requests
import time

def wait_for_task(task_id, timeout=60):
    """Aguarda task completar"""
    start = time.time()
    
    while time.time() - start < timeout:
        response = requests.get(f"http://localhost:8000/tasks/{task_id}")
        task = response.json()
        
        if task["state"] in ["completed", "failed", "cancelled"]:
            return task
        
        time.sleep(1)
    
    raise TimeoutError(f"Task {task_id} não completou em {timeout}s")

# Uso
task = create_task("Criar README")
result = wait_for_task(task["id"])
print(result["result"])
```

### Streaming de Logs

```python
import requests
import time

def stream_logs(task_id):
    """Mostra logs em tempo real"""
    last_log_count = 0
    
    while True:
        response = requests.get(f"http://localhost:8000/tasks/{task_id}")
        task = response.json()
        
        # Mostrar novos logs
        new_logs = task["logs"][last_log_count:]
        for log in new_logs:
            print(f"[{log['timestamp']}] {log['message']}")
        
        last_log_count = len(task["logs"])
        
        # Parar se task terminou
        if task["state"] in ["completed", "failed", "cancelled"]:
            break
        
        time.sleep(0.5)

# Uso
task = create_task("Tarefa longa")
stream_logs(task["id"])
```

### Batch Processing

```python
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_files(files):
    """Processa múltiplos arquivos em paralelo"""
    
    def create_and_wait(file):
        # Criar task
        response = requests.post(
            "http://localhost:8000/tasks",
            json={
                "objective": f"Analisar arquivo {file}",
                "context": {"file": file}
            }
        )
        task_id = response.json()["id"]
        
        # Aguardar
        return wait_for_task(task_id)
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(create_and_wait, f): f for f in files}
        
        for future in as_completed(futures):
            file = futures[future]
            try:
                result = future.result()
                print(f"✅ {file}: {result['result']['output']}")
            except Exception as e:
                print(f"❌ {file}: {e}")

# Uso
process_files(["file1.py", "file2.py", "file3.py"])
```

### Error Handling

```python
import requests

def safe_create_task(objective, max_retries=3):
    """Cria task com retry em caso de erro"""
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "http://localhost:8000/tasks",
                json={"objective": objective},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            print(f"Timeout (tentativa {attempt + 1}/{max_retries})")
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                # Erro de validação - não retry
                print(f"Validação falhou: {e.response.json()}")
                raise
            print(f"HTTP error (tentativa {attempt + 1}/{max_retries})")
            
        except requests.exceptions.ConnectionError:
            print("Servidor offline, aguardando...")
            time.sleep(5)
    
    raise Exception(f"Falhou após {max_retries} tentativas")
```

---

## 🔗 Links Úteis

- **OpenAPI Spec:** http://localhost:8000/openapi.json
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health:** http://localhost:8000/health

---

**API Version:** 1.0  
**Last Updated:** Janeiro 2026