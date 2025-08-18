#!/bin/bash
# start-docker.sh - Script para iniciar o projeto com Docker (versão ajustada)

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

# Função para testar health check com mais tempo e tentativas
test_service_health() {
    local service_url=$1
    local service_name=$2
    local max_attempts=5  # Aumentado de 3 para 5
    local attempt=1
    
    echo "⏳ Testando $service_name..."
    
    # Aguardar um pouco antes de começar os testes
    sleep 5
    
    while [ $attempt -le $max_attempts ]; do
        echo "   Tentativa $attempt/$max_attempts para $service_name..."
        
        # Teste mais robusto com diferentes timeouts
        if curl -f --connect-timeout 10 --max-time 15 --retry 2 "$service_url" >/dev/null 2>&1; then
            echo "✅ $service_name está respondendo!"
            return 0
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            echo "   Aguardando 5 segundos antes da próxima tentativa..."
            sleep 5
        fi
        
        ((attempt++))
    done
    
    echo "❌ $service_name não está respondendo após $max_attempts tentativas"
    
    # Debug adicional
    echo "🔍 Informações de debug:"
    echo "   Container status:"
    docker-compose ps | grep -E "(api-gateway|frontend)" || true
    echo "   Portas em uso:"
    netstat -an | grep -E "(8000|3000)" || lsof -i :8000 -i :3000 || true
    
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

# Liberar portas se estiverem em uso
echo "🔧 Verificando portas..."
for port in 3000 8000 8001 8002 8003 8004; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "⚠️  Porta $port em uso, tentando liberar..."
        lsof -ti:$port | xargs kill -9 >/dev/null 2>&1 || true
    fi
done

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

# Aguardar serviços backend com mais tempo
echo "⏳ Aguardando serviços backend inicializarem..."
sleep 10  # Aumentado de 5 para 10 segundos

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

# Iniciar orquestrador e tool factory
echo "🤖 Iniciando orquestrador e tool factory..."
docker-compose up -d orchestrator-agent tool-factory-service

# Aguardar com mais tempo
echo "⏳ Aguardando orquestrador e tool factory..."
sleep 8  # Aumentado de 3 para 8 segundos

# Iniciar API Gateway
echo "🌐 Iniciando API Gateway..."
docker-compose up -d api-gateway

# Aguardar API Gateway inicializar completamente
echo "⏳ Aguardando API Gateway inicializar completamente..."
sleep 15  # Tempo maior para garantir inicialização

# Testar API Gateway com função melhorada
if test_service_health "http://localhost:8000/health" "API Gateway"; then
    echo "🎉 API Gateway funcionando!"
else
    echo "📋 Logs do API Gateway:"
    docker-compose logs api-gateway
    
    # Tentativa de diagnóstico adicional
    echo "🔍 Diagnóstico adicional:"
    echo "Container API Gateway:"
    docker inspect agente-api-gateway --format='{{.State.Status}}' 2>/dev/null || echo "Container não encontrado"
    
    # Tentar acessar via Docker network
    echo "Tentando acessar via rede Docker..."
    docker-compose exec api-gateway curl -f http://localhost:8000/health 2>/dev/null || echo "Falha no acesso interno"
    
    # Continuar mesmo com falha (para debug)
    echo "⚠️  Continuando apesar da falha no teste do API Gateway..."
fi

# Iniciar Frontend
echo "🎨 Iniciando Frontend..."
docker-compose up -d frontend

# Aguardar Frontend com mais tempo
echo "⏳ Aguardando Frontend inicializar..."
sleep 20  # Aumentado para 20 segundos

# Verificar Frontend (mais permissivo)
if test_service_health "http://localhost:3000" "Frontend"; then
    echo "✅ Frontend está respondendo!"
else
    echo "⚠️  Frontend pode ainda estar inicializando..."
    echo "💡 Tente acessar http://localhost:3000 manualmente em alguns minutos"
    echo "📋 Logs do Frontend:"
    docker-compose logs frontend | tail -20
fi

# Mostrar status final
echo ""
echo "🎉 PROJETO INICIADO!"
echo "================================"
echo ""
echo "🌐 URLs para testar:"
echo "   Frontend:     http://localhost:3000"
echo "   API Gateway:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   Settings:     http://localhost:3000/settings"
echo ""
echo "🐳 Status dos containers:"
docker-compose ps
echo ""
echo "📋 Testes manuais:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:3000"
echo ""
echo "📋 Comandos úteis:"
echo "   Ver logs:           docker-compose logs -f"
echo "   Parar tudo:         docker-compose down"
echo "   Reiniciar:          docker-compose restart"
echo "   Status:             docker-compose ps"
echo "   Logs específicos:   docker-compose logs -f [service-name]"
echo ""
echo "🔧 Se algo não funcionar:"
echo "   1. Aguarde mais alguns minutos"
echo "   2. Teste as URLs manualmente"
echo "   3. Verifique logs: docker-compose logs -f"
echo ""

# Oferecer para mostrar logs
read -p "🤔 Deseja ver os logs em tempo real? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📋 Mostrando logs (Ctrl+C para sair)..."
    docker-compose logs -f
fi