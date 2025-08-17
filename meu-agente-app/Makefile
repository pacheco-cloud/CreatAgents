.PHONY: help setup dev build clean install-deps

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $1, $2}' $(MAKEFILE_LIST)

setup: ## Initial setup (create .env, install dependencies)
	@echo "🚀 Setting up the project..."
	@cp .env.example .env
	@echo "📝 Please edit .env file with your OpenAI API key"
	@echo "💡 Run 'make install-deps' to install dependencies"

install-deps: ## Install all dependencies
	@echo "📦 Installing frontend dependencies..."
	@cd apps/frontend && npm install
	@echo "🐍 Installing Python dependencies..."
	@pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

dev: ## Start development environment
	@echo "🔥 Starting development environment..."
	docker-compose up --build

dev-frontend: ## Start only frontend in dev mode
	@echo "🎨 Starting frontend development server..."
	@cd apps/frontend && npm run dev

dev-backend: ## Start all backend services
	@echo "🔧 Starting backend services..."
	@echo "Starting API Gateway..."
	@cd apps/services/api-gateway && python main.py &
	@echo "Starting Orchestrator Agent..."  
	@cd apps/services/orchestrator-agent && python main.py &
	@echo "Starting Calendar Service..."
	@cd apps/services/calendar-service && python main.py &
	@echo "Starting Settings Service..."
	@cd apps/services/user-settings-service && python main.py &
	@echo "Starting Tool Factory..."
	@cd apps/services/tool-factory-service && python main.py &

build: ## Build all services
	@echo "🏗️ Building all services..."
	docker-compose build

clean: ## Clean up containers and images
	@echo "🧹 Cleaning up..."
	docker-compose down
	docker system prune -f

stop: ## Stop all services
	@echo "⏹️ Stopping services..."
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f

test: ## Run tests
	@echo "🧪 Running tests..."
	@cd apps/frontend && npm test
	pytest apps/services/*/tests/ -v
