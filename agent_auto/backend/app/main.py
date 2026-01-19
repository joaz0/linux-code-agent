# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.chat import router as chat_router
from app.api.execute import router as execute_router
from app.api.health import router as health_router
from app.api.llm import router as llm_router  # Novo router para LLM management
from app.core.config import settings
from app.core.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Linux Code Agent Backend v2.0",
    description="Sistema autônomo com multi-provider LLM e AWS Toolkit support",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(chat_router)
app.include_router(execute_router)
app.include_router(health_router)
app.include_router(llm_router, prefix="/api/v1/llm", tags=["LLM Management"])


@app.get("/")
async def root():
    from app.core.aws_toolkit import AWSToolkitDetector
    from app.core.planner import Planner
    
    # Detecta configuração
    detector = AWSToolkitDetector()
    planner = Planner()
    
    return {
        "message": "Linux Code Agent Backend v2.0 (Multi-Provider)",
        "status": "running",
        "features": {
            "multi_provider": True,
            "aws_toolkit_support": detector.detect_credentials(),
            "available_providers": planner.multi_provider.get_available_providers()
        },
        "endpoints": {
            "chat": "/api/chat",
            "execute": "/api/execute",
            "llm_metrics": "/api/v1/llm/metrics",
            "llm_providers": "/api/v1/llm/providers"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    from app.core.aws_toolkit import AWSToolkitDetector
    
    detector = AWSToolkitDetector()
    aws_status = detector.detect_credentials()
    
    return {
        "status": "healthy",
        "aws_credentials": aws_status,
        "timestamp": datetime.now().isoformat()
    }


# Adicionar import datetime
from datetime import datetime

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Linux Code Agent Backend v2.0")
    logger.info("Features: Multi-Provider LLM, AWS Toolkit support")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )