from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Dict, Any

app = FastAPI(title="API Gateway", version="1.0.0")

# CORS para permitir requests do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração dos microserviços
SERVICES = {
    "orchestrator": "http://localhost:8001",
    "calendar": "http://localhost:8002",
    "settings": "http://localhost:8003",
    "tool-factory": "http://localhost:8004"
}

class ChatMessage(BaseModel):
    message: str
    user_id: str = "default_user"

class AgentConfig(BaseModel):
    name: str
    type: str
    system_prompt: str
    tools: list

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

@app.post("/chat")
async def chat_endpoint(request: ChatMessage):
    """Rota principal para o chat - encaminha para o orquestrador"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVICES['orchestrator']}/process",
                json=request.dict()
            )
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Orchestrator service unavailable: {e}")

@app.get("/agents")
async def get_agents():
    """Lista todos os agentes configurados"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICES['settings']}/agents")
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Settings service unavailable")

@app.post("/agents")
async def create_agent(agent_config: AgentConfig):
    """Cria um novo agente"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVICES['settings']}/agents",
                json=agent_config.dict()
            )
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Settings service unavailable")

@app.get("/calendar/{calendar_type}")
async def get_calendar(calendar_type: str):
    """Busca eventos do calendário"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICES['calendar']}/{calendar_type}")
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Calendar service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
