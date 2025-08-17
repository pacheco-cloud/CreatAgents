# test_database.py - Script para testar a configuração do banco

import sys
import os
from sqlalchemy import text

# Adicionar o caminho do serviço ao Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'apps', 'services', 'user-settings-service'))

try:
    from database import SessionLocal, engine, AgentModel, test_connection, create_tables
    print("✅ Importações do banco realizadas com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar módulos do banco: {e}")
    print("📝 Certifique-se de que está na pasta raiz do projeto")
    sys.exit(1)

def test_database_operations():
    """Testa operações básicas do banco de dados"""
    
    print("\n🧪 Iniciando testes do banco de dados...")
    
    # 1. Testar conexão
    print("\n1️⃣ Testando conexão...")
    if not test_connection():
        print("❌ Falha na conexão com o banco")
        return False
    
    # 2. Criar tabelas
    print("\n2️⃣ Criando tabelas...")
    try:
        create_tables()
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False
    
    # 3. Testar inserção
    print("\n3️⃣ Testando inserção de dados...")
    db = SessionLocal()
    try:
        # Criar agente de teste
        test_agent = AgentModel(
            name="Agente de Teste",
            type="Pessoal",
            system_prompt="Este é um agente de teste para verificar a funcionalidade do banco",
            tools=[{
                "name": "ferramenta_teste",
                "description": "Ferramenta de teste",
                "apiEndpoint": "/api/test",
                "parameters": [{"name": "param1", "type": "texto"}]
            }],
            is_default=False
        )
        
        db.add(test_agent)
        db.commit()
        db.refresh(test_agent)
        
        print(f"✅ Agente criado com ID: {test_agent.id}")
        
        # 4. Testar consulta
        print("\n4️⃣ Testando consulta de dados...")
        agents = db.query(AgentModel).all()
        print(f"✅ Encontrados {len(agents)} agentes no banco")
        
        for agent in agents:
            print(f"   - {agent.name} ({agent.type}) - Default: {agent.is_default}")
        
        # 5. Testar atualização
        print("\n5️⃣ Testando atualização de dados...")
        test_agent.name = "Agente de Teste Atualizado"
        db.commit()
        print("✅ Agente atualizado com sucesso!")
        
        # 6. Testar deleção
        print("\n6️⃣ Testando deleção de dados...")
        db.delete(test_agent)
        db.commit()
        print("✅ Agente deletado com sucesso!")
        
        # 7. Verificar estrutura das tabelas
        print("\n7️⃣ Verificando estrutura das tabelas...")
        result = db.execute(text("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name IN ('agents', 'tools')
            ORDER BY table_name, ordinal_position
        """))
        
        print("📋 Estrutura das tabelas:")
        current_table = None
        for row in result:
            if row.table_name != current_table:
                print(f"\n📁 Tabela: {row.table_name}")
                current_table = row.table_name
            print(f"   - {row.column_name}: {row.data_type}")
        
        print("\n✅ Todos os testes passaram com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_api_endpoints():
    """Testa os endpoints da API usando requests"""
    print("\n🌐 Testando endpoints da API...")
    
    try:
        import requests
        
        base_url = "http://localhost:8003"
        
        # Testar health check
        print("\n🏥 Testando health check...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passou!")
            print(f"📊 Resposta: {response.json()}")
        else:
            print(f"❌ Health check falhou: {response.status_code}")
        
        # Testar listagem de agentes
        print("\n📋 Testando listagem de agentes...")
        response = requests.get(f"{base_url}/agents", timeout=5)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Encontrados {len(agents)} agentes via API")
            for agent in agents:
                print(f"   - {agent['name']} ({agent['type']})")
        else:
            print(f"❌ Falha ao listar agentes: {response.status_code}")
        
        # Testar estatísticas
        print("\n📊 Testando estatísticas...")
        response = requests.get(f"{base_url}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Estatísticas obtidas:")
            for key, value in stats.items():
                print(f"   - {key}: {value}")
        else:
            print(f"❌ Falha ao obter estatísticas: {response.status_code}")
            
        return True
        
    except requests.RequestException as e:
        print(f"❌ Erro de conexão com a API: {e}")
        print("📝 Certifique-se de que o serviço está rodando em http://localhost:8003")
        return False
    except ImportError:
        print("❌ Biblioteca 'requests' não encontrada")
        print("📝 Instale com: pip install requests")
        return False

def main():
    """Função principal do teste"""
    print("🧪 TESTE COMPLETO DO BANCO DE DADOS POSTGRESQL")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print(f"🔗 URL do banco: {database_url}")
    else:
        print("⚠️  Variável DATABASE_URL não encontrada no .env")
    
    # Executar testes
    database_success = test_database_operations()
    
    print("\n" + "=" * 50)
    
    if database_success:
        print("🎉 TODOS OS TESTES DO BANCO PASSARAM!")
        
        # Testar API se solicitado
        test_api = input("\n🤔 Deseja testar os endpoints da API também? (y/n): ").lower().strip()
        if test_api in ['y', 'yes', 's', 'sim']:
            api_success = test_api_endpoints()
            if api_success:
                print("\n🚀 TESTES DA API TAMBÉM PASSARAM!")
            else:
                print("\n⚠️  Alguns testes da API falharam")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("\n🔧 Passos para resolver:")
        print("1. Verifique se o PostgreSQL está rodando")
        print("2. Confirme as credenciais no arquivo .env")
        print("3. Execute o script setup_postgres.sh")
        print("4. Instale as dependências: pip install -r requirements.txt")

if __name__ == "__main__":
    main()