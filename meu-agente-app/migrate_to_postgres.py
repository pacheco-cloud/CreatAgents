# migrate_to_postgres.py - Script para migrar dados existentes para PostgreSQL

import sys
import os
import json
from datetime import datetime
from sqlalchemy import text

# Adicionar caminho do serviço
sys.path.append(os.path.join(os.path.dirname(__file__), 'apps', 'services', 'user-settings-service'))

try:
    from database import SessionLocal, AgentModel, create_tables, test_connection, diagnose_connection
    print("✅ Módulos de banco importados com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("📝 Certifique-se de que:")
    print("   1. Está na pasta raiz do projeto")
    print("   2. Instalou as dependências: pip install -r requirements.txt")
    print("   3. O arquivo database.py existe em apps/services/user-settings-service/")
    sys.exit(1)

# Dados padrão que estavam em memória (do seu código original)
DEFAULT_AGENTS_DATA = [
    {
        "id": 1,
        "name": "Calendário Pessoal",
        "type": "Pessoal",
        "isDefault": True,
        "systemPrompt": "Você é um assistente de agenda pessoal. Ajude com compromissos pessoais, eventos familiares e atividades de lazer.",
        "tools": [{
            "name": "consultar_agenda_pessoal",
            "description": "Consulta eventos na agenda pessoal do usuário",
            "apiEndpoint": "/api/calendar/personal",
            "parameters": [
                {"name": "data_inicio", "type": "data"},
                {"name": "data_fim", "type": "data"}
            ]
        }]
    },
    {
        "id": 2,
        "name": "Calendário Profissional",
        "type": "Profissional",
        "isDefault": True,
        "systemPrompt": "Você é um assistente de agenda profissional. Ajude com reuniões, projetos e compromissos de trabalho.",
        "tools": [{
            "name": "consultar_agenda_profissional",
            "description": "Consulta eventos na agenda profissional do usuário",
            "apiEndpoint": "/api/calendar/professional",
            "parameters": [
                {"name": "data_inicio", "type": "data"},
                {"name": "data_fim", "type": "data"}
            ]
        }]
    }
]

def load_existing_data():
    """Carrega dados existentes de arquivo JSON se existir"""
    json_file = "agents_backup.json"
    
    if os.path.exists(json_file):
        print(f"📄 Encontrado arquivo de backup: {json_file}")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ Carregados {len(data)} agentes do backup")
            return data
        except Exception as e:
            print(f"❌ Erro ao ler backup: {e}")
    
    return None

def backup_current_data():
    """Faz backup dos dados atuais do banco (se existirem)"""
    print("\n💾 Fazendo backup dos dados existentes...")
    
    db = SessionLocal()
    try:
        agents = db.query(AgentModel).all()
        if agents:
            backup_data = []
            for agent in agents:
                backup_data.append({
                    "id": agent.id,
                    "name": agent.name,
                    "type": agent.type,
                    "isDefault": agent.is_default,
                    "systemPrompt": agent.system_prompt,
                    "tools": agent.tools or [],
                    "created_at": agent.created_at.isoformat() if agent.created_at else None,
                    "updated_at": agent.updated_at.isoformat() if agent.updated_at else None
                })
            
            backup_file = f"agents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Backup salvo em: {backup_file}")
            return True
        else:
            print("ℹ️  Nenhum dado existente para fazer backup")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao fazer backup: {e}")
        return False
    finally:
        db.close()

def migrate_data(data_source="default"):
    """Migra dados para PostgreSQL"""
    print(f"\n🚀 Iniciando migração de dados ({data_source})...")
    
    db = SessionLocal()
    try:
        # Determinar fonte dos dados
        if data_source == "default":
            agents_data = DEFAULT_AGENTS_DATA
            print("📋 Usando dados padrão do sistema")
        elif data_source == "backup":
            agents_data = load_existing_data()
            if not agents_data:
                print("❌ Nenhum backup encontrado, usando dados padrão")
                agents_data = DEFAULT_AGENTS_DATA
        else:
            print("❌ Fonte de dados inválida")
            return False
        
        # Verificar se já existem dados
        existing_count = db.query(AgentModel).count()
        if existing_count > 0:
            print(f"⚠️  Já existem {existing_count} agentes no banco")
            overwrite = input("Deseja sobrescrever? (y/n): ").lower().strip()
            if overwrite not in ['y', 'yes', 's', 'sim']:
                print("❌ Migração cancelada pelo usuário")
                return False
            
            # Fazer backup antes de sobrescrever
            backup_current_data()
            
            # Limpar dados existentes
            db.query(AgentModel).delete()
            db.commit()
            print("🗑️  Dados existentes removidos")
        
        # Inserir novos dados
        migrated_count = 0
        for agent_data in agents_data:
            try:
                # Converter dados para o modelo do banco
                db_agent = AgentModel(
                    name=agent_data["name"],
                    type=agent_data["type"],
                    system_prompt=agent_data["systemPrompt"],
                    tools=agent_data["tools"],
                    is_default=agent_data.get("isDefault", False)
                )
                
                db.add(db_agent)
                migrated_count += 1
                
            except Exception as e:
                print(f"❌ Erro ao migrar agente '{agent_data.get('name', 'Desconhecido')}': {e}")
                continue
        
        # Salvar todas as alterações
        db.commit()
        print(f"✅ {migrated_count} agentes migrados com sucesso!")
        
        # Verificar dados migrados
        total_agents = db.query(AgentModel).count()
        print(f"📊 Total de agentes no banco: {total_agents}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def verify_migration():
    """Verifica se a migração foi bem-sucedida"""
    print("\n🔍 Verificando migração...")
    
    db = SessionLocal()
    try:
        agents = db.query(AgentModel).all()
        
        print(f"📊 Agentes encontrados: {len(agents)}")
        for agent in agents:
            print(f"   ✓ {agent.name} ({agent.type})")
            if agent.tools:
                print(f"     - {len(agent.tools)} ferramenta(s) configurada(s)")
        
        # Verificar integridade dos dados
        issues = []
        for agent in agents:
            if not agent.name or not agent.name.strip():
                issues.append(f"Agente ID {agent.id} sem nome")
            if agent.type not in ["Pessoal", "Profissional"]:
                issues.append(f"Agente '{agent.name}' com tipo inválido: {agent.type}")
            if not agent.system_prompt or not agent.system_prompt.strip():
                issues.append(f"Agente '{agent.name}' sem system prompt")
        
        if issues:
            print("\n⚠️  Problemas encontrados:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("\n✅ Migração verificada com sucesso!")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar migração: {e}")
        return False
    finally:
        db.close()

def check_postgresql_status():
    """Verifica o status do PostgreSQL no macOS"""
    print("\n🔍 Verificando status do PostgreSQL...")
    
    try:
        import subprocess
        
        # Verificar se PostgreSQL está rodando (macOS com Homebrew)
        result = subprocess.run(['brew', 'services', 'list'], 
                              capture_output=True, text=True, timeout=10)
        
        if 'postgresql' in result.stdout:
            if 'started' in result.stdout:
                print("✅ PostgreSQL está rodando via Homebrew")
                return True
            else:
                print("❌ PostgreSQL está instalado mas não está rodando")
                print("📝 Execute: brew services start postgresql@15")
                return False
        else:
            print("❌ PostgreSQL não encontrado via Homebrew")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout ao verificar serviços")
        return False
    except FileNotFoundError:
        print("⚠️  Homebrew não encontrado")
        return False
    except Exception as e:
        print(f"⚠️  Erro ao verificar status: {e}")
        return False

def main():
    """Função principal da migração"""
    print("🔄 MIGRAÇÃO PARA POSTGRESQL")
    print("=" * 40)
    
    # Verificar se PostgreSQL está rodando
    print("\n0️⃣ Verificando PostgreSQL...")
    if not check_postgresql_status():
        print("📝 Iniciando PostgreSQL...")
        try:
            import subprocess
            subprocess.run(['brew', 'services', 'start', 'postgresql@15'], 
                         capture_output=True, timeout=15)
            print("✅ PostgreSQL iniciado!")
        except:
            print("❌ Não foi possível iniciar PostgreSQL automaticamente")
            print("📝 Execute manualmente: brew services start postgresql@15")
            return
    
    # Verificar conexão
    print("\n1️⃣ Verificando conexão com PostgreSQL...")
    if not test_connection():
        print("🔍 Executando diagnóstico...")
        if not diagnose_connection():
            print("❌ Falha na conexão. Verifique a configuração do PostgreSQL")
            print("\n🔧 Passos para resolver:")
            print("1. Instalar PostgreSQL: brew install postgresql@15")
            print("2. Iniciar serviço: brew services start postgresql@15")
            print("3. Criar usuário e banco: Execute o script setup_postgres.sh")
            return
    
    # Criar tabelas
    print("\n2️⃣ Criando estrutura do banco...")
    if not create_tables():
        print("❌ Erro ao criar tabelas")
        return
    
    # Escolher fonte dos dados
    print("\n3️⃣ Escolha a fonte dos dados:")
    print("1. Dados padrão do sistema (recomendado)")
    print("2. Arquivo de backup (se existir)")
    
    choice = input("\nEscolha (1 ou 2): ").strip()
    
    data_source = "default" if choice == "1" else "backup"
    
    # Executar migração
    print(f"\n4️⃣ Executando migração...")
    if migrate_data(data_source):
        # Verificar migração
        print("\n5️⃣ Verificando migração...")
        if verify_migration():
            print("\n🎉 MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("\n📝 Próximos passos:")
            print("1. Execute o serviço: python apps/services/user-settings-service/main.py")
            print("2. Teste a API: python test_database.py")
            print("3. Acesse http://localhost:3000/settings para ver os agentes")
        else:
            print("\n❌ Migração com problemas. Verifique os dados.")
    else:
        print("\n❌ Falha na migração.")

if __name__ == "__main__":
    main()