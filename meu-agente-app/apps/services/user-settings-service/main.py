# apps/services/user-settings-service/database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, JSON, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import time
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL - Docker compatible
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://agente_user:agente_pass@postgres:5432/agente_db"  # Docker service name
)

logger.info(f"Database URL: {DATABASE_URL}")

# SQLAlchemy configuration
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Agent Model
class AgentModel(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(String(20), nullable=False)
    system_prompt = Column(Text, nullable=False)
    tools = Column(JSON, nullable=True, default=list)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.type}')>"

# Tool Model
class ToolModel(Base):
    __tablename__ = "tools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    api_endpoint = Column(String(200), nullable=False)
    parameters = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Tool(id={self.id}, name='{self.name}')>"

def wait_for_db(max_retries=30, delay=2):
    """Wait for database to be available"""
    for attempt in range(max_retries):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("✅ Database connection established!")
            return True
        except Exception as e:
            logger.warning(f"⏳ Database not ready (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                logger.error("❌ Database connection failed after all retries")
                return False
    return False

def create_tables():
    """Create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("✅ Database connection test passed!")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False

def initialize_database():
    """Initialize database with retry logic"""
    logger.info("🔧 Initializing database...")
    
    # Wait for database to be available
    if not wait_for_db():
        raise Exception("Database is not available")
    
    # Create tables
    if not create_tables():
        raise Exception("Failed to create tables")
    
    # Test connection
    if not test_connection():
        raise Exception("Database connection test failed")
    
    logger.info("✅ Database initialized successfully!")

def create_default_agents():
    """Create default agents if they don't exist"""
    db = SessionLocal()
    try:
        # Check if default agents already exist
        existing_defaults = db.query(AgentModel).filter(AgentModel.is_default == True).count()
        
        if existing_defaults == 0:
            logger.info("📝 Creating default agents...")
            
            # Personal agent
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
            
            # Professional agent
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
            
            logger.info("✅ Default agents created successfully!")
        else:
            logger.info(f"ℹ️ Default agents already exist ({existing_defaults} found)")
            
    except Exception as e:
        logger.error(f"❌ Error creating default agents: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Initialize database when module is run directly
    initialize_database()
    create_default_agents()