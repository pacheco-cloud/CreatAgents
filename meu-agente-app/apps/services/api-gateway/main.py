from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx
import os
from typing import Dict, Any
import logging

app = FastAPI(title="API Gateway", version="1.0.0")
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

# CORS para permitir requests do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração dos microserviços
SERVICES = {
    "orchestrator": "http://orchestrator-agent:8001",
    "calendar": "http://calendar-service:8002",
    "settings": "http://user-settings-service:8004"
}

class ChatMessage(BaseModel):
    message: str
    user_id: str = "default_user"

class AgentConfig(BaseModel):
    name: str
    type: str
    systemPrompt: str
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

@app.post("/api/chat/process")
async def chat_process_endpoint(request: ChatMessage):
    """Rota alternativa para o chat - encaminha para o orquestrador"""
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
    print(f"[DEBUG] Iniciando requisição para: {SERVICES['settings']}/agents")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            print("[DEBUG] Cliente HTTP criado, fazendo requisição...")
            response = await client.get(f"{SERVICES['settings']}/agents")
            print(f"[DEBUG] Resposta recebida - Status: {response.status_code}")
            print(f"[DEBUG] Conteúdo da resposta: {response.text[:500]}...")
            response.raise_for_status()
            data = response.json()
            print(f"[DEBUG] JSON parseado com sucesso: {len(data) if isinstance(data, list) else 'objeto'}")
            return JSONResponse(content=data)
    except httpx.TimeoutException as e:
        print(f"[ERROR] Timeout ao conectar com settings-service: {e}")
        raise HTTPException(status_code=503, detail="Settings service timeout")
    except httpx.ConnectError as e:
        print(f"[ERROR] Erro de conexão com settings-service: {e}")
        raise HTTPException(status_code=503, detail="Settings service unavailable")
    except Exception as e:
        print(f"[ERROR] Erro inesperado ao buscar agentes: {type(e).__name__}: {e}")
        raise HTTPException(status_code=503, detail=f"Settings service unavailable: {e}")

@app.post("/agents")
async def create_agent(agent_config: AgentConfig):
    """Cria um novo agente"""
    print(f"[DEBUG] Criando agente: {agent_config.name}")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{SERVICES['settings']}/agents",
                json=agent_config.dict()
            )
            print(f"[DEBUG] Resposta criação agente - Status: {response.status_code}")
            response.raise_for_status()
            return JSONResponse(content=response.json())
    except httpx.TimeoutException as e:
        print(f"[ERROR] Timeout ao criar agente: {e}")
        raise HTTPException(status_code=503, detail="Settings service timeout")
    except httpx.ConnectError as e:
        print(f"[ERROR] Erro de conexão ao criar agente: {e}")
        raise HTTPException(status_code=503, detail="Settings service unavailable")
    except Exception as e:
        print(f"[ERROR] Erro inesperado ao criar agente: {type(e).__name__}: {e}")
        raise HTTPException(status_code=503, detail=f"Settings service unavailable: {e}")

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
