# apps/services/user-settings-service/main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# Imports locais
from database import get_db, AgentModel, ToolModel, create_tables, test_connection

app = FastAPI(title="User Settings Service", version="1.0.0")

# Modelos Pydantic (mantendo compatibilidade com o frontend)
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

class AgentCreate(BaseModel):
    name: str
    type: str
    isDefault: bool = False
    systemPrompt: str
    tools: List[Tool]

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    systemPrompt: Optional[str] = None
    tools: Optional[List[Tool]] = None

# Função para converter AgentModel para Pydantic Agent
def agent_model_to_pydantic(agent_model: AgentModel) -> Agent:
    tools_data = agent_model.tools or []
    tools = [Tool(**tool_data) for tool_data in tools_data]
    
    return Agent(
        id=agent_model.id,
        name=agent_model.name,
        type=agent_model.type,
        isDefault=agent_model.is_default,
        systemPrompt=agent_model.system_prompt,
        tools=tools
    )

# Startup event para criar tabelas e dados iniciais
@app.on_event("startup")
async def startup_event():
    """Inicialização do serviço"""
    print("🚀 Inicializando User Settings Service...")
    
    # Testar conexão
    if not test_connection():
        print("❌ Falha na conexão com PostgreSQL!")
        return
    
    # Criar tabelas
    create_tables()
    
    # Inserir agentes padrão se não existirem
    db = next(get_db())
    existing_agents = db.query(AgentModel).filter(AgentModel.is_default == True).count()
    
    if existing_agents == 0:
        print("📝 Criando agentes padrão...")
        
        # Agente Pessoal
        personal_agent = AgentModel(
            name="Calendário Pessoal",
            type="Pessoal",
            system_prompt="Você é um assistente de agenda pessoal. Ajude com compromissos pessoais, eventos familiares e atividades de lazer.",
            tools=[{
                "name": "consultar_agenda_pessoal",
                "description": "Consulta eventos na agenda pessoal do usuário",
                "apiEndpoint": "/api/calendar/personal",
                "parameters": [
                    {"name": "data_inicio", "type": "data"},
                    {"name": "data_fim", "type": "data"}
                ]
            }],
            is_default=True
        )
        
        # Agente Profissional
        professional_agent = AgentModel(
            name="Calendário Profissional",
            type="Profissional",
            system_prompt="Você é um assistente de agenda profissional. Ajude com reuniões, projetos e compromissos de trabalho.",
            tools=[{
                "name": "consultar_agenda_profissional",
                "description": "Consulta eventos na agenda profissional do usuário",
                "apiEndpoint": "/api/calendar/professional",
                "parameters": [
                    {"name": "data_inicio", "type": "data"},
                    {"name": "data_fim", "type": "data"}
                ]
            }],
            is_default=True
        )
        
        db.add(personal_agent)
        db.add(professional_agent)
        db.commit()
        print("✅ Agentes padrão criados!")
    
    db.close()

@app.get("/health")
async def health_check():
    """Verificação de saúde do serviço"""
    return {
        "status": "healthy", 
        "service": "user-settings-service",
        "database": "postgresql",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/agents", response_model=List[Agent])
async def get_agents(db: Session = Depends(get_db)):
    """Retorna todos os agentes configurados"""
    try:
        agents = db.query(AgentModel).order_by(AgentModel.created_at).all()
        return [agent_model_to_pydantic(agent) for agent in agents]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar agentes: {str(e)}")

@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Retorna um agente específico"""
    agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    return agent_model_to_pydantic(agent)

@app.post("/agents", response_model=Agent)
async def create_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """Cria um novo agente personalizado"""
    try:
        # Validar se já existe agente com mesmo nome
        existing = db.query(AgentModel).filter(AgentModel.name == agent_data.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Já existe um agente com este nome")
        
        # Converter tools para JSON
        tools_json = [tool.dict() for tool in agent_data.tools]
        
        # Criar novo agente
        db_agent = AgentModel(
            name=agent_data.name,
            type=agent_data.type,
            system_prompt=agent_data.systemPrompt,
            tools=tools_json,
            is_default=agent_data.isDefault
        )
        
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        
        return agent_model_to_pydantic(db_agent)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar agente: {str(e)}")

@app.put("/agents/{agent_id}", response_model=Agent)
async def update_agent(agent_id: int, agent_update: AgentUpdate, db: Session = Depends(get_db)):
    """Atualiza um agente existente"""
    try:
        # Buscar agente
        agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        # Verificar se pode editar agente padrão
        if agent.is_default and agent_update.name and agent_update.name != agent.name:
            raise HTTPException(status_code=400, detail="Não é possível alterar o nome de agentes padrão")
        
        # Atualizar campos fornecidos
        if agent_update.name:
            # Verificar se novo nome já existe
            existing = db.query(AgentModel).filter(
                AgentModel.name == agent_update.name,
                AgentModel.id != agent_id
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Já existe um agente com este nome")
            agent.name = agent_update.name
        
        if agent_update.type:
            agent.type = agent_update.type
        
        if agent_update.systemPrompt:
            agent.system_prompt = agent_update.systemPrompt
        
        if agent_update.tools:
            agent.tools = [tool.dict() for tool in agent_update.tools]
        
        # Atualizar timestamp
        agent.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(agent)
        
        return agent_model_to_pydantic(agent)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar agente: {str(e)}")

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Deleta um agente (não permite deletar agentes padrão)"""
    try:
        agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        if agent.is_default:
            raise HTTPException(status_code=400, detail="Não é possível deletar agentes padrão")
        
        db.delete(agent)
        db.commit()
        
        return {"message": f"Agente '{agent.name}' deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar agente: {str(e)}")

@app.post("/agents/{agent_id}/duplicate", response_model=Agent)
async def duplicate_agent(agent_id: int, db: Session = Depends(get_db)):
    """Duplica um agente existente"""
    try:
        # Buscar agente original
        original_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
        if not original_agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        
        # Gerar nome único para a cópia
        copy_name = f"{original_agent.name} (Cópia)"
        counter = 1
        while db.query(AgentModel).filter(AgentModel.name == copy_name).first():
            counter += 1
            copy_name = f"{original_agent.name} (Cópia {counter})"
        
        # Criar agente duplicado
        duplicated_agent = AgentModel(
            name=copy_name,
            type=original_agent.type,
            system_prompt=original_agent.system_prompt,
            tools=original_agent.tools.copy() if original_agent.tools else [],
            is_default=False  # Cópias nunca são padrão
        )
        
        db.add(duplicated_agent)
        db.commit()
        db.refresh(duplicated_agent)
        
        return agent_model_to_pydantic(duplicated_agent)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao duplicar agente: {str(e)}")

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Retorna estatísticas dos agentes"""
    try:
        total_agents = db.query(AgentModel).count()
        personal_agents = db.query(AgentModel).filter(AgentModel.type == "Pessoal").count()
        professional_agents = db.query(AgentModel).filter(AgentModel.type == "Profissional").count()
        default_agents = db.query(AgentModel).filter(AgentModel.is_default == True).count()
        custom_agents = total_agents - default_agents
        
        return {
            "total_agents": total_agents,
            "personal_agents": personal_agents,
            "professional_agents": professional_agents,
            "default_agents": default_agents,
            "custom_agents": custom_agents,
            "database": "postgresql"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)