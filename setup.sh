#!/bin/bash

# Script de Setup - Sistema Multi-Agente com Arquitetura de Microserviços
# Baseado na conversa e especificações definidas

set -e

echo "🚀 Iniciando setup do Sistema Multi-Agente..."
echo "📁 Criando estrutura de pastas..."

# Criar estrutura principal
mkdir -p meu-agente-app
cd meu-agente-app

# Estrutura do monorepo
mkdir -p {apps/{frontend,services},packages/{ui,tsconfig}}

# Frontend Next.js
mkdir -p apps/frontend/{app/{chat,canvas,settings},components,lib,public}
mkdir -p apps/frontend/app/{chat,canvas,settings}
mkdir -p apps/frontend/components/{ui,layout}

# Backend Services
mkdir -p apps/services/{api-gateway,orchestrator-agent,calendar-service,user-settings-service,tool-factory-service}

# Packages compartilhados
mkdir -p packages/{ui/components,tsconfig}

echo "📄 Criando arquivos de configuração..."

# Package.json principal (monorepo)
cat > package.json << 'EOF'
{
  "name": "meu-agente-app",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "turbo run dev",
    "build": "turbo run build",
    "lint": "turbo run lint",
    "clean": "turbo run clean"
  },
  "devDependencies": {
    "turbo": "latest"
  },
  "workspaces": [
    "apps/*",
    "packages/*"
  ]
}
EOF

# Turbo.json para monorepo
cat > turbo.json << 'EOF'
{
  "$schema": "https://turbo.build/schema.json",
  "globalDependencies": ["**/.env.*local"],
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "lint": {},
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
EOF

echo "🎨 Configurando Frontend Next.js..."

# Package.json do Frontend
cat > apps/frontend/package.json << 'EOF'
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "next": "14",
    "typescript": "^5",
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.24",
    "allotment": "^1.20.0",
    "@fullcalendar/react": "^6.1.8",
    "@fullcalendar/daygrid": "^6.1.8",
    "@fullcalendar/timegrid": "^6.1.8",
    "@fullcalendar/interaction": "^6.1.8",
    "lucide-react": "^0.263.1",
    "zustand": "^4.4.1",
    "axios": "^1.5.0"
  }
}
EOF

# Next.js config
cat > apps/frontend/next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    OPENAI_API_KEY: process.env.OPENAI_API_KEY,
  }
}

module.exports = nextConfig
EOF

# Tailwind config
cat > apps/frontend/tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
EOF

# PostCSS config
cat > apps/frontend/postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# TypeScript config do frontend
cat > apps/frontend/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./app/*"],
      "@/components/*": ["./components/*"],
      "@/lib/*": ["./lib/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

# Layout principal
cat > apps/frontend/app/layout.tsx << 'EOF'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Sistema Multi-Agente',
  description: 'Seu assistente pessoal e profissional inteligente',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
EOF

# Globals CSS
cat > apps/frontend/app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

body {
  font-family: 'Inter', sans-serif;
}

/* FullCalendar custom styles */
.fc-theme-standard td, .fc-theme-standard th {
  border-color: #e5e7eb;
}

.fc-button-primary {
  background-color: #3b82f6 !important;
  border-color: #3b82f6 !important;
}

.fc-button-primary:hover {
  background-color: #2563eb !important;
  border-color: #2563eb !important;
}
EOF

# Página principal (redirecionamento para chat)
cat > apps/frontend/app/page.tsx << 'EOF'
import { redirect } from 'next/navigation'

export default function HomePage() {
  redirect('/chat')
}
EOF

# Componente principal do Chat (baseado no seu código original)
cat > apps/frontend/app/chat/page.tsx << 'EOF'
'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, Settings, User, Briefcase, Calendar } from 'lucide-react'
import { Allotment } from 'allotment'
import 'allotment/dist/style.css'
import Link from 'next/link'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'

// Dados mock para demonstração
const personalCalendarEvents = [
  { id: 1, title: 'Aniversário da cidade', date: '2025-01-20', color: '#22c55e' },
  { id: 2, title: 'Reunião família', date: '2025-01-19', color: '#22c55e' },
  { id: 3, title: 'Dentista', date: '2025-01-21', color: '#22c55e' },
]

const professionalCalendarEvents = [
  { id: 1, title: 'Reunião equipe', date: '2025-01-20', color: '#3b82f6' },
  { id: 2, title: 'Apresentação projeto', date: '2025-01-21', color: '#3b82f6' },
  { id: 3, title: 'Call cliente', date: '2025-01-19', color: '#3b82f6' },
]

interface Message {
  id: number
  type: 'user' | 'bot'
  content: string
  agent?: string
  timestamp: Date
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [activeAgent, setActiveAgent] = useState('master')
  const [showCanvas, setShowCanvas] = useState(false)
  const [canvasContent, setCanvasContent] = useState<'personal' | 'professional' | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const processMessage = async (message: string) => {
    setIsLoading(true)
    
    const userMessage: Message = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    
    // Simular processamento
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    let response = ''
    let agent = 'master'
    
    const msg = message.toLowerCase()
    
    if (msg.includes('agenda pessoal') || msg.includes('pessoal')) {
      agent = 'Calendário Pessoal'
      response = 'Consultando sua agenda pessoal... Encontrei seus próximos compromissos!'
      setCanvasContent('personal')
      setShowCanvas(true)
    } else if (msg.includes('agenda profissional') || msg.includes('profissional')) {
      agent = 'Calendário Profissional'
      response = 'Verificando sua agenda profissional... Aqui estão suas reuniões!'
      setCanvasContent('professional')
      setShowCanvas(true)
    } else {
      response = 'Olá! Posso ajudar com sua agenda pessoal ou profissional. O que você gostaria de consultar?'
    }
    
    setActiveAgent(agent)
    
    const botMessage: Message = {
      id: Date.now() + 1,
      type: 'bot',
      content: response,
      agent,
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, botMessage])
    setIsLoading(false)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputValue.trim()) {
      processMessage(inputValue)
      setInputValue('')
    }
  }

  const getAgentIcon = (agentName: string) => {
    if (agentName === 'Calendário Pessoal') return User
    if (agentName === 'Calendário Profissional') return Briefcase
    return Settings
  }

  const getAgentColor = (agentName: string) => {
    if (agentName === 'Calendário Pessoal') return 'green'
    if (agentName === 'Calendário Profissional') return 'blue'
    return 'purple'
  }

  return (
    <div className="h-screen bg-gray-50">
      <Allotment>
        {/* Painel do Chat */}
        <Allotment.Pane minSize={400}>
          <div className="h-full flex flex-col bg-white">
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4">
              <div className="flex justify-between items-center">
                <div>
                  <h1 className="text-xl font-bold">Chat Multi-Agente</h1>
                  <div className="flex items-center space-x-2 mt-2">
                    <div className={`w-3 h-3 rounded-full bg-${getAgentColor(activeAgent)}-400`}></div>
                    <span className="text-sm">{activeAgent === 'master' ? 'Agente Master' : activeAgent} ativo</span>
                  </div>
                </div>
                <Link href="/settings" className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors">
                  <Settings className="w-5 h-5" />
                </Link>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && (
                <div className="text-center text-gray-500 mt-8">
                  <Settings className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="text-lg font-medium mt-4">Bem-vindo ao Sistema Multi-Agente!</h3>
                  <p className="mt-2">Experimente perguntar:</p>
                  <div className="mt-4 space-y-2 text-sm">
                    <div className="bg-gray-100 p-2 rounded">"Mostrar minha agenda pessoal"</div>
                    <div className="bg-gray-100 p-2 rounded">"Verificar agenda profissional"</div>
                  </div>
                </div>
              )}
              
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[70%] rounded-lg p-3 ${
                    message.type === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-100 border'
                  }`}>
                    {message.type === 'bot' && message.agent && (
                      <div className="flex items-center space-x-2 mb-2">
                        {React.createElement(getAgentIcon(message.agent), { 
                          className: `w-4 h-4 text-${getAgentColor(message.agent)}-600` 
                        })}
                        <span className={`text-xs font-medium text-${getAgentColor(message.agent)}-600`}>
                          {message.agent}
                        </span>
                      </div>
                    )}
                    <div className="text-sm">{message.content}</div>
                    <div className={`text-xs mt-1 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 border rounded-lg p-3">
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full"></div>
                      <span className="text-sm">Processando...</span>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-4 border-t bg-white">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Digite sua mensagem..."
                  className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !inputValue.trim()}
                  className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </form>
          </div>
        </Allotment.Pane>

        {/* Canvas */}
        {showCanvas && (
          <Allotment.Pane>
            <div className="h-full bg-white border-l flex flex-col">
              <div className="bg-gray-100 p-4 border-b flex justify-between items-center">
                <div className="flex items-center space-x-2">
                  <Calendar className="w-5 h-5 text-blue-600" />
                  <h2 className="text-lg font-semibold">
                    {canvasContent === 'personal' ? 'Agenda Pessoal' : 'Agenda Profissional'}
                  </h2>
                </div>
                <button
                  onClick={() => setShowCanvas(false)}
                  className="text-gray-500 hover:text-gray-700 text-xl"
                >
                  ×
                </button>
              </div>
              <div className="flex-1 overflow-y-auto p-4">
                <FullCalendar
                  plugins={[dayGridPlugin]}
                  initialView="dayGridMonth"
                  events={canvasContent === 'personal' ? personalCalendarEvents : professionalCalendarEvents}
                  headerToolbar={{
                    left: 'prev,next today',
                    center: 'title',
                    right: 'dayGridMonth'
                  }}
                  height="100%"
                />
              </div>
            </div>
          </Allotment.Pane>
        )}
      </Allotment>
    </div>
  )
}
EOF

# Página de Settings (baseada na sua especificação)
cat > apps/frontend/app/settings/page.tsx << 'EOF'
'use client'

import React, { useState } from 'react'
import { ArrowLeft, Plus, Edit, Copy, Trash2, Save, X, PlusCircle } from 'lucide-react'
import Link from 'next/link'

interface Tool {
  name: string
  description: string
  apiEndpoint: string
  parameters: Array<{
    name: string
    type: 'texto' | 'numero' | 'data' | 'booleano'
  }>
}

interface Agent {
  id: number
  name: string
  type: 'Pessoal' | 'Profissional'
  isDefault: boolean
  systemPrompt: string
  tools: Tool[]
}

const defaultAgents: Agent[] = [
  {
    id: 1,
    name: 'Calendário Pessoal',
    type: 'Pessoal',
    isDefault: true,
    systemPrompt: 'Você é um assistente de agenda pessoal. Ajude com compromissos pessoais, eventos familiares e atividades de lazer.',
    tools: [{
      name: 'consultar_agenda_pessoal',
      description: 'Consulta eventos na agenda pessoal do usuário',
      apiEndpoint: '/api/calendar/personal',
      parameters: [
        { name: 'data_inicio', type: 'data' },
        { name: 'data_fim', type: 'data' }
      ]
    }]
  },
  {
    id: 2,
    name: 'Calendário Profissional',
    type: 'Profissional',
    isDefault: true,
    systemPrompt: 'Você é um assistente de agenda profissional. Ajude com reuniões, projetos e compromissos de trabalho.',
    tools: [{
      name: 'consultar_agenda_profissional',
      description: 'Consulta eventos na agenda profissional do usuário',
      apiEndpoint: '/api/calendar/professional',
      parameters: [
        { name: 'data_inicio', type: 'data' },
        { name: 'data_fim', type: 'data' }
      ]
    }]
  }
]

export default function SettingsPage() {
  const [agents, setAgents] = useState<Agent[]>(defaultAgents)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingAgent, setEditingAgent] = useState<Partial<Agent> | null>(null)

  const openCreateModal = () => {
    setEditingAgent({
      name: '',
      type: 'Pessoal',
      isDefault: false,
      systemPrompt: '',
      tools: [{
        name: '',
        description: '',
        apiEndpoint: '',
        parameters: []
      }]
    })
    setIsModalOpen(true)
  }

  const openEditModal = (agent: Agent) => {
    setEditingAgent({ ...agent })
    setIsModalOpen(true)
  }

  const handleSave = () => {
    if (!editingAgent?.name?.trim()) {
      alert('Nome do agente é obrigatório')
      return
    }

    if ('id' in editingAgent && editingAgent.id) {
      // Editar existente
      setAgents(prev => prev.map(a => a.id === editingAgent.id ? editingAgent as Agent : a))
    } else {
      // Criar novo
      const newAgent: Agent = {
        ...editingAgent as Agent,
        id: Date.now()
      }
      setAgents(prev => [...prev, newAgent])
    }
    
    setIsModalOpen(false)
    setEditingAgent(null)
  }

  const handleDelete = (id: number) => {
    const agent = agents.find(a => a.id === id)
    if (agent?.isDefault) return
    
    if (confirm('Tem certeza que deseja deletar este agente?')) {
      setAgents(prev => prev.filter(a => a.id !== id))
    }
  }

  const handleDuplicate = (agent: Agent) => {
    const duplicated: Agent = {
      ...JSON.parse(JSON.stringify(agent)),
      id: Date.now(),
      name: `${agent.name} (Cópia)`,
      isDefault: false
    }
    setAgents(prev => [...prev, duplicated])
  }

  const addTool = () => {
    if (!editingAgent) return
    setEditingAgent({
      ...editingAgent,
      tools: [
        ...editingAgent.tools || [],
        {
          name: '',
          description: '',
          apiEndpoint: '',
          parameters: []
        }
      ]
    })
  }

  const updateTool = (toolIndex: number, field: string, value: any) => {
    if (!editingAgent?.tools) return
    const newTools = [...editingAgent.tools]
    newTools[toolIndex] = { ...newTools[toolIndex], [field]: value }
    setEditingAgent({ ...editingAgent, tools: newTools })
  }

  const addParameter = (toolIndex: number) => {
    if (!editingAgent?.tools) return
    const newTools = [...editingAgent.tools]
    newTools[toolIndex].parameters.push({ name: '', type: 'texto' })
    setEditingAgent({ ...editingAgent, tools: newTools })
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-6xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/chat" className="text-gray-400 hover:text-white transition-colors">
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold">Configurações</h1>
                <p className="text-gray-400">Gerencie seus agentes e ferramentas</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold">Meus Agentes</h2>
          <button
            onClick={openCreateModal}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            <span>Criar Novo Agente</span>
          </button>
        </div>

        <div className="grid gap-4">
          {agents.map(agent => (
            <div key={agent.id} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                    agent.type === 'Pessoal' 
                      ? 'bg-green-500/20 text-green-300' 
                      : 'bg-blue-500/20 text-blue-300'
                  }`}>
                    {agent.type}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold">{agent.name}</h3>
                    <p className="text-gray-400 text-sm">
                      {agent.tools.length} ferramenta(s) configurada(s)
                      {agent.isDefault && ' • Padrão do sistema'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => openEditModal(agent)}
                    className="p-2 text-gray-400 hover:text-white transition-colors"
                  >
                    <Edit className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleDuplicate(agent)}
                    className="p-2 text-gray-400 hover:text-white transition-colors"
                  >
                    <Copy className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(agent.id)}
                    disabled={agent.isDefault}
                    className="p-2 text-gray-400 hover:text-red-400 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && editingAgent && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-700 flex justify-between items-center">
              <h2 className="text-xl font-bold">
                {'id' in editingAgent ? 'Editar Agente' : 'Criar Novo Agente'}
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Basic Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Nome do Agente</label>
                  <input
                    type="text"
                    value={editingAgent.name || ''}
                    onChange={(e) => setEditingAgent({ ...editingAgent, name: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="Pessoal">Pessoal</option>
                    <option value="Profissional">Profissional</option>
                  </select>
                </div>
              </div>

              {/* System Prompt */}
              <div>
                <label className="block text-sm font-medium mb-2">Persona e Objetivo (System Prompt)</label>
                <textarea
                  value={editingAgent.systemPrompt || ''}
                  onChange={(e) => setEditingAgent({ ...editingAgent, systemPrompt: e.target.value })}
                  rows={4}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Descreva como o agente deve se comportar e qual sua função principal..."
                />
              </div>

              {/* Tools */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Ferramentas</h3>
                  <button
                    onClick={addTool}
                    type="button"
                    className="flex items-center space-x-1 text-blue-400 hover:text-blue-300"
                  >
                    <PlusCircle className="w-5 h-5" />
                    <span>Adicionar Ferramenta</span>
                  </button>
                </div>

                {editingAgent.tools?.map((tool, toolIndex) => (
                  <div key={toolIndex} className="bg-gray-700/50 rounded-lg p-4 mb-4 border border-gray-600">
                    <h4 className="font-medium mb-3">Ferramenta {toolIndex + 1}</h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">Nome da Ferramenta</label>
                        <input
                          type="text"
                          value={tool.name}
                          onChange={(e) => updateTool(toolIndex, 'name', e.target.value)}
                          className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded focus:ring-2 focus:ring-blue-500"
                          placeholder="ex: buscar_hoteis"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Endpoint da API</label>
                        <input
                          type="text"
                          value={tool.apiEndpoint}
                          onChange={(e) => updateTool(toolIndex, 'apiEndpoint', e.target.value)}
                          className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded focus:ring-2 focus:ring-blue-500"
                          placeholder="/api/travel/hotels"
                        />
                      </div>
                    </div>

                    <div className="mb-4">
                      <label className="block text-sm font-medium mb-1">Descrição</label>
                      <textarea
                        value={tool.description}
                        onChange={(e) => updateTool(toolIndex, 'description', e.target.value)}
                        rows={2}
                        className="w-full px-3 py-2 bg-gray-600 border border-gray-500 rounded focus:ring-2 focus:ring-blue-500"
                        placeholder="Descreva o que esta ferramenta faz..."
                      />
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <label className="block text-sm font-medium">Parâmetros</label>
                        <button
                          onClick={() => addParameter(toolIndex)}
                          type="button"
                          className="text-sm text-blue-400 hover:text-blue-300"
                        >
                          + Adicionar Parâmetro
                        </button>
                      </div>
                      
                      {tool.parameters.map((param, paramIndex) => (
                        <div key={paramIndex} className="flex gap-2 mb-2">
                          <input
                            type="text"
                            value={param.name}
                            onChange={(e) => {
                              const newParams = [...tool.parameters]
                              newParams[paramIndex] = { ...param, name: e.target.value }
                              updateTool(toolIndex, 'parameters', newParams)
                            }}
                            className="flex-1 px-2 py-1 bg-gray-600 border border-gray-500 rounded text-sm"
                            placeholder="Nome do parâmetro"
                          />
                          <select
                            value={param.type}
                            onChange={(e) => {
                              const newParams = [...tool.parameters]
                              newParams[paramIndex] = { ...param, type: e.target.value as any }
                              updateTool(toolIndex, 'parameters', newParams)
                            }}
                            className="px-2 py-1 bg-gray-600 border border-gray-500 rounded text-sm"
                          >
                            <option value="texto">Texto</option>
                            <option value="numero">Número</option>
                            <option value="data">Data</option>
                            <option value="booleano">Booleano</option>
                          </select>
                          <button
                            onClick={() => {
                              const newParams = tool.parameters.filter((_, i) => i !== paramIndex)
                              updateTool(toolIndex, 'parameters', newParams)
                            }}
                            className="px-2 text-red-400 hover:text-red-300"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 border-t border-gray-700 flex justify-end space-x-3">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleSave}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
              >
                <Save className="w-5 h-5" />
                <span>Salvar Agente</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
EOF

echo "🐍 Configurando Backend Services (Python)..."

# Requirements para todos os serviços Python
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-ai==0.0.6
python-dotenv==1.0.0
httpx==0.25.2
python-multipart==0.0.6
openai==1.3.8
asyncio==3.4.3
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
pytest==7.4.3
pytest-asyncio==0.21.1
EOF

# API Gateway
cat > apps/services/api-gateway/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from typing import Dict, Any

app = FastAPI(title="API Gateway", version="1.0.0")

# CORS para permitir requests do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração dos microserviços
SERVICES = {
    "orchestrator": "http://localhost:8001",
    "calendar": "http://localhost:8002",
    "settings": "http://localhost:8003",
    "tool-factory": "http://localhost:8004"
}

class ChatMessage(BaseModel):
    message: str
    user_id: str = "default_user"

class AgentConfig(BaseModel):
    name: str
    type: str
    system_prompt: str
    tools: list

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

@app.post("/chat")
async def chat_endpoint(request: ChatMessage):
    """Rota principal para o chat - encaminha para o orquestrador"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVICES['orchestrator']}/process",
                json=request.dict()
            )
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Orchestrator service unavailable: {e}")

@app.get("/agents")
async def get_agents():
    """Lista todos os agentes configurados"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICES['settings']}/agents")
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Settings service unavailable")

@app.post("/agents")
async def create_agent(agent_config: AgentConfig):
    """Cria um novo agente"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SERVICES['settings']}/agents",
                json=agent_config.dict()
            )
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Settings service unavailable")

@app.get("/calendar/{calendar_type}")
async def get_calendar(calendar_type: str):
    """Busca eventos do calendário"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICES['calendar']}/{calendar_type}")
            return response.json()
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Calendar service unavailable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Orchestrator Agent (Pydantic AI)
cat > apps/services/orchestrator-agent/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
import os
from dotenv import load_dotenv
import httpx
from typing import Dict, Any, List

load_dotenv()

app = FastAPI(title="Orchestrator Agent", version="1.0.0")

# Configurar modelo OpenAI
model = OpenAIModel(
    'gpt-4-mini',  # Usando gpt-4-mini como especificado
    api_key=os.getenv('OPENAI_API_KEY')
)

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    show_canvas: bool = False
    canvas_type: str = None

# Agente Orquestrador Principal
orchestrator = Agent(
    model,
    system_prompt="""
    Você é o Agente Orquestrador de um sistema multi-agente.
    Sua função é analisar as mensagens do usuário e decidir:
    1. Qual agente especializado deve responder
    2. Se deve mostrar informações no canvas visual
    
    Agentes disponíveis:
    - calendar_personal: Para agenda pessoal, compromissos familiares
    - calendar_professional: Para agenda profissional, reuniões de trabalho
    
    Responda sempre em português brasileiro.
    Se a mensagem for sobre agenda pessoal, responda que está consultando e marque para mostrar o canvas.
    Se for sobre agenda profissional, faça o mesmo.
    Para outras perguntas, seja útil e educado.
    """
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "orchestrator-agent"}

@app.post("/process")
async def process_message(request: ChatRequest) -> ChatResponse:
    """Processa a mensagem do usuário e orquestra a resposta"""
    
    try:
        # Usar Pydantic AI para processar a mensagem
        result = await orchestrator.run(request.message)
        
        # Determinar se deve mostrar canvas e qual tipo
        message_lower = request.message.lower()
        show_canvas = False
        canvas_type = None
        agent_used = "master"
        
        if any(word in message_lower for word in ["agenda pessoal", "pessoal", "família"]):
            show_canvas = True
            canvas_type = "personal"
            agent_used = "Calendário Pessoal"
            
        elif any(word in message_lower for word in ["agenda profissional", "profissional", "trabalho", "reunião"]):
            show_canvas = True
            canvas_type = "professional" 
            agent_used = "Calendário Profissional"
        
        return ChatResponse(
            response=str(result.data),
            agent_used=agent_used,
            show_canvas=show_canvas,
            canvas_type=canvas_type
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
EOF

# Calendar Service
cat > apps/services/calendar-service/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
import json

app = FastAPI(title="Calendar Service", version="1.0.0")

class Event(BaseModel):
    id: int
    title: str
    date: str
    color: str
    type: str = "event"

# Mock data - em produção isso viria de um banco de dados
PERSONAL_EVENTS = [
    Event(id=1, title="Aniversário da cidade", date="2025-01-20", color="#22c55e", type="holiday"),
    Event(id=2, title="Reunião família", date="2025-01-19", color="#22c55e", type="personal"),
    Event(id=3, title="Dentista", date="2025-01-21", color="#22c55e", type="appointment"),
    Event(id=4, title="Academia", date="2025-01-20", color="#22c55e", type="exercise")
]

PROFESSIONAL_EVENTS = [
    Event(id=1, title="Reunião equipe", date="2025-01-20", color="#3b82f6", type="meeting"),
    Event(id=2, title="Apresentação projeto", date="2025-01-21", color="#3b82f6", type="presentation"),
    Event(id=3, title="Call cliente", date="2025-01-19", color="#3b82f6", type="call")
]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "calendar-service"}

@app.get("/personal")
async def get_personal_calendar() -> List[Event]:
    """Retorna eventos do calendário pessoal"""
    return PERSONAL_EVENTS

@app.get("/professional") 
async def get_professional_calendar() -> List[Event]:
    """Retorna eventos do calendário profissional"""
    return PROFESSIONAL_EVENTS

@app.post("/personal")
async def create_personal_event(event: Event) -> Event:
    """Cria um novo evento pessoal"""
    event.id = max([e.id for e in PERSONAL_EVENTS], default=0) + 1
    event.color = "#22c55e"
    PERSONAL_EVENTS.append(event)
    return event

@app.post("/professional")
async def create_professional_event(event: Event) -> Event:
    """Cria um novo evento profissional"""
    event.id = max([e.id for e in PROFESSIONAL_EVENTS], default=0) + 1
    event.color = "#3b82f6"
    PROFESSIONAL_EVENTS.append(event)
    return event

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
EOF

# User Settings Service
cat > apps/services/user-settings-service/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
import os

app = FastAPI(title="User Settings Service", version="1.0.0")

class Tool(BaseModel):
    name: str
    description: str
    apiEndpoint: str
    parameters: List[Dict[str, Any]]

class Agent(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    isDefault: bool = False
    systemPrompt: str
    tools: List[Tool]

# Agentes padrão do sistema
DEFAULT_AGENTS = [
    Agent(
        id=1,
        name="Calendário Pessoal",
        type="Pessoal", 
        isDefault=True,
        systemPrompt="Você é um assistente de agenda pessoal. Ajude com compromissos pessoais, eventos familiares e atividades de lazer.",
        tools=[Tool(
            name="consultar_agenda_pessoal",
            description="Consulta eventos na agenda pessoal do usuário",
            apiEndpoint="/api/calendar/personal",
            parameters=[
                {"name": "data_inicio", "type": "data"},
                {"name": "data_fim", "type": "data"}
            ]
        )]
    ),
    Agent(
        id=2,
        name="Calendário Profissional",
        type="Profissional",
        isDefault=True, 
        systemPrompt="Você é um assistente de agenda profissional. Ajude com reuniões, projetos e compromissos de trabalho.",
        tools=[Tool(
            name="consultar_agenda_profissional",
            description="Consulta eventos na agenda profissional do usuário", 
            apiEndpoint="/api/calendar/professional",
            parameters=[
                {"name": "data_inicio", "type": "data"},
                {"name": "data_fim", "type": "data"}
            ]
        )]
    )
]

# Simulando um "banco de dados" em memória
agents_db = DEFAULT_AGENTS.copy()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "user-settings-service"}

@app.get("/agents")
async def get_agents() -> List[Agent]:
    """Retorna todos os agentes configurados"""
    return agents_db

@app.post("/agents")
async def create_agent(agent: Agent) -> Agent:
    """Cria um novo agente personalizado"""
    agent.id = max([a.id for a in agents_db], default=0) + 1
    agents_db.append(agent)
    return agent

@app.put("/agents/{agent_id}")
async def update_agent(agent_id: int, agent: Agent) -> Agent:
    """Atualiza um agente existente"""
    for i, a in enumerate(agents_db):
        if a.id == agent_id:
            agent.id = agent_id
            agents_db[i] = agent
            return agent
    raise HTTPException(status_code=404, detail="Agent not found")

@app.delete("/agents/{agent_id}")
async def delete_agent(agent_id: int):
    """Deleta um agente (não permite deletar agentes padrão)"""
    agent = next((a for a in agents_db if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if agent.isDefault:
        raise HTTPException(status_code=400, detail="Cannot delete default agent")
    
    agents_db[:] = [a for a in agents_db if a.id != agent_id]
    return {"message": "Agent deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
EOF

# Tool Factory Service
cat > apps/services/tool-factory-service/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import httpx

app = FastAPI(title="Tool Factory Service", version="1.0.0")

class ToolConfig(BaseModel):
    name: str
    description: str
    apiEndpoint: str
    parameters: List[Dict[str, Any]]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tool-factory-service"}

@app.post("/create-tool")
async def create_tool(tool_config: ToolConfig):
    """
    Cria dinamicamente uma nova ferramenta que pode ser usada pelos agentes.
    Em uma implementação completa, isso geraria código Pydantic AI automaticamente.
    """
    # Por enquanto, apenas log da configuração
    print(f"Criando ferramenta: {tool_config.name}")
    print(f"Endpoint: {tool_config.apiEndpoint}")
    print(f"Parâmetros: {tool_config.parameters}")
    
    # Em produção, aqui seria gerado dinamicamente:
    # 1. Um modelo Pydantic para os parâmetros
    # 2. Uma função que chama a API externa
    # 3. Registrar a ferramenta no agente orquestrador
    
    return {
        "message": f"Ferramenta '{tool_config.name}' criada com sucesso",
        "tool_id": hash(tool_config.name),
        "status": "created"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
EOF

echo "🔧 Criando arquivos de configuração para os serviços..."

# Docker files para cada serviço
for service in api-gateway orchestrator-agent calendar-service user-settings-service tool-factory-service; do
    cat > apps/services/$service/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
EOF

    cat > apps/services/$service/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-ai==0.0.6
python-dotenv==1.0.0
httpx==0.25.2
python-multipart==0.0.6
openai==1.3.8
asyncio==3.4.3
EOF
done

echo "🐳 Criando Docker Compose..."

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Frontend Next.js
  frontend:
    build: ./apps/frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./apps/frontend:/app
      - /app/node_modules
    depends_on:
      - api-gateway

  # API Gateway
  api-gateway:
    build: ./apps/services/api-gateway
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
    depends_on:
      - orchestrator-agent
      - calendar-service
      - user-settings-service

  # Orchestrator Agent (Pydantic AI)
  orchestrator-agent:
    build: ./apps/services/orchestrator-agent
    ports:
      - "8001:8001"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PYTHONPATH=/app

  # Calendar Service
  calendar-service:
    build: ./apps/services/calendar-service
    ports:
      - "8002:8002"
    environment:
      - PYTHONPATH=/app

  # User Settings Service  
  user-settings-service:
    build: ./apps/services/user-settings-service
    ports:
      - "8003:8003"
    environment:
      - PYTHONPATH=/app

  # Tool Factory Service
  tool-factory-service:
    build: ./apps/services/tool-factory-service
    ports:
      - "8004:8004"
    environment:
      - PYTHONPATH=/app

  # Redis (para cache e filas futuras)
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # PostgreSQL (para persistência futura)
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=agente_db
      - POSTGRES_USER=agente_user
      - POSTGRES_PASSWORD=agente_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
EOF

echo "📝 Criando arquivos de configuração..."

# .env.example
cat > .env.example << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql://agente_user:agente_pass@localhost:5432/agente_db

# Redis Configuration  
REDIS_URL=redis://localhost:6379

# API Configuration
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
EOF

# Dockerfile para o frontend
cat > apps/frontend/Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
EOF

# Makefile para facilitar o desenvolvimento
cat > Makefile << 'EOF'
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
EOF

# README.md
cat > README.md << 'EOF'
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
EOF

# .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
.pnp
.pnp.js

# Production builds
.next/
out/
build/
dist/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/
ENV/

# Database
*.db
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Docker
.dockerignore

# Temporary files
*.tmp
*.temp

# Coverage
coverage/
.coverage
.nyc_output

# Cache
.cache/
.parcel-cache/
.eslintcache
EOF

# Script de start para desenvolvimento
cat > start-dev.sh << 'EOF'
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

cd ../tool-factory-service && python main.py &
FACTORY_PID=$!

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
    kill $FRONTEND_PID $API_GATEWAY_PID $ORCHESTRATOR_PID $CALENDAR_PID $SETTINGS_PID $FACTORY_PID 2>/dev/null
    echo "✅ Serviços parados!"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Manter o script rodando
wait
EOF

# Tornar o script executável
chmod +x start-dev.sh

echo "🎉 Setup completo!"
echo ""
echo "📋 Próximos passos:"
echo "1. Entre na pasta do projeto: cd meu-agente-app"
echo "2. Crie o ambiente virtual: python3 -m venv .venv"
echo "3. Ative o ambiente: source .venv/bin/activate"
echo "4. Configure o projeto: make setup"
echo "5. Edite o arquivo .env com sua chave OpenAI"
echo "6. Instale dependências: make install-deps"
echo "7. Execute: ./start-dev.sh ou make dev"
echo ""
echo "🌟 URLs que estarão disponíveis:"
echo "  Frontend: http://localhost:3000"  
echo "  API: http://localhost:8000"
echo "  Docs: http://localhost:8000/docs"
echo ""
echo "✨ Projeto criado com sucesso!"2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ex: Assistente de Viagens"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Tipo</label>
                  <select
                    value={editingAgent.type || 'Pessoal'}
                    onChange={(e) => setEditingAgent({ ...editingAgent, type: e.target.value as 'Pessoal' | 'Profissional' })}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-