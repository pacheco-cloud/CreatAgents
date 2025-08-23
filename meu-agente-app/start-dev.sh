#!/bin/bash

echo "🚀 Iniciando ambiente de desenvolvimento..."

# Verificar se o .env existe
if [ ! -f .env ]; then
    echo "❌ Arquivo .env não encontrado! Copiando .env.example..."
    cp .env.example .env
    echo "📝 Edite o arquivo .env com sua chave da OpenAI antes de continuar."
    exit 1
fi

# Verificar se a chave da OpenAI está configurada
if grep -q "your_openai_api_key_here" .env; then
    echo "❌ Configure sua chave da OpenAI no arquivo .env antes de continuar!"
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d ".venv" ]; then
    echo "🐍 Ativando ambiente virtual..."
    source .venv/bin/activate
fi

echo "🎨 Iniciando frontend..."
cd apps/frontend && npm run dev &
FRONTEND_PID=$!

echo "🔧 Iniciando serviços backend..."
cd ../../

# Iniciar cada serviço em background
cd apps/services/api-gateway && python main.py &
API_GATEWAY_PID=$!

cd ../orchestrator-agent && python main.py &
ORCHESTRATOR_PID=$!

cd ../calendar-service && python main.py &
CALENDAR_PID=$!

cd ../user-settings-service && python main.py &
SETTINGS_PID=$!

cd ../../../

echo "✅ Todos os serviços iniciados!"
echo ""
echo "🌐 URLs disponíveis:"
echo "  Frontend: http://localhost:3000"
echo "  API Gateway: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Para parar todos os serviços, pressione Ctrl+C"

# Função para parar todos os processos quando o script for interrompido
cleanup() {
    echo ""
    echo "🛑 Parando todos os serviços..."
    kill $FRONTEND_PID $API_GATEWAY_PID $ORCHESTRATOR_PID $CALENDAR_PID $SETTINGS_PID 2>/dev/null
    echo "✅ Serviços parados!"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Manter o script rodando
wait
