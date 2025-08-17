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
