import React, { useEffect, useMemo, useState } from 'react'
import { Brain, CheckCircle2, Clock, Package, Play, Square, Truck, XCircle } from 'lucide-react'

import { agenticApi, AgentAction, AgentLog, AgentStatus } from '../services/agenticApi'
import { supabaseService } from '../services/supabaseService'
import { useWebSocket } from '../hooks/useWebSocket'

interface SimulationStatus {
  is_running: boolean
  current_tick: number
  total_ticks: number
  tick_interval_seconds: number
  simulated_time: string
  last_tick_time?: string | null
  started_at?: string | null
  estimated_completion?: string | null
}

const AgenticDashboard: React.FC = () => {
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null)
  const [pendingActions, setPendingActions] = useState<AgentAction[]>([])
  const [agentLogs, setAgentLogs] = useState<AgentLog[]>([])
  const [simulationStatus, setSimulationStatus] = useState<SimulationStatus | null>(null)
  const [purchaseOrders, setPurchaseOrders] = useState<any[]>([])
  const [disposalOrders, setDisposalOrders] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'actions' | 'agents' | 'logs' | 'orders'>('actions')
  const [simMutationPending, setSimMutationPending] = useState(false)
  const wsUrl = process.env.REACT_APP_WS_URL
  const { data: wsData } = useWebSocket(wsUrl)

  const loadAgents = async () => {
    const status = await agenticApi.getAgentStatus()
    setAgentStatus(status)
  }

  const loadActions = async () => {
    const { actions } = await agenticApi.getAgentActions(100)
    setPendingActions(actions.filter((a) => a.status === 'pending'))
  }

  const loadLogs = async () => {
    const { logs } = await agenticApi.getAgentLogs(50)
    setAgentLogs(logs)
  }

  const loadSimulation = async () => {
      const status = await agenticApi.getSimulationStatus()
      setSimulationStatus(status.simulation || null)
    }

  const loadOrders = async () => {
    const [purchases, disposals] = await Promise.all([
      supabaseService.getPurchaseOrders(20),
      supabaseService.getDisposalOrders(20),
    ])
    setPurchaseOrders(purchases)
    setDisposalOrders(disposals)
  }

  useEffect(() => {
    const bootstrap = async () => {
      setLoading(true)
      await Promise.all([loadAgents(), loadActions(), loadLogs(), loadSimulation(), loadOrders()])
      setLoading(false)
    }
    bootstrap()
  }, [])

  useEffect(() => {
    const message = wsData as { type?: string; payload?: unknown } | null
    if (!message?.type) return
    if (message.type === 'agent_action') {
      loadActions()
    }
    if (message.type === 'simulation_update') {
      setSimulationStatus(message.payload as SimulationStatus)
    }
  }, [wsData])

  const simulationProgress = useMemo(() => {
    if (!simulationStatus || simulationStatus.total_ticks === 0) return 0
    return Math.round((simulationStatus.current_tick / simulationStatus.total_ticks) * 100)
  }, [simulationStatus])

  const handleApprove = async (actionId: string) => {
    await agenticApi.approveAction(actionId)
    loadActions()
  }

  const handleDecline = async (actionId: string) => {
    await agenticApi.declineAction(actionId)
    loadActions()
  }

  const toggleSimulation = async () => {
    if (!simulationStatus) return
    setSimMutationPending(true)
    try {
      if (simulationStatus.is_running) {
        await agenticApi.stopSimulation()
      } else {
        await agenticApi.startSimulation()
      }
      await loadSimulation()
    } finally {
      setSimMutationPending(false)
    }
  }

  const stepSimulation = async () => {
    setSimMutationPending(true)
    try {
      await agenticApi.stepSimulation()
      await loadSimulation()
    } finally {
      setSimMutationPending(false)
    }
  }

  if (loading || !agentStatus) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600" />
      </div>
    )
  }

  const agentsList = Object.entries(agentStatus.agents || {}).map(([key, value]) => ({
    key,
    ...value,
  }))

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm uppercase text-blue-600 font-semibold tracking-wide">Agentic AI</p>
          <h1 className="text-3xl font-bold text-gray-900">Autonomous Control Center</h1>
          <p className="text-gray-600">Approve actions, monitor agents, and run market simulations in one place.</p>
        </div>
        {simulationStatus ? (
          <button
            onClick={toggleSimulation}
            disabled={!simulationStatus || simMutationPending}
            className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium text-white shadow transition ${
              simulationStatus?.is_running ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'
            } ${simMutationPending ? 'opacity-60 cursor-not-allowed' : ''}`}
          >
            {simulationStatus?.is_running ? (
              <>
                <Square className="w-4 h-4 mr-2" />
                Stop Simulation
              </>
            ) : (
              <>
                <Play className="w-4 h-4 mr-2" />
                Start Simulation
              </>
            )}
          </button>
        ) : (
          <div className="px-4 py-2 rounded-lg text-sm font-medium text-gray-500 border border-gray-200">
            Simulation disabled
          </div>
        )}
      </div>

      {/* Simulation status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl border p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-sm text-gray-500">Simulation Status</p>
              <p className="text-2xl font-semibold text-gray-900">
                {simulationStatus ? (simulationStatus.is_running ? 'Running' : 'Paused') : 'Disabled'}
              </p>
            </div>
            <Brain className={`w-10 h-10 ${simulationStatus?.is_running ? 'text-green-500' : 'text-gray-400'}`} />
          </div>
          {simulationStatus ? (
            <div className="space-y-2">
              <div className="text-sm text-gray-600 flex items-center justify-between">
                <span>Current Tick</span>
                <span>{simulationStatus?.current_tick ?? 0} / {simulationStatus?.total_ticks ?? 0}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${simulationProgress}%` }} />
              </div>
              <div className="text-xs text-gray-500">
                Simulated time: {simulationStatus?.simulated_time ? new Date(simulationStatus.simulated_time).toLocaleString() : '—'}
              </div>
              <button
                onClick={stepSimulation}
                disabled={simMutationPending}
                className="w-full mt-3 border border-gray-300 rounded-lg py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                Process Single Tick
              </button>
            </div>
          ) : (
            <p className="text-sm text-gray-500">Simulation is disabled in this environment.</p>
          )}
        </div>

        <div className="bg-white rounded-xl border p-6 shadow-sm">
          <p className="text-sm text-gray-500">Pending Approvals</p>
          <p className="text-3xl font-semibold text-gray-900">{pendingActions.length}</p>
          <p className="text-xs text-gray-500">Actions waiting for human validation</p>
        </div>

        <div className="bg-white rounded-xl border p-6 shadow-sm">
          <p className="text-sm text-gray-500">Active Agents</p>
          <p className="text-3xl font-semibold text-gray-900">{agentStatus.total_agents}</p>
          <p className="text-xs text-gray-500">{agentStatus.agents_running ? 'Manager running' : 'Manager idle'}</p>
        </div>
      </div>

      {/* Tabs */}
      <div>
        <div className="flex space-x-6 border-b border-gray-200">
          {[
            { key: 'actions', label: `Pending Actions (${pendingActions.length})` },
            { key: 'agents', label: `Agents (${agentsList.length})` },
            { key: 'logs', label: 'Recent Logs' },
            { key: 'orders', label: 'Order Workflow' },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as typeof activeTab)}
              className={`pb-3 text-sm font-medium border-b-2 -mb-px transition-colors ${
                activeTab === tab.key ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="mt-6">
          {activeTab === 'actions' && (
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              {pendingActions.length === 0 && (
                <div className="col-span-full text-center text-gray-500 border border-dashed rounded-lg py-12">
                  No pending actions. Agents are waiting for new recommendations.
                </div>
              )}
              {pendingActions.map((action) => (
                <div key={action.id} className="bg-white border rounded-xl p-4 shadow-sm">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500 uppercase">{action.action_type}</p>
                      <p className="text-lg font-semibold text-gray-900">{action.payload?.item_name || action.payload?.item_id || action.action_type}</p>
                    </div>
                    <Clock className="w-5 h-5 text-gray-400" />
                  </div>
                  <p className="text-sm text-gray-600 mt-2">{action.payload?.reason || 'No reasoning provided'}</p>
                  <div className="flex items-center space-x-2 mt-4">
                    <button
                      onClick={() => handleApprove(action.id)}
                      className="flex-1 inline-flex items-center justify-center px-3 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg"
                    >
                      <CheckCircle2 className="w-4 h-4 mr-2" /> Approve
                    </button>
                    <button
                      onClick={() => handleDecline(action.id)}
                      className="flex-1 inline-flex items-center justify-center px-3 py-2 text-sm font-medium text-red-600 border border-red-200 rounded-lg hover:bg-red-50"
                    >
                      <XCircle className="w-4 h-4 mr-2" /> Decline
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'agents' && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agentsList.map((agent) => (
                <div key={agent.key} className="bg-white border rounded-xl p-4 shadow-sm">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-500">{agent.agent_type}</p>
                      <p className="text-lg font-semibold text-gray-900">{agent.key}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${agent.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                      {agent.is_active ? 'Active' : 'Idle'}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">Last action: {agent.last_action_time ? new Date(agent.last_action_time).toLocaleString() : '—'}</p>
                </div>
              ))}
            </div>
          )}

          {activeTab === 'logs' && (
            <div className="bg-white border rounded-xl p-4 shadow-sm">
              <div className="space-y-3 max-h-[420px] overflow-y-auto">
                {agentLogs.map((log) => (
                  <div key={log.id} className="border-l-4 border-blue-500 pl-3">
                    <p className="text-sm font-semibold text-gray-900">{log.action}</p>
                    <p className="text-xs text-gray-500">{new Date(log.timestamp).toLocaleString()}</p>
                    <p className="text-sm text-gray-600 mt-1">{log.details || log.status}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'orders' && (
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              <div className="bg-white border rounded-xl p-4 shadow-sm">
                <div className="flex items-center mb-3">
                  <Package className="w-5 h-5 text-blue-600 mr-2" />
                  <h3 className="text-lg font-semibold text-gray-900">Purchase Orders</h3>
                </div>
                <div className="space-y-3 max-h-[360px] overflow-y-auto">
                  {purchaseOrders.length === 0 && <p className="text-sm text-gray-500">No purchase orders found.</p>}
                  {purchaseOrders.map((order) => (
                    <div key={order.id} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-semibold text-gray-900">{order.item_name}</p>
                          <p className="text-xs text-gray-500">{order.order_type} · {order.quantity} units</p>
                        </div>
                        <span className="text-xs px-2 py-1 rounded-full bg-blue-50 text-blue-700 capitalize">{order.status}</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-2">{order.reason || 'No reason provided'}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white border rounded-xl p-4 shadow-sm">
                <div className="flex items-center mb-3">
                  <Truck className="w-5 h-5 text-amber-600 mr-2" />
                  <h3 className="text-lg font-semibold text-gray-900">Disposal Orders</h3>
                </div>
                <div className="space-y-3 max-h-[360px] overflow-y-auto">
                  {disposalOrders.length === 0 && <p className="text-sm text-gray-500">No disposal orders found.</p>}
                  {disposalOrders.map((order) => (
                    <div key={order.id} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-semibold text-gray-900">{order.item_id || 'Unknown Item'}</p>
                          <p className="text-xs text-gray-500">{order.disposal_type} · {order.quantity} units</p>
                        </div>
                        <span className="text-xs px-2 py-1 rounded-full bg-amber-50 text-amber-700 capitalize">{order.status}</span>
                      </div>
                      <p className="text-xs text-gray-600 mt-2">{order.reason || 'No reason provided'}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AgenticDashboard
