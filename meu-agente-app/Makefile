.PHONY: help setup dev build clean install-deps docker-dev docker-build docker-stop docker-logs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $1, $2}' $(MAKEFILE_LIST)

setup: ## Initial setup (create .env, install dependencies)
	@echo "🚀 Setting up the project..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "📝 Please edit .env file with your OpenAI API key"
	@echo "💡 Run 'make docker-dev' to start with Docker"

install-deps: ## Install all dependencies locally
	@echo "📦 Installing frontend dependencies..."
	@cd apps/frontend && npm install
	@echo "🐍 Installing Python dependencies..."
	@pip install -r requirements.txt
	@echo "✅ Dependencies installed!"

# Docker Commands
docker-dev: ## Start development environment with Docker
	@echo "🐳 Starting Docker development environment..."
	@docker-compose up --build

docker-build: ## Build all Docker images
	@echo "🏗️ Building Docker images..."
	@docker-compose build

docker-stop: ## Stop all Docker containers
	@echo "⏹️ Stopping Docker containers..."
	@docker-compose down

docker-clean: ## Clean Docker containers and images
	@echo "🧹 Cleaning Docker containers and images..."
	@docker-compose down --rmi all --volumes --remove-orphans
	@docker system prune -f

docker-logs: ## Show logs from all containers
	@echo "📋 Showing Docker logs..."
	@docker-compose logs -f

docker-restart: ## Restart all containers
	@echo "🔄 Restarting Docker containers..."
	@docker-compose restart

docker-ps: ## Show running containers
	@echo "📊 Running containers:"
	@docker-compose ps

docker-exec-backend: ## Execute bash in backend container
	@echo "🔧 Entering backend container..."
	@docker-compose exec user-settings-service bash

docker-exec-frontend: ## Execute bash in frontend container
	@echo "🔧 Entering frontend container..."
	@docker-compose exec frontend sh

docker-exec-db: ## Execute psql in database container
	@echo "🗄️ Entering database container..."
	@docker-compose exec postgres psql -U agente_user -d agente_db

# Local Development Commands (without Docker)
dev-local: ## Start development environment locally
	@echo "💻 Starting local development environment..."
	@echo "Starting backend services..."
	@cd apps/services/api-gateway && python main.py &
	@cd apps/services/orchestrator-agent && python main.py &
	@cd apps/services/calendar-service && python main.py &
	@cd apps/services/user-settings-service && python main.py &
	@cd apps/services/tool-factory-service && python main.py &
	@echo "Starting frontend..."
	@cd apps/frontend && npm run dev

dev-frontend: ## Start only frontend in dev mode
	@echo "🎨 Starting frontend development server..."
	@cd apps/frontend && npm run dev

dev-backend: ## Start all backend services locally
	@echo "🔧 Starting backend services..."
	@cd apps/services/api-gateway && python main.py &
	@cd apps/services/orchestrator-agent && python main.py &
	@cd apps/services/calendar-service && python main.py &
	@cd apps/services/user-settings-service && python main.py &
	@cd apps/services/tool-factory-service && python main.py &

# Testing
test: ## Run tests
	@echo "🧪 Running tests..."
	@docker-compose exec frontend npm test
	@docker-compose exec user-settings-service pytest -v

test-local: ## Run tests locally
	@echo "🧪 Running tests locally..."
	@cd apps/frontend && npm test
	@pytest apps/services/*/tests/ -v

# Database
db-migrate: ## Run database migrations in Docker
	@echo "🗄️ Running database migrations..."
	@docker-compose exec user-settings-service python -c "from database import initialize_database, create_default_agents; initialize_database(); create_default_agents()"

db-reset: ## Reset database in Docker
	@echo "🗄️ Resetting database..."
	@docker-compose exec postgres psql -U agente_user -d agente_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	@make db-migrate

# Monitoring
monitor: ## Show system resources
	@echo "📊 System resources:"
	@docker stats --no-stream

# Production
prod-up: ## Start production environment
	@echo "🚀 Starting production environment..."
	@docker-compose --profile production up -d

prod-down: ## Stop production environment
	@echo "⏹️ Stopping production environment..."
	@docker-compose --profile production down

# Backup
backup-db: ## Backup database
	@echo "💾 Backing up database..."
	@docker-compose exec postgres pg_dump -U agente_user agente_db > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Restore database (requires BACKUP_FILE variable)
	@echo "🔄 Restoring database from $(BACKUP_FILE)..."
	@docker-compose exec -T postgres psql -U agente_user agente_db < $(BACKUP_FILE)