# 🤖 CreatAgents - Sistema Multi-Agente Inteligente

Um sistema completo de agentes de IA com orquestração inteligente, construído com FastAPI, Next.js e Docker.

## 🚀 Características Principais

- **🧠 Orquestrador Inteligente**: Roteia automaticamente mensagens para agentes especializados
- **💬 Assistente de Conhecimento Geral**: Responde perguntas como ChatGPT/Gemini/Claude
- **📅 Gerenciamento de Agenda**: Consulta e gerencia eventos do calendário
- **🔄 Arquitetura Microserviços**: Serviços independentes com comunicação via API
- **🐳 Containerização Docker**: Deploy fácil e escalável
- **🌐 Interface Web Moderna**: Frontend Next.js com chat em tempo real

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   API Gateway   │───▶│  Orchestrator   │
│   (Next.js)     │    │   (FastAPI)     │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                       ┌─────────────────┐    ┌────────┴────────┐
                       │   PostgreSQL    │    │                 │
                       │   (Database)    │    ▼                 ▼
                       └─────────────────┘  ┌─────────┐  ┌─────────────┐
                                           │Calendar │  │User Settings│
                       ┌─────────────────┐  │Service  │  │   Service   │
                       │     Redis       │  │(FastAPI)│  │  (FastAPI)  │
                       │    (Cache)      │  └─────────┘  └─────────────┘
                       └─────────────────┘
```

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno para APIs
- **PostgreSQL** - Banco de dados relacional
- **Redis** - Cache e gerenciamento de sessões
- **SQLAlchemy** - ORM para Python
- **OpenAI API** - Integração com modelos de IA

### Frontend
- **Next.js 14** - Framework React com App Router
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Framework CSS utilitário
- **Lucide React** - Biblioteca de ícones

### DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração de containers

## 🚀 Como Executar

### Pré-requisitos
- Docker e Docker Compose instalados
- Chave da API OpenAI (opcional, mas recomendado)

### 1. Clone o repositório
```bash
git clone https://github.com/pacheco-cloud/CreatAgents.git
cd CreatAgents/meu-agente-app
```

### 2. Configure as variáveis de ambiente
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com sua chave OpenAI
nano .env
```

### 3. Execute o projeto
```bash
# Construir e iniciar todos os serviços
docker-compose up -d --build

# Verificar status dos containers
docker-compose ps
```

### 4. Acesse a aplicação
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Documentação da API**: http://localhost:8000/docs

## 📋 Serviços Disponíveis

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| Frontend | 3000 | Interface web do chat |
| API Gateway | 8000 | Gateway principal da API |
| Orchestrator | 8001 | Orquestrador de agentes |
| Calendar Service | 8002 | Serviço de calendário |
| User Settings | 8004 | Configurações dos agentes |
| PostgreSQL | 5432 | Banco de dados |
| Redis | 6379 | Cache e sessões |

## 🤖 Como Usar

### Conhecimento Geral
Faça qualquer pergunta como faria com ChatGPT:
```
"Explique sobre inteligência artificial"
"Como funciona machine learning?"
"Escreva um código Python para..."
```

### Agenda e Calendário
Use palavras-chave relacionadas à agenda:
```
"Qual é minha agenda para hoje?"
"Que compromissos tenho amanhã?"
"Mostre meus eventos da semana"
```

O sistema detecta automaticamente o tipo de consulta e roteia para o agente apropriado.

## 🔧 Desenvolvimento

### Estrutura do Projeto
```
meu-agente-app/
├── apps/
│   ├── frontend/              # Interface Next.js
│   └── services/              # Microserviços FastAPI
│       ├── api-gateway/       # Gateway principal
│       ├── orchestrator-agent/# Orquestrador
│       ├── calendar-service/  # Serviço de agenda
│       └── user-settings-service/ # Configurações
├── scripts/
│   └── init-db.sql           # Script de inicialização do DB
├── docker-compose.yml        # Configuração Docker
└── start-dev.sh             # Script de desenvolvimento
```

### Comandos Úteis

```bash
# Ver logs de um serviço específico
docker-compose logs -f frontend

# Reconstruir um serviço
docker-compose build orchestrator-agent

# Executar comando em um container
docker-compose exec postgres psql -U agente_user -d agente_db

# Parar todos os serviços
docker-compose down

# Limpar volumes (cuidado: remove dados!)
docker-compose down -v
```

## 🌟 Funcionalidades

### ✅ Implementadas
- [x] Sistema de chat multi-agente
- [x] Orquestração inteligente de mensagens
- [x] Assistente de conhecimento geral
- [x] Consulta de agenda/calendário
- [x] Interface web responsiva
- [x] Containerização Docker
- [x] Banco de dados PostgreSQL
- [x] Cache Redis

### 🔄 Em Desenvolvimento
- [ ] Criação de novos eventos na agenda
- [ ] Autenticação de usuários
- [ ] Personalização de agentes
- [ ] Integração com calendários externos
- [ ] API para webhooks
- [ ] Dashboard administrativo

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🐛 Problemas e Suporte

Se encontrar problemas ou tiver sugestões:
1. Verifique se todos os containers estão rodando: `docker-compose ps`
2. Consulte os logs: `docker-compose logs`
3. Abra uma issue no GitHub com detalhes do problema

## 👨‍💻 Autor

**Ricardo Pacheco**
- GitHub: [@pacheco-cloud](https://github.com/pacheco-cloud)

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!
