from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log da URL do banco de dados para debug
db_url = os.getenv("DATABASE_URL", "postgresql://agente_user:agente_pass@postgres:5432/agente_db")
logger.info(f"Database URL: {db_url}")

app = FastAPI(title="User Settings Service", version="1.0.0")

class Tool(BaseModel):
    name: str
    description: str
    apiEndpoint: str
    parameters: List[Dict[str, Any]]

class Agent(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    isDefault: bool = False
    systemPrompt: str
    tools: List[Tool]

# Agentes padrão do sistema
DEFAULT_AGENTS = [
    Agent(
        id=1,
        name="Calendário Pessoal",
        type="Pessoal", 
        isDefault=True,
        systemPrompt="Você é um assistente de agenda pessoal. Ajude com compromissos pessoais, eventos familiares e atividades de lazer.",
        tools=[{
            "name": "consultar_agenda_pessoal",
            "description": "Consulta eventos na agenda pessoal do usuário",
            "apiEndpoint": "/api/calendar/personal",
            "parameters": [
                {"name": "data_inicio", "type": "data"},
                {"name": "data_fim", "type": "data"}
            ]
        }]
    ),
    Agent(
        id=2,
        name="Calendário Profissional",
        type="Profissional",
        isDefault=True,
        systemPrompt="Você é um assistente de agenda profissional. Ajude com reuniões, projetos e compromissos de trabalho.",
        tools=[{
            "name": "consultar_agenda_profissional",
            "description": "Consulta eventos na agenda profissional do usuário",
            "apiEndpoint": "/api/calendar/professional",
            "parameters": [
                {"name": "data_inicio", "type": "data"},
                {"name": "data_fim", "type": "data"}
            ]
        }]
    )
]

# Armazenamento em memória para desenvolvimento
CUSTOM_AGENTS = []

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-settings-service"}

@app.get("/agents")
async def get_agents() -> List[Agent]:
    """Retorna todos os agentes (padrão + customizados)"""
    return DEFAULT_AGENTS + CUSTOM_AGENTS

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: int) -> Agent:
    """Retorna um agente específico"""
    all_agents = DEFAULT_AGENTS + CUSTOM_AGENTS
    agent = next((a for a in all_agents if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    return agent

@app.post("/agents")
async def create_agent(agent: Agent) -> Agent:
    """Cria um novo agente customizado"""
    # Gerar novo ID
    all_agents = DEFAULT_AGENTS + CUSTOM_AGENTS
    max_id = max([a.id for a in all_agents if a.id], default=0)
    agent.id = max_id + 1
    
    # Agentes customizados não podem ser padrão
    agent.isDefault = False
    
    CUSTOM_AGENTS.append(agent)
    return agent

@app.put("/agents/{agent_id}")
async def update_agent(agent_id: int, agent_data: Agent) -> Agent:
    """Atualiza um agente customizado"""
    # Não permite editar agentes padrão
    if agent_id <= 2:
        raise HTTPException(status_code=400, detail="Não é possível editar agentes padrão")
    
    agent_index = next((i for i, a in enumerate(CUSTOM_AGENTS) if a.id == agent_id), None)
    if agent_index is None:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    agent_data.id = agent_id
    agent_data.isDefault = False
    CUSTOM_AGENTS[agent_index] = agent_data
    return agent_data

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int):
    """Remove um agente customizado"""
    # Não permite deletar agentes padrão
    if agent_id <= 2:
        raise HTTPException(status_code=400, detail="Não é possível deletar agentes padrão")
    
    agent_index = next((i for i, a in enumerate(CUSTOM_AGENTS) if a.id == agent_id), None)
    if agent_index is None:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    del CUSTOM_AGENTS[agent_index]
    return {"message": "Agente removido com sucesso"}

@app.post("/agents/{agent_id}/duplicate")
async def duplicate_agent(agent_id: int) -> Agent:
    """Duplica um agente existente"""
    all_agents = DEFAULT_AGENTS + CUSTOM_AGENTS
    original_agent = next((a for a in all_agents if a.id == agent_id), None)
    if not original_agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    # Criar nova instância
    new_agent = Agent(
        name=f"{original_agent.name} - Cópia",
        type=original_agent.type,
        isDefault=False,
        systemPrompt=original_agent.systemPrompt,
        tools=original_agent.tools.copy()
    )
    
    # Gerar novo ID
    max_id = max([a.id for a in all_agents if a.id], default=0)
    new_agent.id = max_id + 1
    
    CUSTOM_AGENTS.append(new_agent)
    return new_agent

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)