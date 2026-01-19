# 💡 Examples - Casos de Uso Práticos

Exemplos reais de como usar o Linux Code Agent no dia a dia.

---

## 📋 Índice

1. [Automação de Tarefas](#automação-de-tarefas)
2. [Desenvolvimento de Software](#desenvolvimento-de-software)
3. [DevOps & Infraestrutura](#devops--infraestrutura)
4. [Data Science](#data-science)
5. [Integração com IDEs](#integração-com-ides)

---

## 🤖 Automação de Tarefas

### 1. Criar Estrutura de Projeto

```python
import requests

def create_project_structure(project_name, language="python"):
    """Cria estrutura completa de projeto"""
    
    objective = f"""
    Criar estrutura de projeto para {project_name} em {language}:
    
    1. Criar diretório {project_name}/
    2. Estrutura:
       - README.md com documentação básica
       - .gitignore para {language}
       - LICENSE (MIT)
       - src/ ou lib/ dependendo da linguagem
       - tests/ para testes
       - requirements.txt ou package.json
    3. Inicializar git repository
    4. Fazer primeiro commit
    """
    
    response = requests.post(
        "http://localhost:8000/tasks",
        json={
            "objective": objective,
            "context": {
                "project_name": project_name,
                "language": language
            }
        }
    )
    
    return response.json()

# Uso
task = create_project_structure("my-awesome-api", "python")
print(f"Projeto sendo criado... ID: {task['id']}")
```

### 2. Limpeza de Código

```python
def cleanup_python_project():
    """Remove arquivos desnecessários e organiza código"""
    
    objective = """
    Limpar projeto Python:
    
    1. Remover arquivos __pycache__/ recursivamente
    2. Remover arquivos .pyc e .pyo
    3. Remover diretórios .pytest_cache/
    4. Organizar imports com isort
    5. Formatar código com black
    6. Gerar requirements.txt atualizado
    """
    
    response = requests.post(
        "http://localhost:8000/tasks",
        json={"objective": objective}
    )
    
    return response.json()
```

### 3. Backup Automático

```python
def create_backup(directories, destination):
    """Cria backup compactado de diretórios"""
    
    dirs_str = ", ".join(directories)
    
    objective = f"""
    Criar backup dos diretórios: {dirs_str}
    
    1. Criar arquivo backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tar.gz
    2. Compactar diretórios especificados
    3. Mover para {destination}
    4. Verificar integridade do arquivo
    5. Remover backups antigos (manter últimos 5)
    """
    
    response = requests.post(
        "http://localhost:8000/tasks",
        json={
            "objective": objective,
            "context": {
                "directories": directories,
                "destination": destination
            }
        }
    )
    
    return response.json()

# Uso
backup = create_backup(
    directories=["~/projetos", "~/documentos"],
    destination="~/backups"
)
```

---

## 💻 Desenvolvimento de Software

### 4. Criar API REST

```python
def scaffold_rest_api(resource_name, fields):
    """Gera código de API REST completa"""
    
    fields_str = ", ".join([f"{k}: {v}" for k, v in fields.items()])
    
    objective = f"""
    Criar API REST para recurso '{resource_name}':
    
    Campos: {fields_str}
    
    Gerar:
    1. Model (SQLAlchemy ou Pydantic)
    2. Schema de validação
    3. CRUD repository
    4. Endpoints (GET, POST, PUT, DELETE)
    5. Testes unitários
    6. Documentação OpenAPI
    
    Usar FastAPI + Pydantic + SQLAlchemy
    """
    
    response = requests.post(
        "http://localhost:8000/tasks",
        json={
            "objective": objective,
            "context": {
                "resource": resource_name,
                "fields": fields
            }
        }
    )
    
    return response.json()

# Uso
api = scaffold_rest_api(
    resource_name="User",
    fields={
        "id": "int",
        "name": "str",
        "email": "str",
        "created_at": "datetime"
    }
)
```

### 5. Refatorar Código

```python
def refactor_code(file_path, improvements):
    """Refatora código seguindo melhores práticas"""
    
    objective = f"""
    Refatorar arquivo {file_path}:
    
    Melhorias solicitadas:
    {chr(10).join(f'- {imp}' for imp in improvements)}
    
    Manter:
    - Funcionalidade existente
    - Testes passando
    - Compatibilidade com código existente
    
    Adicionar:
    - Type hints onde faltam
    - Docstrings em funções públicas
    - Tratamento de erros apropriado
    """
    
    response = requests.post(
        "http://localhost:8000/tasks",
        json={
            "objective": objective,
            "context": {
                "file": file_path,
                "improvements": improvements
            }
        }
    )
    
    return response.json()

# Uso
refactor = refactor_code(
    file_path="app/services/user_service.py",
    improvements=[
        "Extrair métodos longos",
        "Remover código duplicado",
        "Melhorar nomes de variáveis",
        "Adicionar validação de entrada"
    ]
)
```

### 6. Gerar Testes

```python
def generate_tests(module_path, coverage_target=80):
    """Gera testes automaticamente"""
    
    objective = f"""
    Gerar testes para módulo {module_path}:
    
    1. Analisar funções e classes públicas
    2. Gerar testes unitários com pytest
    3. Incluir casos de sucesso e falha
    4. Adicionar fixtures necessários
    5. Atingir pelo menos {coverage_target}% de coverage
    6. Incluir testes de edge cases
    
    Usar:
    - pytest
    - pytest-mock para mocks
    - Factory pattern para fixtures
    """
    
    response = requests.post(
        "http://localhost:8000/tasks",
        json={
            "objective": objective,
            "context": {
                "module": module_path,
                "coverage_target": coverage_target
            }
        }
    )
    
    return response.json()

# Uso
tests = generate_tests(
    module_path="app/core/agent.py",
    coverage_target=90
)
```

---

## 🔧 DevOps & Infraestrutura

### 7. Setup CI/CD

```python
def setup_cicd(platform="github"):
    """Configura pipeline CI/CD"""
    
    objective = f"""
    Configurar CI/CD com {platform} Actions:
    
    Pipeline deve:
    1. Rodar em push para main e pull requests
    2. Executar testes (pytest)
    3. Verificar linting (flake8, black)
    4. Verificar type hints (mypy)
    5. Medir coverage (mínimo 80%)
    6. Build de imagem Docker
    7. Push para registry (se main)
    8. Deploy automático (staging)
    
    Criar:
    - .github/workflows/ci.yml
    - .github/workflows/cd.yml
    - Dockerfile se não existir
    - Scripts de deploy
    """
    
    response = requests.post(
        "http://localhost:8000/tasks",
        json={
            "objective": objective,
            "context": {"platform": platform}
        }
    )
    
    return response.json()

# Uso
cicd = setup_cicd(platform="github")
```

### 8. Containerizar Aplicação

```python
def dockerize_app(app_type="fastapi"):
    """Cria Dockerfile otimizado"""
    
    objective = f"""
    Criar setup Docker para aplicação {app_type}:
    
    Gerar:
    1. Dockerfile multi-stage para produção
    2. Dockerfile.dev para desenvolvimento
    3. docker-compose.yml completo
    4. .dockerignore
    5. Scripts de build e run
    
    Dockerfile deve:
    - Usar Python 3.11 slim
    - Multi-stage build (menor imagem)
    - Non-root user
    - Health checks
    - Otimizado para cache
    
    docker-compose deve incluir:
    - App principal
    - PostgreSQL
    - Redis
    - Volumes persistentes
    - Network isolada
    """
    
    response = requests.post(
        "http://localhost:8000/tasks",
        json={
            "objective": objective,
            "context": {"app_type": app_type}
        }
    )
    
    return response.json()

# Uso
docker = dockerize_app(app_type="fastapi")
```

### 9. Monitoramento

```python
def setup_monitoring():
    """Configura stack de monitoramento"""
    
    objective = """
    Setup de monitoramento completo:
    
    1. Prometheus:
       - Configurar scraping de métricas
       - Criar alertas básicos
       - prometheus.yml
    
    2. Grafana:
       - Dashboard de aplicação
       - Dashboard de infraestrutura
       - Alertas configurados
    
    3. Instrumentação:
       - Adicionar prometheus_client ao código
       - Métricas customizadas
       - Health checks
    
    4. docker-compose.monitoring.yml
    
    Métricas a coletar:
    - Request rate
    - Response time
    - Error rate
    - Task duration
    - Active tasks
    """
    
    response = requests.post(
        "http://localhost:8000/tasks",
        json={"objective": objective}
    )
    
    return response.json()

# Uso
monitoring = setup_monitoring()
```

---

## 📊 Data Science

### 10. Análise de Dados

```python
def analyze_dataset(csv_path):
    """Análise exploratória de dataset"""
    
    objective = f"""
    Análise exploratória do dataset {csv_path}:
    
    Gerar notebook Jupyter com:
    
    1. Carregamento e inspeção inicial
       - df.info()
       - df.describe()
       - Tipos de dados
       - Missing values
    
    2. Visualizações:
       - Distribuição de variáveis numéricas
       - Correlação entre features
       - Outliers (boxplots)
       - Pairplot das principais features
    
    3. Limpeza:
       - Tratamento de missing values
       - Detecção de outliers
       - Normalização/padronização
    
    4. Feature Engineering:
       - Novas features relevantes
       - Encoding de categorias
       - Seleção de features
    
    5. Relatório markdown com insights
    """
    
    response = requests.post(
        "http://localhost:8000/tasks",
        json={
            "objective": objective,
            "context": {"csv_path": csv_path}
        }
    )
    
    return response.json()

# Uso
analysis = analyze_dataset("data/sales.csv")
```

### 11. Machine Learning Pipeline

```python
def create_ml_pipeline(problem_type, target_column):
    """Cria pipeline de ML end-to-end"""
    
    objective = f"""
    Criar pipeline de ML para {problem_type}:
    
    Target: {target_column}
    
    Pipeline deve incluir:
    
    1. Data Loading e Split
       - Train/validation/test split
       - Stratified se classificação
    
    2. Preprocessing
       - Imputer para missing values
       - Scaler para numéricas
       - Encoder para categóricas
       - Pipeline do sklearn
    
    3. Modelo
       - Baseline (dummy)
       - Random Forest
       - Gradient Boosting
       - Comparação de modelos
    
    4. Evaluation
       - Métricas apropriadas
       - Confusion matrix (se classificação)
       - Feature importance
       - Cross-validation
    
    5. Código de treino e inferência
    6. Serialização do modelo (joblib)
    7. API de predição (FastAPI)
    """
    
    response = requests.post(
        "http://localhost:8000/tasks",
        json={
            "objective": objective,
            "context": {
                "problem_type": problem_type,
                "target": target_column
            }
        }
    )
    
    return response.json()

# Uso
ml_pipeline = create_ml_pipeline(
    problem_type="classification",
    target_column="churn"
)
```

---

## 🔌 Integração com IDEs

### 12. VSCode Extension (Exemplo de Uso)

```javascript
// extension.js (VSCode extension)
const vscode = require('vscode');
const axios = require('axios');

async function createTaskFromSelection() {
    const editor = vscode.window.activeTextEditor;
    const selection = editor.document.getText(editor.selection);
    
    const objective = await vscode.window.showInputBox({
        prompt: 'O que você quer fazer com o código selecionado?',
        placeHolder: 'Ex: Refatorar para usar async/await'
    });
    
    if (!objective) return;
    
    try {
        const response = await axios.post('http://localhost:8000/tasks', {
            objective: objective,
            context: {
                code: selection,
                file: editor.document.fileName,
                language: editor.document.languageId
            }
        });
        
        const taskId = response.data.id;
        
        // Monitorar task
        const result = await pollTask(taskId);
        
        if (result.result.success) {
            // Aplicar mudanças
            const edit = new vscode.WorkspaceEdit();
            edit.replace(
                editor.document.uri,
                editor.selection,
                result.result.output
            );
            await vscode.workspace.applyEdit(edit);
            
            vscode.window.showInformationMessage('Código atualizado!');
        }
    } catch (error) {
        vscode.window.showErrorMessage(`Erro: ${error.message}`);
    }
}

async function pollTask(taskId) {
    const maxAttempts = 60;
    let attempts = 0;
    
    while (attempts < maxAttempts) {
        const response = await axios.get(`http://localhost:8000/tasks/${taskId}`);
        const task = response.data;
        
        if (task.state === 'completed' || task.state === 'failed') {
            return task;
        }
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        attempts++;
    }
    
    throw new Error('Timeout aguardando task');
}

function activate(context) {
    let disposable = vscode.commands.registerCommand(
        'codeagent.processSelection',
        createTaskFromSelection
    );
    
    context.subscriptions.push(disposable);
}

exports.activate = activate;
```

### 13. Workflow Complexo

```python
def complex_feature_development(feature_name, description):
    """Desenvolve feature completa do início ao fim"""
    
    tasks = []
    
    # 1. Criar branch
    tasks.append(create_task(f"Criar branch feature/{feature_name}"))
    
    # 2. Gerar código
    tasks.append(create_task(f"""
    Implementar feature {feature_name}:
    {description}
    
    Criar:
    - Módulo principal
    - Testes unitários
    - Testes de integração
    - Documentação
    """))
    
    # 3. Code review automático
    tasks.append(create_task("""
    Revisar código criado:
    - Verificar boas práticas
    - Sugerir melhorias
    - Verificar coverage de testes
    """))
    
    # 4. Atualizar docs
    tasks.append(create_task("""
    Atualizar documentação:
    - README.md
    - API docs
    - Changelog
    """))
    
    # 5. Criar PR
    tasks.append(create_task(f"""
    Criar Pull Request:
    - Título: feat: {feature_name}
    - Descrição detalhada
    - Link para issue se houver
    """))
    
    return tasks

# Uso
feature_tasks = complex_feature_development(
    feature_name="user-authentication",
    description="Sistema de autenticação JWT com refresh tokens"
)

# Aguardar todas as tasks
for task in feature_tasks:
    wait_for_task(task['id'])
    
print("Feature completa!")
```

---

## 🎨 Casos de Uso Criativos

### 14. Documentação Automática

```python
def auto_document_codebase():
    """Gera documentação completa do projeto"""
    
    objective = """
    Gerar documentação técnica completa:
    
    1. Analisar todo o codebase
    2. Gerar:
       - README.md principal
       - API documentation
       - Architecture diagram (mermaid)
       - Contributing guide
       - Code of conduct
    
    3. Para cada módulo:
       - Docstrings completos
       - Exemplos de uso
       - Parâmetros documentados
    
    4. Gerar mkdocs.yml e docs/
    5. Deploy docs (GitHub Pages ou ReadTheDocs)
    """
    
    return create_task(objective)
```

### 15. Code Migration

```python
def migrate_codebase(from_version, to_version):
    """Migra código para nova versão"""
    
    objective = f"""
    Migrar codebase de {from_version} para {to_version}:
    
    1. Identificar breaking changes
    2. Atualizar imports e APIs deprecated
    3. Adaptar código para nova sintaxe
    4. Atualizar dependências
    5. Rodar testes e corrigir falhas
    6. Gerar relatório de migração
    
    Manter:
    - Funcionalidade existente
    - Performance equivalente
    - Compatibilidade de API pública
    """
    
    return create_task(objective, {
        "from_version": from_version,
        "to_version": to_version
    })

# Uso
migration = migrate_codebase(
    from_version="Python 3.8",
    to_version="Python 3.11"
)
```

---

## 📚 Recursos Adicionais

### Helper Functions

```python
import requests
import time
from typing import Dict, Any

def create_task(objective: str, context: Dict = None) -> Dict[str, Any]:
    """Wrapper para criar tasks"""
    response = requests.post(
        "http://localhost:8000/tasks",
        json={
            "objective": objective,
            "context": context or {}
        }
    )
    return response.json()

def wait_for_task(task_id: str, timeout: int = 300) -> Dict[str, Any]:
    """Aguarda task completar"""
    start = time.time()
    
    while time.time() - start < timeout:
        response = requests.get(f"http://localhost:8000/tasks/{task_id}")
        task = response.json()
        
        if task["state"] in ["completed", "failed", "cancelled"]:
            return task
        
        time.sleep(2)
    
    raise TimeoutError(f"Task {task_id} não completou em {timeout}s")

def get_task_result(task_id: str) -> str:
    """Retorna apenas o output da task"""
    task = wait_for_task(task_id)
    
    if task["state"] == "completed":
        return task["result"]["output"]
    else:
        error = task["result"]["error"] if task["result"] else "Unknown error"
        raise Exception(f"Task failed: {error}")
```

---

**Mais exemplos sendo adicionados regularmente!**

Para contribuir com seus próprios exemplos, abra um PR ou Issue. 🚀