'use client'

import React, { useState, useEffect } from 'react'
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
  id?: number
  name: string
  type: string  // Permitir qualquer string em vez de apenas 'Pessoal' | 'Profissional'
  isDefault: boolean
  systemPrompt: string
  tools: Tool[]
  service_id?: string
  service_status?: string
}

export default function SettingsPage() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingAgent, setEditingAgent] = useState<Partial<Agent> | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  // Buscar agentes do backend ao carregar a página
  useEffect(() => {
    fetchAgents()
  }, [])

  const fetchAgents = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('http://localhost:8000/agents')
      if (response.ok) {
        const agentsData = await response.json()
        setAgents(agentsData)
        console.log('✅ Agentes carregados do backend:', agentsData)
      } else {
        console.error('❌ Erro ao buscar agentes:', response.status)
        alert('Erro ao carregar agentes. Verifique se o backend está funcionando.')
      }
    } catch (error) {
      console.error('❌ Erro de conexão:', error)
      alert('Erro de conexão com o backend')
    } finally {
      setIsLoading(false)
    }
  }

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

  const handleSave = async () => {
    if (!editingAgent?.name?.trim()) {
      alert('Nome do agente é obrigatório')
      return
    }

    try {
      setIsLoading(true)

      if ('id' in editingAgent && editingAgent.id) {
        // Atualizar agente existente (PUT)
        console.log('🔄 Atualizando agente:', editingAgent.id)
        const response = await fetch(`http://localhost:8000/agents/${editingAgent.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(editingAgent)
        })

        if (response.ok) {
          const updatedAgent = await response.json()
          setAgents(prev => prev.map(a => a.id === editingAgent.id ? updatedAgent : a))
          console.log('✅ Agente atualizado:', updatedAgent)
          alert('Agente atualizado com sucesso!')
        } else {
          const errorData = await response.json()
          console.error('❌ Erro ao atualizar agente:', errorData)
          
          // Tratar erros de validação do Pydantic
          if (errorData.detail && Array.isArray(errorData.detail)) {
            const validationErrors = errorData.detail.map((err: any) => 
              `${err.loc.join('.')}: ${err.msg}`
            ).join('\n')
            alert(`Erro de validação:\n${validationErrors}`)
          } else {
            alert(`Erro ao atualizar agente: ${errorData.detail || JSON.stringify(errorData)}`)
          }
        }
      } else {
        // Criar novo agente (POST)
        console.log('➕ Criando novo agente:', editingAgent)
        const response = await fetch('http://localhost:8000/agents', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: editingAgent.name,
            type: editingAgent.type,
            systemPrompt: editingAgent.systemPrompt,
            tools: editingAgent.tools || [],
            isDefault: false
          })
        })

        if (response.ok) {
          const newAgent = await response.json()
          setAgents(prev => [...prev, newAgent])
          console.log('✅ Agente criado:', newAgent)
          alert('Agente criado com sucesso!')
        } else {
          const errorData = await response.json()
          console.error('❌ Erro ao criar agente:', errorData)
          
          // Tratar erros de validação do Pydantic
          if (errorData.detail && Array.isArray(errorData.detail)) {
            const validationErrors = errorData.detail.map((err: any) => 
              `${err.loc.join('.')}: ${err.msg}`
            ).join('\n')
            alert(`Erro de validação:\n${validationErrors}`)
          } else {
            alert(`Erro ao criar agente: ${errorData.detail || JSON.stringify(errorData)}`)
          }
        }
      }

      setIsModalOpen(false)
      setEditingAgent(null)
    } catch (error) {
      console.error('❌ Erro de conexão:', error)
      alert('Erro de conexão com o backend')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    const agent = agents.find(a => a.id === id)
    if (agent?.isDefault) {
      alert('Não é possível deletar agentes padrão')
      return
    }
    
    if (!confirm('Tem certeza que deseja deletar este agente?')) return

    try {
      setIsLoading(true)
      console.log('🗑️ Deletando agente:', id)
      
      const response = await fetch(`http://localhost:8000/agents/${id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setAgents(prev => prev.filter(a => a.id !== id))
        console.log('✅ Agente deletado:', id)
        alert('Agente deletado com sucesso!')
      } else {
        const errorData = await response.json()
        console.error('❌ Erro ao deletar agente:', errorData)
        alert(`Erro ao deletar agente: ${errorData.detail || 'Erro desconhecido'}`)
      }
    } catch (error) {
      console.error('❌ Erro de conexão:', error)
      alert('Erro de conexão com o backend')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDuplicate = async (id: number) => {
    try {
      setIsLoading(true)
      console.log('📄 Duplicando agente:', id)
      
      const response = await fetch(`http://localhost:8000/agents/${id}/duplicate`, {
        method: 'POST'
      })

      if (response.ok) {
        const duplicatedAgent = await response.json()
        setAgents(prev => [...prev, duplicatedAgent])
        console.log('✅ Agente duplicado:', duplicatedAgent)
        alert('Agente duplicado com sucesso!')
      } else {
        const errorData = await response.json()
        console.error('❌ Erro ao duplicar agente:', errorData)
        alert(`Erro ao duplicar agente: ${errorData.detail || 'Erro desconhecido'}`)
      }
    } catch (error) {
      console.error('❌ Erro de conexão:', error)
      alert('Erro de conexão com o backend')
    } finally {
      setIsLoading(false)
    }
  }

  const addTool = () => {
    if (!editingAgent) return
    setEditingAgent({
      ...editingAgent,
      tools: [
        ...(editingAgent.tools || []),
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

  if (isLoading && agents.length === 0) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p>Carregando agentes...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link 
              href="/chat"
              className="flex items-center space-x-2 text-gray-300 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span>Voltar ao Chat</span>
            </Link>
            <div>
              <h1 className="text-2xl font-bold">Configurações</h1>
              <p className="text-gray-400">Gerencie seus agentes e ferramentas</p>
            </div>
          </div>
          <button
            onClick={openCreateModal}
            disabled={isLoading}
            className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            <span>Novo Agente</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">Meus Agentes</h2>
          
          {isLoading && agents.length > 0 && (
            <div className="mb-4 p-3 bg-blue-900/50 border border-blue-700 rounded-lg">
              <p className="text-blue-300">Processando...</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent) => (
              <div key={agent.id} className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-lg">{agent.name}</h3>
                    <div className="flex items-center space-x-2 mt-1">
                      <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                        agent.type === 'Pessoal' 
                          ? 'bg-green-900 text-green-300' 
                          : 'bg-blue-900 text-blue-300'
                      }`}>
                        {agent.type}
                      </span>
                      {agent.isDefault && (
                        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-900 text-yellow-300">
                          Padrão
                        </span>
                      )}
                      {agent.service_status && (
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                          agent.service_status === 'active' || agent.service_status === 'created' 
                            ? 'bg-green-900 text-green-300'
                            : agent.service_status === 'error'
                            ? 'bg-red-900 text-red-300'
                            : 'bg-gray-700 text-gray-300'
                        }`}>
                          {agent.service_status}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex space-x-1">
                    <button
                      onClick={() => openEditModal(agent)}
                      disabled={isLoading}
                      className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded disabled:opacity-50"
                      title="Editar"
                    >
                      <Edit className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDuplicate(agent.id!)}
                      disabled={isLoading}
                      className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded disabled:opacity-50"
                      title="Duplicar"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                    {!agent.isDefault && (
                      <button
                        onClick={() => handleDelete(agent.id!)}
                        disabled={isLoading}
                        className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded disabled:opacity-50"
                        title="Deletar"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
                
                <p className="text-gray-400 text-sm mb-3 line-clamp-2">
                  {agent.systemPrompt}
                </p>
                
                <div className="text-xs text-gray-500">
                  {agent.tools.length} ferramenta(s) configurada(s)
                </div>
              </div>
            ))}
          </div>

          {agents.length === 0 && !isLoading && (
            <div className="text-center py-12">
              <p className="text-gray-400 mb-4">Nenhum agente encontrado</p>
              <button
                onClick={openCreateModal}
                className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg mx-auto"
              >
                <Plus className="w-5 h-5" />
                <span>Criar primeiro agente</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b border-gray-700">
              <h2 className="text-xl font-semibold">
                {editingAgent?.id ? 'Editar Agente' : 'Criar Novo Agente'}
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                disabled={isLoading}
                className="text-gray-400 hover:text-white disabled:opacity-50"
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
                    value={editingAgent?.name || ''}
                    onChange={(e) => setEditingAgent({ ...editingAgent, name: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ex: Assistente de Viagens"
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Tipo</label>
                  <input
                    type="text"
                    value={editingAgent?.type || ''}
                    onChange={(e) => setEditingAgent({ ...editingAgent, type: e.target.value })}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ex: Pessoal, Profissional, Pesquisa, Educacional, etc."
                    disabled={isLoading}
                  />
                </div>
              </div>

              {/* System Prompt */}
              <div>
                <label className="block text-sm font-medium mb-2">Persona e Objetivo (System Prompt)</label>
                <textarea
                  value={editingAgent?.systemPrompt || ''}
                  onChange={(e) => setEditingAgent({ ...editingAgent, systemPrompt: e.target.value })}
                  rows={4}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Descreva como o agente deve se comportar e qual sua função principal..."
                  disabled={isLoading}
                />
              </div>

              {/* Tools */}
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Ferramentas</h3>
                  <button
                    onClick={addTool}
                    disabled={isLoading}
                    type="button"
                    className="flex items-center space-x-1 text-blue-400 hover:text-blue-300 disabled:opacity-50"
                  >
                    <PlusCircle className="w-5 h-5" />
                    <span>Adicionar Ferramenta</span>
                  </button>
                </div>

                {editingAgent?.tools?.map((tool, toolIndex) => (
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
                          disabled={isLoading}
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
                          disabled={isLoading}
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
                        disabled={isLoading}
                      />
                    </div>

                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <label className="block text-sm font-medium">Parâmetros</label>
                        <button
                          onClick={() => addParameter(toolIndex)}
                          disabled={isLoading}
                          type="button"
                          className="text-sm text-blue-400 hover:text-blue-300 disabled:opacity-50"
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
                            disabled={isLoading}
                          />
                          <select
                            value={param.type}
                            onChange={(e) => {
                              const newParams = [...tool.parameters]
                              newParams[paramIndex] = { ...param, type: e.target.value as any }
                              updateTool(toolIndex, 'parameters', newParams)
                            }}
                            className="px-2 py-1 bg-gray-600 border border-gray-500 rounded text-sm"
                            disabled={isLoading}
                          >
                            <option value="texto">Texto</option>
                            <option value="numero">Número</option>
                            <option value="data">Data</option>
                            <option value="booleano">Booleano</option>
                          </select>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="flex justify-end space-x-3 pt-4 border-t border-gray-700">
                <button
                  onClick={() => setIsModalOpen(false)}
                  disabled={isLoading}
                  className="px-4 py-2 text-gray-400 hover:text-white disabled:opacity-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleSave}
                  disabled={isLoading}
                  className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 px-4 py-2 rounded-lg"
                >
                  {isLoading && <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>}
                  <Save className="w-4 h-4" />
                  <span>{isLoading ? 'Salvando...' : 'Salvar Agente'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}