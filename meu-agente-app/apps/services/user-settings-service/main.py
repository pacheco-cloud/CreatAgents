# apps/services/user-settings-service/main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
import logging
import httpx
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://agente_user:agente_pass@postgres:5432/agente_db")
logger.info(f"Database URL: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class AgentModel(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)
    system_prompt = Column(Text, nullable=False)
    tools = Column(Text, nullable=False)  # JSON string
    service_id = Column(String, nullable=True)
    service_status = Column(String, default="created")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tabelas do banco criadas com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao criar tabelas: {e}")

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
    service_id: Optional[str] = None
    service_status: Optional[str] = None

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# URL do Tool Factory Service
TOOL_FACTORY_URL = os.getenv("TOOL_FACTORY_URL", "http://tool-factory-service:8004")

def init_default_agents(db: Session):
    """Inicializa agentes padrão se não existirem"""
    
    try:
        existing_agents = db.query(AgentModel).filter(AgentModel.is_default == True).count()
        if existing_agents > 0:
            logger.info("Agentes padrão já existem no banco")
            return
        
        logger.info("Criando agentes padrão...")
        
        default_agents = [
            {
                "id": 1,
                "name": "Calendário Pessoal",
                "type": "Pessoal",
                "is_default": True,
                "system_prompt": "Você é um assistente de agenda pessoal. Ajude com compromissos pessoais, eventos familiares e atividades de lazer.",
                "tools": json.dumps([{
                    "name": "consultar_agenda_pessoal",
                    "description": "Consulta eventos na agenda pessoal do usuário",
                    "apiEndpoint": "/api/calendar/personal",
                    "parameters": [
                        {"name": "data_inicio", "type": "data"},
                        {"name": "data_fim", "type": "data"}
                    ]
                }]),
                "service_status": "active"
            },
            {
                "id": 2,
                "name": "Calendário Profissional",
                "type": "Profissional",
                "is_default": True,
                "system_prompt": "Você é um assistente de agenda profissional. Ajude com reuniões, projetos e compromissos de trabalho.",
                "tools": json.dumps([{
                    "name": "consultar_agenda_profissional",
                    "description": "Consulta eventos na agenda profissional do usuário",
                    "apiEndpoint": "/api/calendar/professional",
                    "parameters": [
                        {"name": "data_inicio", "type": "data"},
                        {"name": "data_fim", "type": "data"}
                    ]
                }]),
                "service_status": "active"
            }
        ]
        
        for agent_data in default_agents:
            agent = AgentModel(**agent_data)
            db.add(agent)
        
        db.commit()
        logger.info("✅ Agentes padrão criados com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar agentes padrão: {e}")
        db.rollback()

def agent_model_to_pydantic(agent_model: AgentModel) -> Agent:
    """Converte modelo do banco para Pydantic"""
    try:
        tools_data = json.loads(agent_model.tools) if agent_model.tools else []
        tools = [Tool(**tool) for tool in tools_data]
        
        return Agent(
            id=agent_model.id,
            name=agent_model.name,
            type=agent_model.type,
            isDefault=agent_model.is_default,
            systemPrompt=agent_model.system_prompt,
            tools=tools,
            service_id=agent_model.service_id,
            service_status=agent_model.service_status
        )
    except Exception as e:
        logger.error(f"Erro ao converter agent_model para pydantic: {e}")
        # Retornar agent básico em caso de erro
        return Agent(
            id=agent_model.id,
            name=agent_model.name,
            type=agent_model.type,
            isDefault=agent_model.is_default,
            systemPrompt=agent_model.system_prompt,
            tools=[],
            service_id=agent_model.service_id,
            service_status=agent_model.service_status
        )

def agent_pydantic_to_model(agent: Agent, db_agent: AgentModel = None) -> AgentModel:
    """Converte Pydantic para modelo do banco"""
    tools_json = json.dumps([tool.dict() for tool in agent.tools])
    
    if db_agent:
        # Update existing
        db_agent.name = agent.name
        db_agent.type = agent.type
        db_agent.is_default = agent.isDefault
        db_agent.system_prompt = agent.systemPrompt
        db_agent.tools = tools_json
        db_agent.service_id = agent.service_id
        db_agent.service_status = agent.service_status
        db_agent.updated_at = datetime.utcnow()
        return db_agent
    else:
        # Create new
        return AgentModel(
            id=agent.id,
            name=agent.name,
            type=agent.type,
            is_default=agent.isDefault,
            system_prompt=agent.systemPrompt,
            tools=tools_json,
            service_id=agent.service_id,
            service_status=agent.service_status
        )

async def create_service_for_agent(agent: Agent) -> Dict[str, Any]:
    """Chama o Tool Factory para criar um serviço para o agente"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{TOOL_FACTORY_URL}/create-service",
                json={
                    "agent_name": agent.name,
                    "agent_type": agent.type,
                    "tools": [tool.dict() for tool in agent.tools]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao criar serviço: {response.status_code} - {response.text}")
                return {"error": "Falha ao criar serviço"}
                
    except Exception as e:
        logger.error(f"Erro na comunicação com Tool Factory: {e}")
        return {"error": str(e)}

@app.on_event("startup")
async def startup_event():
    """Inicializa dados padrão na startup"""
    try:
        db = SessionLocal()
        init_default_agents(db)
        db.close()
        logger.info("✅ Startup concluído com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro no startup: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-settings-service"}

@app.get("/agents")
async def get_agents(db: Session = Depends(get_db)) -> List[Agent]:
    """Retorna todos os agentes do banco"""
    try:
        agent_models = db.query(AgentModel).order_by(AgentModel.id).all()
        return [agent_model_to_pydantic(agent) for agent in agent_models]
    except Exception as e:
        logger.error(f"Erro ao buscar agentes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: int, db: Session = Depends(get_db)) -> Agent:
    """Retorna um agente específico"""
    agent_model = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not agent_model:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    return agent_model_to_pydantic(agent_model)

@app.post("/agents")
async def create_agent(agent: Agent, db: Session = Depends(get_db)) -> Agent:
    """Cria um novo agente e salva no banco"""
    
    try:
        # Gerar novo ID
        max_id_result = db.query(AgentModel.id).order_by(AgentModel.id.desc()).first()
        agent.id = (max_id_result[0] if max_id_result else 0) + 1
        
        # Agentes customizados não podem ser padrão
        agent.isDefault = False
        agent.service_status = "creating"
        
        # Salvar no banco primeiro
        db_agent = agent_pydantic_to_model(agent)
        db.add(db_agent)
        db.commit()
        db.refresh(db_agent)
        
        logger.info(f"✅ Agente '{agent.name}' criado com ID {agent.id}")
        
        # Depois, criar o serviço se tem ferramentas customizadas
        if agent.tools and any(not tool.apiEndpoint.startswith('/api/calendar') for tool in agent.tools):
            logger.info(f"Criando serviço para agente: {agent.name}")
            
            # Chamar Tool Factory para gerar o serviço
            service_result = await create_service_for_agent(agent)
            
            if "error" not in service_result:
                db_agent.service_id = service_result.get("service_id")
                db_agent.service_status = "created"
                logger.info(f"Serviço criado: {service_result.get('service_name')}")
            else:
                db_agent.service_status = "error"
                logger.error(f"Erro ao criar serviço: {service_result['error']}")
            
            db.commit()
        else:
            # Usa serviços existentes (calendar)
            db_agent.service_status = "using_existing"
            db.commit()
        
        return agent_model_to_pydantic(db_agent)
        
    except Exception as e:
        logger.error(f"Erro ao criar agente: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar agente")

@app.put("/agents/{agent_id}")
async def update_agent(agent_id: int, agent_data: Agent, db: Session = Depends(get_db)) -> Agent:
    """Atualiza um agente"""
    
    db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    # Não permite editar agentes padrão
    if db_agent.is_default:
        raise HTTPException(status_code=400, detail="Não é possível editar agentes padrão")
    
    try:
        agent_data.id = agent_id
        agent_data.isDefault = False
        
        # Se as ferramentas mudaram, recriar o serviço
        old_tools = json.loads(db_agent.tools) if db_agent.tools else []
        new_tools = [tool.dict() for tool in agent_data.tools]
        
        if old_tools != new_tools:
            agent_data.service_status = "updating"
            
            # Recrear serviço
            service_result = await create_service_for_agent(agent_data)
            if "error" not in service_result:
                agent_data.service_id = service_result.get("service_id")
                agent_data.service_status = "updated"
            else:
                agent_data.service_status = "error"
        
        # Atualizar no banco
        updated_agent = agent_pydantic_to_model(agent_data, db_agent)
        db.commit()
        db.refresh(updated_agent)
        
        logger.info(f"✅ Agente {agent_id} atualizado com sucesso")
        return agent_model_to_pydantic(updated_agent)
        
    except Exception as e:
        logger.error(f"Erro ao atualizar agente: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar agente")

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Remove um agente"""
    
    db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    # Não permite deletar agentes padrão
    if db_agent.is_default:
        raise HTTPException(status_code=400, detail="Não é possível deletar agentes padrão")
    
    try:
        # Tentar remover o serviço gerado
        if db_agent.service_id:
            try:
                async with httpx.AsyncClient() as client:
                    await client.delete(f"{TOOL_FACTORY_URL}/services/{db_agent.service_id}")
                    logger.info(f"Serviço {db_agent.service_id} removido")
            except Exception as e:
                logger.warning(f"Erro ao remover serviço: {e}")
        
        db.delete(db_agent)
        db.commit()
        
        logger.info(f"✅ Agente {agent_id} removido com sucesso")
        return {"message": "Agente removido com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro ao deletar agente: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao deletar agente")

@app.post("/agents/{agent_id}/duplicate")
async def duplicate_agent(agent_id: int, db: Session = Depends(get_db)) -> Agent:
    """Duplica um agente existente"""
    
    original_agent_model = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
    if not original_agent_model:
        raise HTTPException(status_code=404, detail="Agente não encontrado")
    
    original_agent = agent_model_to_pydantic(original_agent_model)
    
    # Criar nova instância
    new_agent = Agent(
        name=f"{original_agent.name} - Cópia",
        type=original_agent.type,
        isDefault=False,
        systemPrompt=original_agent.systemPrompt,
        tools=original_agent.tools.copy()
    )
    
    # Usar a função create_agent para gerar o serviço
    return await create_agent(new_agent, db)

@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Retorna estatísticas dos agentes"""
    
    try:
        total_agents = db.query(AgentModel).count()
        default_agents = db.query(AgentModel).filter(AgentModel.is_default == True).count()
        custom_agents = total_agents - default_agents
        active_services = db.query(AgentModel).filter(AgentModel.service_status == "active").count()
        
        pessoal_agents = db.query(AgentModel).filter(AgentModel.type == "Pessoal").count()
        profissional_agents = db.query(AgentModel).filter(AgentModel.type == "Profissional").count()
        
        return {
            "total_agents": total_agents,
            "default_agents": default_agents,
            "custom_agents": custom_agents,
            "active_services": active_services,
            "agents_by_type": {
                "Pessoal": pessoal_agents,
                "Profissional": profissional_agents
            }
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)