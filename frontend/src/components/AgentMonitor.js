import React, { useState, useEffect } from 'react';
import { Cpu, Play, Square, RotateCcw, Eye, Clock, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { supabaseService } from '../services/supabaseService.ts';

const AgentMonitor = () => {
  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentLogs, setAgentLogs] = useState([]);
  const [pendingDecisions, setPendingDecisions] = useState([]);
  const [decisionHistory, setDecisionHistory] = useState([]);

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedAgent) {
      fetchPendingDecisions(selectedAgent.agent_id);
      fetchDecisionHistory(selectedAgent.agent_id);
    }
  }, [selectedAgent]);

  const fetchAgents = async () => {
    try {
      const agents = await supabaseService.getAgents();
      setAgents(agents.agents || []);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const fetchAgentLogs = async (agentId) => {
    try {
      const logs = await supabaseService.getAgentLogs(agentId);
      setAgentLogs(logs.logs || []);
    } catch (error) {
      console.error('Error fetching agent logs:', error);
    }
  };

  const fetchPendingDecisions = async (agentId) => {
    try {
      const response = await fetch(`/api/v1/agents/${agentId}/decisions/pending`);
      const data = await response.json();
      setPendingDecisions(data.decisions || []);
    } catch (error) {
      console.error('Error fetching pending decisions:', error);
    }
  };

  const fetchDecisionHistory = async (agentId) => {
    try {
      const response = await fetch(`/api/v1/agents/${agentId}/decisions/history`);
      const data = await response.json();
      setDecisionHistory(data.decisions || []);
    } catch (error) {
      console.error('Error fetching decision history:', error);
    }
  };

  const approveDecision = async (agentId, decisionId) => {
    try {
      const response = await fetch(`/api/v1/agents/${agentId}/decisions/${decisionId}/approve`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchPendingDecisions(agentId);
        fetchDecisionHistory(agentId);
      }
    } catch (error) {
      console.error('Error approving decision:', error);
    }
  };

  const declineDecision = async (agentId, decisionId) => {
    try {
      const response = await fetch(`/api/v1/agents/${agentId}/decisions/${decisionId}/decline`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchPendingDecisions(agentId);
        fetchDecisionHistory(agentId);
      }
    } catch (error) {
      console.error('Error declining decision:', error);
    }
  };

  const controlAgent = async (agentId, action) => {
    try {
      const result = await supabaseService.agentAction(agentId, action);
      if (result.ok) {
        fetchAgents();
      }
    } catch (error) {
      console.error(`Error ${action} agent:`, error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'text-green-600 bg-green-100';
      case 'stopped': return 'text-gray-600 bg-gray-100';
      case 'starting': return 'text-blue-600 bg-blue-100';
      case 'stopping': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getActionTypeColor = (actionType) => {
    switch (actionType) {
      case 'restock': return 'text-blue-600 bg-blue-100';
      case 'pricing': return 'text-green-600 bg-green-100';
      case 'route': return 'text-purple-600 bg-purple-100';
      case 'dispatch': return 'text-orange-600 bg-orange-100';
      case 'forecasting': return 'text-indigo-600 bg-indigo-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Agent Monitor</h1>
        <p className="text-gray-600 mt-2">Monitor and control autonomous AI agents</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agents List */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Active Agents</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {agents.map((agent) => (
                  <div key={agent.agent_key} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Cpu className="h-5 w-5 text-blue-600" />
                        <div>
                          <h3 className="font-medium text-gray-900">{agent.name}</h3>
                          <p className="text-sm text-gray-600">{agent.agent_type}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(agent.status)}`}>
                          {agent.status}
                        </span>
                        <button
                          onClick={() => setSelectedAgent(agent)}
                          className="p-1 text-gray-400 hover:text-gray-600"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                    <div className="mt-3 flex items-center justify-between text-sm text-gray-600">
                      <span>Tasks: {agent.tasks_completed} completed, {agent.tasks_failed} failed</span>
                      <span>Response: {agent.average_response_time || 0}ms</span>
                    </div>
                    <div className="mt-3 flex space-x-2">
                      <button
                        onClick={() => controlAgent(agent.agent_key, 'start')}
                        disabled={agent.status === 'running'}
                        className="flex items-center px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                      >
                        <Play className="h-3 w-3 mr-1" />
                        Start
                      </button>
                      <button
                        onClick={() => controlAgent(agent.agent_key, 'stop')}
                        disabled={agent.status === 'stopped'}
                        className="flex items-center px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
                      >
                        <Square className="h-3 w-3 mr-1" />
                        Stop
                      </button>
                      <button
                        onClick={() => controlAgent(agent.agent_key, 'restart')}
                        className="flex items-center px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        <RotateCcw className="h-3 w-3 mr-1" />
                        Restart
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Pending Decisions */}
          {selectedAgent && (
            <div className="bg-white rounded-lg shadow mt-6">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">Pending Decisions</h2>
                <p className="text-sm text-gray-600">Review and approve autonomous decisions</p>
              </div>
              <div className="p-6">
                {pendingDecisions.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No pending decisions</p>
                ) : (
                  <div className="space-y-4">
                    {pendingDecisions.map((decision) => (
                      <div key={decision.decision_id} className="border rounded-lg p-4 bg-yellow-50">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getActionTypeColor(decision.action_type)}`}>
                                {decision.action_type.toUpperCase()}
                              </span>
                              <span className="text-sm text-gray-500">
                                Confidence: {Math.round(decision.confidence * 100)}%
                              </span>
                            </div>
                            <h4 className="font-medium text-gray-900 mb-2">{decision.reasoning}</h4>
                            <div className="text-sm text-gray-600 mb-3">
                              <p><strong>Impact:</strong> ${decision.estimated_impact.cost} • {decision.estimated_impact.efficiency_gain} efficiency gain</p>
                              <p><strong>Risk:</strong> {decision.estimated_impact.risk_level}</p>
                              <p><strong>Generated:</strong> {formatTimestamp(decision.timestamp)}</p>
                            </div>
                            <div className="text-xs text-gray-500 bg-white p-2 rounded border">
                              <strong>Parameters:</strong> {JSON.stringify(decision.parameters, null, 2)}
                            </div>
                          </div>
                          <div className="flex flex-col space-y-2 ml-4">
                            <button
                              onClick={() => approveDecision(selectedAgent.agent_key, decision.decision_id)}
                              className="flex items-center px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
                            >
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Approve
                            </button>
                            <button
                              onClick={() => declineDecision(selectedAgent.agent_key, decision.decision_id)}
                              className="flex items-center px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                            >
                              <XCircle className="h-3 w-3 mr-1" />
                              Decline
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Agent Details */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Agent Details</h2>
            </div>
            <div className="p-6">
              {selectedAgent ? (
                <div>
                  <h3 className="font-medium text-gray-900 mb-2">{selectedAgent.name}</h3>
                  <div className="space-y-3 text-sm">
                    <div>
                      <span className="text-gray-600">Type:</span>
                      <span className="ml-2 font-medium">{selectedAgent.agent_type}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Status:</span>
                      <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedAgent.status)}`}>
                        {selectedAgent.status}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Last Heartbeat:</span>
                      <span className="ml-2 font-medium">
                        {selectedAgent.last_heartbeat ? new Date(selectedAgent.last_heartbeat).toLocaleTimeString() : 'Never'}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-600">Tasks Completed:</span>
                      <span className="ml-2 font-medium">{selectedAgent.tasks_completed}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Tasks Failed:</span>
                      <span className="ml-2 font-medium">{selectedAgent.tasks_failed}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Avg Response Time:</span>
                      <span className="ml-2 font-medium">{selectedAgent.average_response_time || 0}ms</span>
                    </div>
                  </div>
                  <button
                    onClick={() => fetchAgentLogs(selectedAgent.agent_key)}
                    className="mt-4 w-full flex items-center justify-center px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    <Clock className="h-4 w-4 mr-2" />
                    View Logs
                  </button>
                </div>
              ) : (
                <p className="text-gray-500 text-center">Select an agent to view details</p>
              )}
            </div>
          </div>

          {/* Decision History */}
          {selectedAgent && decisionHistory.length > 0 && (
            <div className="bg-white rounded-lg shadow mt-6">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Recent Decisions</h3>
              </div>
              <div className="p-6 max-h-64 overflow-y-auto">
                <div className="space-y-2">
                  {decisionHistory.slice(0, 5).map((decision) => (
                    <div key={decision.decision_id} className="text-sm border-l-2 border-blue-500 pl-3">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <span className={`px-1 py-0.5 rounded text-xs font-medium ${getActionTypeColor(decision.action_type)}`}>
                              {decision.action_type}
                            </span>
                            <span className={`px-1 py-0.5 rounded text-xs font-medium ${
                              decision.approval_status === 'approved' ? 'text-green-600 bg-green-100' :
                              decision.approval_status === 'denied' ? 'text-red-600 bg-red-100' :
                              'text-yellow-600 bg-yellow-100'
                            }`}>
                              {decision.approval_status}
                            </span>
                          </div>
                          <p className="text-gray-600 mt-1 text-xs">{decision.reasoning.substring(0, 80)}...</p>
                        </div>
                        <span className="text-gray-500 text-xs">{formatTimestamp(decision.timestamp)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Agent Logs */}
          {agentLogs.length > 0 && (
            <div className="bg-white rounded-lg shadow mt-6">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Recent Logs</h3>
              </div>
              <div className="p-6 max-h-64 overflow-y-auto">
                <div className="space-y-2">
                  {agentLogs.slice(0, 10).map((log, index) => (
                    <div key={index} className="text-sm border-l-2 border-blue-500 pl-3">
                      <div className="flex justify-between">
                        <span className="font-medium">{log.action}</span>
                        <span className="text-gray-500">{new Date(log.timestamp).toLocaleTimeString()}</span>
                      </div>
                      <div className="text-gray-600 mt-1">
                        Status: <span className={log.status === 'completed' ? 'text-green-600' : 'text-red-600'}>{log.status}</span>
                      </div>
                      {log.error_message && (
                        <div className="text-red-600 text-xs mt-1">{log.error_message}</div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AgentMonitor; 