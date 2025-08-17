# apps/services/user-settings-service/database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, JSON, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from typing import Optional

# URL de conexão com PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://agente_user:agente_pass@localhost:5432/agente_db"
)

# Configuração do SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)  # Mudei para False para menos verbosidade
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency para obter sessão do banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelo da tabela de Agentes
class AgentModel(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(String(20), nullable=False)  # 'Pessoal' ou 'Profissional'
    system_prompt = Column(Text, nullable=False)
    tools = Column(JSON, nullable=True, default=list)  # PostgreSQL suporte JSON nativo
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.type}')>"

# Modelo da tabela de Ferramentas (para normalização futura)
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

# Função para criar todas as tabelas
def create_tables():
    """Cria todas as tabelas no banco de dados"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

# Função para verificar conexão - CORRIGIDA para SQLAlchemy 2.0
def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        # Usar a sintaxe correta do SQLAlchemy 2.0
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()  # Consumir o resultado
        print("✅ Conexão com PostgreSQL estabelecida!")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

# Função adicional para verificar se o banco existe
def check_database_exists():
    """Verifica se o banco de dados existe"""
    try:
        # Extrair informações da URL
        from urllib.parse import urlparse
        parsed = urlparse(DATABASE_URL)
        
        # URL para conexão com postgres (banco padrão)
        admin_url = f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/postgres"
        admin_engine = create_engine(admin_url)
        
        with admin_engine.connect() as connection:
            result = connection.execute(text("SELECT 1 FROM pg_database WHERE datname = :dbname"), 
                                      {"dbname": parsed.path[1:]})  # Remove '/' do path
            exists = result.fetchone() is not None
            
        if exists:
            print(f"✅ Banco de dados '{parsed.path[1:]}' existe!")
        else:
            print(f"❌ Banco de dados '{parsed.path[1:]}' não existe!")
            
        return exists
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

# Função para verificar se o usuário existe
def check_user_exists():
    """Verifica se o usuário do banco existe"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(DATABASE_URL)
        
        admin_url = f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/postgres"
        admin_engine = create_engine(admin_url)
        
        with admin_engine.connect() as connection:
            result = connection.execute(text("SELECT 1 FROM pg_user WHERE usename = :username"), 
                                      {"username": parsed.username})
            exists = result.fetchone() is not None
            
        if exists:
            print(f"✅ Usuário '{parsed.username}' existe!")
        else:
            print(f"❌ Usuário '{parsed.username}' não existe!")
            
        return exists
        
    except Exception as e:
        print(f"❌ Erro ao verificar usuário: {e}")
        return False

# Função de diagnóstico completo
def diagnose_connection():
    """Faz diagnóstico completo da conexão"""
    print("🔍 Iniciando diagnóstico da conexão PostgreSQL...")
    
    from urllib.parse import urlparse
    parsed = urlparse(DATABASE_URL)
    
    print(f"📋 Configuração:")
    print(f"   Host: {parsed.hostname}")
    print(f"   Porta: {parsed.port}")
    print(f"   Banco: {parsed.path[1:]}")
    print(f"   Usuário: {parsed.username}")
    
    # Verificar se PostgreSQL está rodando
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            user=parsed.username,
            password=parsed.password,
            database="postgres"  # Conectar ao banco padrão primeiro
        )
        conn.close()
        print("✅ PostgreSQL está rodando!")
        
        # Verificar usuário
        check_user_exists()
        
        # Verificar banco
        check_database_exists()
        
        # Testar conexão final
        return test_connection()
        
    except ImportError:
        print("❌ psycopg2 não está instalado")
        print("📝 Execute: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL não está acessível: {e}")
        print("📝 Execute: brew services start postgresql@15")  # Para macOS
        return False

if __name__ == "__main__":
    # Script para testar a configuração
    print("🔧 Testando configuração do banco...")
    
    if test_connection():
        create_tables()
    else:
        print("\n🔍 Executando diagnóstico completo...")
        diagnose_connection()