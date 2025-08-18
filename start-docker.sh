#!/bin/bash
# start-docker.sh - Script para iniciar o projeto com Docker

set -e

echo "🐳 INICIANDO PROJETO COM DOCKER"
echo "================================"

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado!"
    echo "📝 Instale Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado!"
    echo "📝 Instale Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Verificar se Docker está rodando
if ! docker info &> /dev/null; then
    echo "❌ Docker não está rodando!"
    echo "📝 Inicie o Docker Desktop ou o daemon do Docker"
    exit 1
fi

echo "✅ Docker está disponível e rodando!"

# Verificar se arquivo .env existe
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo "⚠️  Configure sua chave OpenAI no arquivo .env antes de continuar!"
    echo "   OPENAI_API_KEY=sk-your-key-here"
    read -p "Pressione Enter após configurar a chave OpenAI..."
fi

# Verificar se a chave OpenAI está configurada
if grep -q "your_openai_api_key_here" .env; then
    echo "❌ Configure sua chave da OpenAI no arquivo .env!"
    echo "   Edite OPENAI_API_KEY=your_openai_api_key_here"
    exit 1
fi

echo "✅ Arquivo .env configurado!"

# Limpar containers anteriores se existirem
echo "🧹 Limpando containers anteriores..."
docker-compose down --remove-orphans 2>/dev/null || true

# Construir e iniciar serviços
echo "🏗️ Construindo e iniciando serviços..."
echo "⏳ Este processo pode demorar alguns minutos na primeira execução..."

# Iniciar apenas banco e cache primeiro
echo "🗄️ Iniciando banco de dados e cache..."
docker-compose up -d postgres redis

# Aguardar banco estar pronto
echo "⏳ Aguardando banco de dados..."
timeout 60 bash -c 'until docker-compose exec postgres pg_isready -U agente_user -d agente_db; do sleep 2; done'

if [ $? -eq 0 ]; then
    echo "✅ Banco de dados está pronto!"
else
    echo "❌ Timeout aguardando banco de dados"
    docker-compose logs postgres
    exit 1
fi

# Iniciar serviços backend
echo "🔧 Iniciando serviços backend..."
docker-compose up -d user-settings-service calendar-service

# Aguardar serviços backend
echo "⏳ Aguardando serviços backend..."
sleep 10

# Verificar se serviços estão saudáveis
echo "🏥 Verificando saúde dos serviços..."
for service in user-settings-service calendar-service; do
    if docker-compose ps | grep $service | grep -q "Up"; then
        echo "✅ $service está rodando"
    else
        echo "❌ $service falhou ao iniciar"
        docker-compose logs $service
        exit 1
    fi
done

# Iniciar orquestrador
echo "🤖 Iniciando orquestrador..."
docker-compose up -d orchestrator-agent tool-factory-service

# Aguardar orquestrador
sleep 5

# Iniciar API Gateway
echo "🌐 Iniciando API Gateway..."
docker-compose up -d api-gateway

# Aguardar API Gateway
sleep 5

# Verificar API Gateway
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ API Gateway está respondendo!"
else
    echo "❌ API Gateway não está respondendo"
    docker-compose logs api-gateway
    exit 1
fi

# Iniciar Frontend
echo "🎨 Iniciando Frontend..."
docker-compose up -d frontend

# Aguardar Frontend
echo "⏳ Aguardando Frontend..."
sleep 15

# Verificar Frontend
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Frontend está respondendo!"
else
    echo "⚠️ Frontend pode ainda estar iniciando..."
fi

# Mostrar status final
echo ""
echo "🎉 PROJETO INICIADO COM SUCESSO!"
echo "================================"
echo ""
echo "🌐 URLs disponíveis:"
echo "   Frontend:     http://localhost:3000"
echo "   API Gateway:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Settings:     http://localhost:3000/settings"
echo ""
echo "🐳 Containers rodando:"
docker-compose ps
echo ""
echo "📋 Comandos úteis:"
echo "   Ver logs:           docker-compose logs -f"
echo "   Parar tudo:         docker-compose down"
echo "   Reiniciar:          docker-compose restart"
echo "   Status:             docker-compose ps"
echo "   Logs específicos:   docker-compose logs -f [service-name]"
echo ""
echo "🔧 Para desenvolvimento:"
echo "   make docker-logs    # Ver todos os logs"
echo "   make docker-stop    # Parar containers"
echo "   make docker-clean   # Limpar tudo"
echo ""

# Oferecer para mostrar logs
read -p "🤔 Deseja ver os logs em tempo real? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📋 Mostrando logs (Ctrl+C para sair)..."
    docker-compose logs -f
fi