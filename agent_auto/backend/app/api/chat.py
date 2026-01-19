from fastapi import APIRouter
from app.schemas.chat import ChatRequest

router = APIRouter()

@router.post("/chat")
async def chat(req: ChatRequest):
    return {"resposta": f"✅ Você disse: {req.mensagem}"}