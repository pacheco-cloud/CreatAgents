from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, timezone
import json
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/agente_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo do Agente
class AgentModel(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    system_prompt = Column(Text)
    tools = Column(Text)
    is_default = Column(Boolean, default=False)
    service_status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))

# Dependência para obter sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para inicializar agentes padrão
def init_default_agents():
    db = SessionLocal()
    try:
        # Verificar se já existem agentes
        existing_agents = db.query(AgentModel).count()
        if existing_agents > 0:
            logger.info("Agentes já existem no banco de dados")
            return
        
        logger.info("Criando agentes padrão...")
        
        # Ferramentas disponíveis (atualmente desativadas para o agente de conhecimento geral)
        # O orquestrador pode usar essas ferramentas quando necessário
        available_tools = {
            "calendar_tools": [
                {
                    "name": "consultar_agenda",
                    "description": "Consulta eventos na agenda do usuário",
                    "apiEndpoint": "/api/calendar/all",
                    "parameters": [
                        {"name": "data_inicio", "type": "data"},
                        {"name": "data_fim", "type": "data"}
                    ]
                },
                {
                    "name": "criar_evento",
                    "description": "Cria um novo evento na agenda",
                    "apiEndpoint": "/api/calendar/create",
                    "parameters": [
                        {"name": "titulo", "type": "string"},
                        {"name": "data_inicio", "type": "data"},
                        {"name": "data_fim", "type": "data"},
                        {"name": "descricao", "type": "string"}
                    ]
                }
            ]
        }
        
        # Criar agente de conhecimento geral
        general_agent = AgentModel(
            id=1,
            name="Assistente Geral",
            type="Conhecimento Geral",
            is_default=True,
            system_prompt="""Você é um assistente de IA de conhecimento geral, como ChatGPT, Gemini ou Claude. 

Suas capacidades incluem:
- Responder perguntas sobre qualquer tópico
- Ajudar com tarefas de escrita e criação de conteúdo
- Resolver problemas e dar explicações
- Fornecer análises e insights
- Auxiliar em pesquisas e estudos
- Conversar sobre diversos assuntos

Seja útil, preciso e amigável. Quando não souber algo, seja honesto sobre suas limitações. 
Se o usuário precisar de funcionalidades específicas como agenda ou outros serviços, 
informe que essas funcionalidades podem ser acessadas através do orquestrador do sistema.""",
            tools=json.dumps([]),  # Sem ferramentas específicas - é um agente de conversa geral
            service_status="active"
        )
        
        db.add(general_agent)
        db.commit()
        logger.info("✅ Agente de conhecimento geral criado com sucesso!")
        logger.info("📝 Ferramentas de agenda mantidas disponíveis para o orquestrador")
        
    except Exception as e:
        logger.error(f"Erro ao criar agentes padrão: {e}")
        db.rollback()
    finally:
        db.close()

# Criação da aplicação FastAPI
app = FastAPI(title="User Settings Service", version="1.0.0")

# Classe Pydantic para resposta do agente
from pydantic import BaseModel
from typing import List, Optional

class AgentResponse(BaseModel):
    id: int
    name: str
    type: str
    system_prompt: str
    tools: str
    is_default: bool
    service_status: str

    class Config:
        from_attributes = True

# Criar tabelas no banco de dados
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup_event():
    init_default_agents()

@app.get("/")
async def read_root():
    return {"message": "User Settings Service is running"}

@app.get("/agents", response_model=List[AgentResponse])
async def get_agents(db: Session = Depends(get_db)):
    try:
        agents = db.query(AgentModel).all()
        return agents
    except Exception as e:
        logger.error(f"Erro ao buscar agentes: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    try:
        agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agente não encontrado")
        return agent
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar agente {agent_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
