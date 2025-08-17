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
                    placeholder="Ex: Assistente de Viagens"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Tipo</label>
                  <select
                    value={editingAgent.type || 'Pessoal'}
                    onChange={(e) => setEditingAgent({ ...editingAgent, type: e.target.value as 'Pessoal' | 'Profissional' })}
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