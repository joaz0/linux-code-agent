"""
FastAPI Application - Entrypoint principal
Responsável por: criar app, registrar rotas, configurar middleware
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Carregar .env ANTES de importar outros módulos
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from app.api.routes import tasks


def create_app() -> FastAPI:
    """
    Factory para criar a aplicação FastAPI
    
    Returns:
        FastAPI app configurada
    """
    app = FastAPI(
        title="Linux Code Agent API",
        description="""
        🤖 **Agente de desenvolvimento local e autônomo**
        
        Similar ao Amazon Q / GitHub Copilot, mas:
        - ✅ 100% local
        - ✅ Execução real de ações
        - ✅ Controle total
        - ✅ Open source
        
        ## Features
        
        - 🧠 Planejamento inteligente via LLM
        - 🔧 Execução de comandos shell
        - 📁 Manipulação de arquivos
        - 🔀 Operações git
        - 📊 Status e logs em tempo real
        - ⏸️ Cancelamento de tasks
        
        ## Como usar
        
        1. Crie uma task em `POST /tasks`
        2. Acompanhe o progresso em `GET /tasks/{id}`
        3. Veja estatísticas em `GET /tasks/stats`
        
        A execução é **assíncrona** - a task roda em background.
        """,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS - permitir acesso de qualquer origem (desenvolvimento)
    # TODO: Restringir em produção
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Registrar rotas
    app.include_router(tasks.router)
    
    # Health check
    @app.get("/", tags=["health"])
    async def root():
        """Health check endpoint"""
        return {
            "status": "online",
            "service": "Linux Code Agent",
            "version": "0.1.0",
            "docs": "/docs"
        }
    
    @app.get("/health", tags=["health"])
    async def health():
        """Detailed health check"""
        from app.services.task_service import get_task_service
        
        task_service = get_task_service()
        stats = task_service.get_stats()
        
        return {
            "status": "healthy",
            "tasks": stats
        }
    
    return app


# Criar instância global
app = create_app()


if __name__ == "__main__":
    """
    Roda o servidor diretamente
    Uso: python -m app.app
    """
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload em desenvolvimento
        log_level="info"
    )