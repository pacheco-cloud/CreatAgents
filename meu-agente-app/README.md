# 🤖 Sistema Multi-Agente

Sistema inteligente de assistente pessoal e profissional com arquitetura de microserviços.

## 🏗️ Arquitetura

### Frontend
- **Next.js 14** com TypeScript
- **Tailwind CSS** para estilização
- **Allotment** para divisão de tela (Chat/Canvas)
- **FullCalendar** para visualização de calendário

### Backend
- **FastAPI** para todos os microserviços
- **Pydantic AI** para orquestração de agentes
- **OpenAI GPT-4-mini** como modelo de linguagem
- **PostgreSQL** para persistência
- **Redis** para cache e filas

### Microserviços
1. **API Gateway** (8000) - Ponto de entrada único
2. **Orchestrator Agent** (8001) - Agente principal com Pydantic AI  
3. **Calendar Service** (8002) - Gerenciamento de calendários
4. **User Settings Service** (8003) - Configurações e agentes
5. **Tool Factory Service** (8004) - Criação dinâmica de ferramentas

## 🚀 Como executar

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- Docker e Docker Compose (opcional)

### Setup inicial
```bash
# 1. Clone e configure o projeto
cd meu-agente-app

# 2. Criar ambiente virtual Python
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou .venv\Scripts\activate  # Windows

# 3. Setup inicial
make setup

# 4. Editar .env com sua chave OpenAI
# OPENAI_API_KEY=sk-your-key-here

# 5. Instalar dependências
make install-deps
```

### Desenvolvimento

```bash
# Opção 1: Docker (Recomendado)
make dev

# Opção 2: Desenvolvimento local
# Terminal 1 - Frontend
make dev-frontend

# Terminal 2 - Backend
make dev-backend
```

### URLs
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Docs API**: http://localhost:8000/docs

## 🎯 Funcionalidades

### Chat Multi-Agente
- Interface de chat inteligente
- Detecção automática de contexto (pessoal/profissional)
- Canvas lateral para visualizações

### Configurações Avançadas
- Criação de agentes personalizados
- Sistema de ferramentas configuráveis
- Edição, duplicação e exclusão de agentes

### Calendários Inteligentes
- Calendário pessoal e profissional
- Visualização em FullCalendar
- Integração com o sistema de chat

## 🔧 Desenvolvimento

### Estrutura de Pastas
```
meu-agente-app/
├── apps/
│   ├── frontend/          # Next.js app
│   └── services/          # Python microservices
├── packages/              # Shared packages
├── docker-compose.yml     # Container orchestration
└── Makefile              # Development commands
```

### Adicionando Novos Agentes
1. Use a interface `/settings` no frontend
2. Configure nome, tipo (Pessoal/Profissional)
3. Defina system prompt e ferramentas
4. Teste no chat principal

### Criando Novas Ferramentas
1. Acesse "Criar Novo Agente" nas configurações
2. Adicione ferramentas com parâmetros customizados
3. Configure endpoint da API
4. O sistema gerará automaticamente a integração

## 🧪 Testes

```bash
# Executar todos os testes
make test

# Testes específicos
cd apps/frontend && npm test
pytest apps/services/*/tests/ -v
```

## 📝 Próximos Passos

- [ ] Integração com calendários externos (Google, Outlook)
- [ ] Sistema de notificações em tempo real
- [ ] Dashboard de métricas e analytics
- [ ] Suporte a mais modelos de IA (Anthropic, Gemini)
- [ ] Sistema de backup e sincronização
- [ ] Mobile app (React Native)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
