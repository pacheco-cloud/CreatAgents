#!/bin/bash
# start-docker.sh - Script para iniciar o projeto com Docker (compatível com macOS)

set -e

echo "🐳 INICIANDO PROJETO COM DOCKER"
echo "================================"

# Função para aguardar com timeout manual (compatível com macOS)
wait_with_timeout() {
    local timeout_duration=$1
    local command_to_run="$2"
    local description="$3"
    
    echo "⏳ $description..."
    
    local count=0
    while [ $count -lt $timeout_duration ]; do
        if eval "$command_to_run" >/dev/null 2>&1; then
            echo "✅ $description concluído!"
            return 0
        fi
        sleep 2
        count=$((count + 2))
        if [ $((count % 10)) -eq 0 ]; then
            echo "   Aguardando... ($count/${timeout_duration}s)"
        fi
    done
    
    echo "❌ Timeout após ${timeout_duration}s para: $description"
    return 1
}

# Função para testar health check com menos tentativas
test_service_health() {
    local service_url=$1
    local service_name=$2
    local max_attempts=3
    local attempt=1
    
    echo "⏳ Testando $service_name..."
    
    while [ $attempt -le $max_attempts ]; do
        echo "   Tentativa $attempt/$max_attempts para $service_name..."
        
        if curl -f --connect-timeout 5 --max-time 10 "$service_url" >/dev/null 2>&1; then
            echo "✅ $service_name está respondendo!"
            return 0
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            sleep 3
        fi
        
        ((attempt++))
    done
    
    echo "❌ $service_name não está respondendo após $max_attempts tentativas"
    return 1
}

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

# Aguardar banco estar pronto (sem comando timeout)
if wait_with_timeout 60 "docker-compose exec postgres pg_isready -U agente_user -d agente_db" "Aguardando banco de dados"; then
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
echo "⏳ Aguardando serviços backend inicializarem..."
sleep 5

# Verificar se serviços estão rodando (método simplificado)
echo "🏥 Verificando saúde dos serviços backend..."
sleep 3

# Verificar se containers estão up
for service in user-settings-service calendar-service; do
    if docker-compose ps | grep $service | grep -q "Up"; then
        echo "✅ $service está rodando"
    else
        echo "❌ $service falhou ao iniciar"
        echo "📋 Logs do $service:"
        docker-compose logs $service
        exit 1
    fi
done

# Iniciar orquestrador
echo "🤖 Iniciando orquestrador e tool factory..."
docker-compose up -d orchestrator-agent tool-factory-service

# Aguardar orquestrador
sleep 3

# Iniciar API Gateway
echo "🌐 Iniciando API Gateway..."
docker-compose up -d api-gateway

# Testar API Gateway
if test_service_health "http://localhost:8000/health" "API Gateway"; then
    echo "🎉 API Gateway funcionando!"
else
    echo "📋 Logs do API Gateway:"
    docker-compose logs api-gateway
    exit 1
fi

# Iniciar Frontend
echo "🎨 Iniciando Frontend..."
docker-compose up -d frontend

# Aguardar Frontend
echo "⏳ Aguardando Frontend inicializar..."
sleep 10

# Verificar Frontend (mais permissivo)
if test_service_health "http://localhost:3000" "Frontend"; then
    echo "✅ Frontend está respondendo!"
else
    echo "⚠️  Frontend pode ainda estar inicializando..."
    echo "💡 Acesse http://localhost:3000 manualmente em alguns minutos"
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
echo "🐳 Status dos containers:"
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
echo "   Ver logs API:       docker-compose logs -f api-gateway"
echo "   Ver logs Frontend:  docker-compose logs -f frontend"
echo "   Limpar tudo:        docker-compose down && docker system prune -f"
echo ""

# Oferecer para mostrar logs
read -p "🤔 Deseja ver os logs em tempo real? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📋 Mostrando logs (Ctrl+C para sair)..."
    docker-compose logs -f
fi