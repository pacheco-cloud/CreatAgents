from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os

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
        tools=[Tool(
            name="consultar_agenda_pessoal",
            description="Consulta eventos na agenda pessoal do usuário",
            apiEndpoint="/api/calendar/personal",
            parameters=[
                {"name": "data_inicio", "type": "data"},
                {"name": "data_fim", "type": "data"}
            ]
        )]
    ),
    Agent(
        id=2,
        name="Calendário Profissional",
        type="Profissional",
        isDefault=True, 
        systemPrompt="Você é um assistente de agenda profissional. Ajude com reuniões, projetos e compromissos de trabalho.",
        tools=[Tool(
            name="consultar_agenda_profissional",
            description="Consulta eventos na agenda profissional do usuário", 
            apiEndpoint="/api/calendar/professional",
            parameters=[
                {"name": "data_inicio", "type": "data"},
                {"name": "data_fim", "type": "data"}
            ]
        )]
    )
]

# Simulando um "banco de dados" em memória
agents_db = DEFAULT_AGENTS.copy()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-settings-service"}

@app.get("/agents")
async def get_agents() -> List[Agent]:
    """Retorna todos os agentes configurados"""
    return agents_db

@app.post("/agents")
async def create_agent(agent: Agent) -> Agent:
    """Cria um novo agente personalizado"""
    agent.id = max([a.id for a in agents_db], default=0) + 1
    agents_db.append(agent)
    return agent

@app.put("/agents/{agent_id}")
async def update_agent(agent_id: int, agent: Agent) -> Agent:
    """Atualiza um agente existente"""
    for i, a in enumerate(agents_db):
        if a.id == agent_id:
            agent.id = agent_id
            agents_db[i] = agent
            return agent
    raise HTTPException(status_code=404, detail="Agent not found")

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int):
    """Deleta um agente (não permite deletar agentes padrão)"""
    agent = next((a for a in agents_db if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent.isDefault:
        raise HTTPException(status_code=400, detail="Cannot delete default agent")
    
    agents_db[:] = [a for a in agents_db if a.id != agent_id]
    return {"message": "Agent deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
