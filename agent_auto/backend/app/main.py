from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.execute import router as execute_router
from app.api.health import router as health_router
from app.core.config import settings
from app.core.logger import setup_logging

setup_logging()

app = FastAPI(title="Linux Code Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(execute_router)
app.include_router(health_router)
@app.get("/")
async def root():
    return {"message": "Linux Code Agent Backend is running."}