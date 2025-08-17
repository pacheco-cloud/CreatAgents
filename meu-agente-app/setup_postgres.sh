#!/bin/bash
# setup_postgres.sh - Script para configurar PostgreSQL localmente

set -e

echo "🐘 Configurando PostgreSQL para o projeto..."

# Detectar SO
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS="windows"
else
    echo "❌ Sistema operacional não suportado: $OSTYPE"
    exit 1
fi

echo "🔍 Sistema detectado: $OS"

# Função para instalar PostgreSQL no Linux
install_postgres_linux() {
    echo "📦 Instalando PostgreSQL no Linux..."
    
    # Ubuntu/Debian
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y postgresql postgresql-contrib
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    
    # CentOS/RHEL/Fedora
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y postgresql postgresql-server postgresql-contrib
        sudo postgresql-setup --initdb
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    
    # Arch Linux
    elif command -v pacman &> /dev/null; then
        sudo pacman -S postgresql
        sudo -u postgres initdb -D /var/lib/postgres/data
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    
    else
        echo "❌ Gerenciador de pacotes não suportado"
        echo "📝 Instale o PostgreSQL manualmente: https://www.postgresql.org/download/linux/"
        exit 1
    fi
}

# Função para instalar PostgreSQL no macOS
install_postgres_macos() {
    echo "📦 Instalando PostgreSQL no macOS..."
    
    if command -v brew &> /dev/null; then
        brew install postgresql@15
        brew services start postgresql@15
        echo "✅ PostgreSQL instalado via Homebrew"
    else
        echo "❌ Homebrew não encontrado"
        echo "📝 Instale o Homebrew: https://brew.sh/"
        echo "📝 Ou baixe PostgreSQL: https://www.postgresql.org/download/macosx/"
        exit 1
    fi
}

# Função para instalar PostgreSQL no Windows
install_postgres_windows() {
    echo "📦 Para Windows, baixe o instalador oficial:"
    echo "🔗 https://www.postgresql.org/download/windows/"
    echo "📝 Ou use o Chocolatey: choco install postgresql"
    echo "📝 Ou use o Scoop: scoop install postgresql"
    exit 1
}

# Verificar se PostgreSQL já está instalado
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL já está instalado!"
    POSTGRES_VERSION=$(psql --version | awk '{print $3}')
    echo "📋 Versão: $POSTGRES_VERSION"
else
    echo "❌ PostgreSQL não encontrado, instalando..."
    
    case $OS in
        linux)
            install_postgres_linux
            ;;
        macos)
            install_postgres_macos
            ;;
        windows)
            install_postgres_windows
            ;;
    esac
fi

# Configurar banco de dados e usuário
echo "🔧 Configurando banco de dados..."

# Comandos SQL para criar usuário e banco
SQL_COMMANDS="
CREATE USER agente_user WITH PASSWORD 'agente_pass';
CREATE DATABASE agente_db OWNER agente_user;
GRANT ALL PRIVILEGES ON DATABASE agente_db TO agente_user;
ALTER USER agente_user CREATEDB;
"

# Executar comandos como usuário postgres
if [[ "$OS" == "linux" ]]; then
    sudo -u postgres psql -c "$SQL_COMMANDS" || {
        echo "⚠️  Erro ao criar banco. Tentando método alternativo..."
        echo "$SQL_COMMANDS" | sudo -u postgres psql
    }
elif [[ "$OS" == "macos" ]]; then
    psql postgres -c "$SQL_COMMANDS" || {
        echo "⚠️  Erro ao criar banco. Tentando com createdb..."
        createuser agente_user || echo "Usuário já existe"
        createdb agente_db -O agente_user || echo "Banco já existe"
    }
fi

# Testar conexão
echo "🧪 Testando conexão..."
if PGPASSWORD=agente_pass psql -h localhost -U agente_user -d agente_db -c "SELECT 1;" &> /dev/null; then
    echo "✅ Conexão com PostgreSQL estabelecida com sucesso!"
else
    echo "❌ Falha na conexão. Verifique as configurações."
    echo "🔧 Comandos manuais para configurar:"
    echo "   sudo -u postgres createuser agente_user"
    echo "   sudo -u postgres createdb agente_db -O agente_user"
    echo "   sudo -u postgres psql -c \"ALTER USER agente_user WITH PASSWORD 'agente_pass';\""
    exit 1
fi

# Configurar pg_hba.conf para permitir conexões locais (se necessário)
echo "🔐 Verificando configurações de autenticação..."

# Localizar pg_hba.conf
PG_HBA_PATH=""
if [[ "$OS" == "linux" ]]; then
    PG_HBA_PATH=$(sudo -u postgres psql -t -P format=unaligned -c 'SHOW hba_file;' 2>/dev/null || echo "")
elif [[ "$OS" == "macos" ]]; then
    PG_HBA_PATH=$(psql postgres -t -P format=unaligned -c 'SHOW hba_file;' 2>/dev/null || echo "")
fi

if [[ -n "$PG_HBA_PATH" && -f "$PG_HBA_PATH" ]]; then
    echo "📁 Arquivo pg_hba.conf encontrado: $PG_HBA_PATH"
    
    # Verificar se configuração local já existe
    if grep -q "local.*agente_db.*agente_user.*md5" "$PG_HBA_PATH"; then
        echo "✅ Configuração de autenticação já está correta"
    else
        echo "⚠️  Pode ser necessário configurar pg_hba.conf manualmente"
        echo "📝 Adicione esta linha ao arquivo $PG_HBA_PATH:"
        echo "local   agente_db   agente_user   md5"
    fi
else
    echo "⚠️  Não foi possível localizar pg_hba.conf automaticamente"
fi

echo ""
echo "🎉 Configuração do PostgreSQL concluída!"
echo ""
echo "📋 Informações da conexão:"
echo "   Host: localhost"
echo "   Porta: 5432"
echo "   Banco: agente_db"
echo "   Usuário: agente_user"
echo "   Senha: agente_pass"
echo ""
echo "🔗 URL de conexão:"
echo "   postgresql://agente_user:agente_pass@localhost:5432/agente_db"
echo ""
echo "🚀 Próximos passos:"
echo "   1. Instale as dependências Python: pip install -r requirements.txt"
echo "   2. Configure o arquivo .env com as variáveis do banco"
echo "   3. Execute o serviço: python apps/services/user-settings-service/main.py"
echo ""