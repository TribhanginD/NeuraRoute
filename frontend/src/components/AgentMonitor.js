import React, { useState, useEffect } from 'react';
import { Cpu, Play, Square, RotateCcw, Eye, Clock, CheckCircle, XCircle, AlertTriangle, Brain, Zap, TrendingUp, Package, Truck, DollarSign } from 'lucide-react';
import { agenticWebSocket } from '../services/agenticWebSocket.ts';

const AgentMonitor = () => {
  const [agents, setAgents] = useState([]);
  const [pendingActions, setPendingActions] = useState([]);
  const [actionHistory, setActionHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('actions'); // 'actions', 'agents', 'history', 'logs'
  const [agentLogs, setAgentLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAgents();
    fetchActions();
    const interval = setInterval(() => {
      fetchAgents();
      fetchActions();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeTab === 'logs') {
      fetchLogs();
    }
  }, [activeTab]);

  const fetchAgents = async () => {
    try {
      const response = await agenticWebSocket.getAgentStatus();
      if (response.agents) {
        const agentsList = Object.entries(response.agents).map(([key, agent]) => ({
          agent_key: key,
          name: key.charAt(0).toUpperCase() + key.slice(1) + ' Agent',
          agent_type: agent.agent_type,
          status: agent.is_active ? 'active' : 'inactive',
          is_active: agent.is_active
        }));
        setAgents(agentsList);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching agents:', error);
      setLoading(false);
    }
  };

  const fetchActions = async () => {
    try {
      const response = await agenticWebSocket.getAgentActions();
      if (response.actions) {
        setPendingActions(response.actions.filter(action => action.status === 'pending'));
        setActionHistory(response.actions.filter(action => action.status !== 'pending'));
      }
    } catch (error) {
      console.error('Error fetching actions:', error);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await agenticWebSocket.getAgentLogs();
      if (response.logs) {
        setAgentLogs(response.logs);
      }
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  };

  const approveAction = async (actionId) => {
    try {
      await agenticWebSocket.approveAction(actionId);
      fetchActions();
    } catch (error) {
      console.error('Error approving action:', error);
    }
  };

  const declineAction = async (actionId) => {
    try {
      await agenticWebSocket.declineAction(actionId);
      fetchActions();
    } catch (error) {
      console.error('Error declining action:', error);
    }
  };

  const controlAgent = async (agentType, action) => {
    try {
      await agenticWebSocket.triggerAgent(agentType, action);
      fetchAgents();
    } catch (error) {
      console.error('Error controlling agent:', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
      case 'running':
        return 'bg-green-100 text-green-800';
      case 'inactive':
      case 'stopped':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getActionTypeColor = (actionType) => {
    switch (actionType) {
      case 'reorder':
        return 'bg-blue-100 text-blue-600';
      case 'route_optimization':
        return 'bg-green-100 text-green-600';
      case 'price_adjustment':
        return 'bg-purple-100 text-purple-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getActionIcon = (actionType) => {
    switch (actionType) {
      case 'reorder': return <Package className="h-5 w-5" />;
      case 'price_adjustment': return <DollarSign className="h-5 w-5" />;
      case 'route_optimization': return <Truck className="h-5 w-5" />;
      default: return <Brain className="h-5 w-5" />;
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.7) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'low': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'high': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 flex flex-col h-full min-h-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Agent Monitor</h1>
        <p className="text-gray-600 mt-2">Monitor and control AI agents</p>
        <div className="mt-4">
          <button
            onClick={() => controlAgent('inventory', 'trigger_decision')}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors duration-200"
          >
            <Brain className="w-4 h-4 mr-2" />
            Trigger Agent Decision
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('actions')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'actions'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Pending Actions ({pendingActions.length})
          </button>
          <button
            onClick={() => setActiveTab('agents')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'agents'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Agents ({agents.length})
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'history'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            History ({actionHistory.length})
          </button>
          <button
            onClick={() => setActiveTab('logs')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'logs'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Logs
          </button>
        </nav>
      </div>

      {/* Content */}
      <div className="flex-1 min-h-0">
        {activeTab === 'actions' && (
          <div className="bg-white rounded-lg shadow flex flex-col h-full min-h-0">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Pending Actions</h2>
            </div>
            <div className="flex-1 min-h-0 overflow-y-auto max-h-[calc(100vh-180px)] p-6">
              {pendingActions.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No pending actions</p>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 min-h-0">
                  {pendingActions.map((action) => (
                    <div key={action.id} className="bg-white rounded-lg shadow-lg border-2 border-yellow-200 hover:border-yellow-300 transition-all duration-200 flex flex-col h-full min-h-0">
                      {/* Action Header */}
                      <div className="p-6 border-b border-gray-200">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <div className={`p-2 rounded-lg ${getActionTypeColor(action.action_type)}`}>
                              {getActionIcon(action.action_type)}
                            </div>
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900 capitalize">
                                {action.action_type.replace('_', ' ')} Action
                              </h3>
                              <p className="text-sm text-gray-500">
                                Generated {formatTimestamp(action.created_at)}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm font-medium text-gray-600">
                              Agent: {action.agent_id}
                            </div>
                            <div className={`text-xs px-2 py-1 rounded-full ${getActionTypeColor(action.action_type)}`}>
                              {action.status}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Action Content */}
                      <div className="p-6 flex-1 overflow-auto min-h-0">
                        <div className="mb-4">
                          <h4 className="font-medium text-gray-900 mb-2">Action Details</h4>
                          <div className="bg-gray-50 p-3 rounded-lg text-sm text-gray-700 overflow-x-auto max-h-40">
                            <pre className="whitespace-pre-wrap break-all">{JSON.stringify(action.payload, null, 2)}</pre>
                          </div>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex space-x-3 p-4 border-t border-gray-100 bg-gray-50">
                        <button
                          onClick={() => approveAction(action.id)}
                          className="flex-1 flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 font-medium"
                        >
                          <CheckCircle className="h-5 w-5 mr-2" />
                          Approve Action
                        </button>
                        <button
                          onClick={() => declineAction(action.id)}
                          className="flex-1 flex items-center justify-center px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 font-medium"
                        >
                          <XCircle className="h-5 w-5 mr-2" />
                          Decline Action
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Action History</h2>
            </div>
            <div className="p-6">
              {actionHistory.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No action history available</p>
              ) : (
                <div className="space-y-4">
                  {actionHistory.slice(0, 10).map((action) => (
                    <div key={action.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`p-2 rounded-lg ${getActionTypeColor(action.action_type)}`}>
                            {getActionIcon(action.action_type)}
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-900 capitalize">{action.action_type.replace('_', ' ')}</h4>
                            <p className="text-sm text-gray-600">Agent: {action.agent_id}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                            action.status === 'approved' ? 'text-green-600 bg-green-100' :
                            action.status === 'declined' ? 'text-red-600 bg-red-100' :
                            'text-yellow-600 bg-yellow-100'
                          }`}>
                            {action.status}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">{formatTimestamp(action.created_at)}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {agents.map((agent) => (
              <div key={agent.agent_key} className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Cpu className="h-6 w-6 text-blue-600" />
                    <div>
                      <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                      <p className="text-sm text-gray-600">{agent.agent_type}</p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(agent.status)}`}>
                    {agent.status}
                  </span>
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => controlAgent(agent.agent_key, 'start')}
                    disabled={agent.status === 'active'}
                    className="flex-1 px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                  >
                    Start
                  </button>
                  <button
                    onClick={() => controlAgent(agent.agent_key, 'stop')}
                    disabled={agent.status === 'inactive'}
                    className="flex-1 px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                  >
                    Stop
                  </button>
                  <button
                    onClick={() => controlAgent(agent.agent_key, 'restart')}
                    className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm font-medium"
                  >
                    Restart
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'logs' && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Agent Logs</h2>
            </div>
            <div className="p-6 max-h-96 overflow-y-auto">
              {agentLogs.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No logs available</p>
              ) : (
                <ul className="space-y-2">
                  {agentLogs.map((log) => (
                    <li key={log.id} className="border-l-2 border-blue-500 pl-3">
                      <div className="flex justify-between">
                        <span className="font-medium">[{formatTimestamp(log.created_at)}] {log.log_type}</span>
                      </div>
                      <div className="text-gray-700 mt-1">{log.message}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentMonitor; 