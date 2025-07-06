import React, { useState, useEffect } from 'react';
import { Cpu, Play, Square, RotateCcw, Eye, Clock, CheckCircle, XCircle, AlertTriangle, Brain, Zap, TrendingUp, Package, Truck, DollarSign } from 'lucide-react';
import { supabaseService } from '../services/supabaseService.ts';

const AgentMonitor = () => {
  const [agents, setAgents] = useState([]);
  const [pendingDecisions, setPendingDecisions] = useState([]);
  const [decisionHistory, setDecisionHistory] = useState([]);
  const [activeTab, setActiveTab] = useState('decisions'); // 'decisions', 'agents', 'history'

  // Always use the first agent as the default
  const selectedAgent = agents.length > 0 ? agents[0] : null;

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedAgent) {
      fetchPendingDecisions(selectedAgent.agent_key);
      fetchDecisionHistory(selectedAgent.agent_key);
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
      case 'restock': return 'text-blue-600 bg-blue-100 border-blue-200';
      case 'pricing': return 'text-green-600 bg-green-100 border-green-200';
      case 'route': return 'text-purple-600 bg-purple-100 border-purple-200';
      case 'dispatch': return 'text-orange-600 bg-orange-100 border-orange-200';
      case 'forecasting': return 'text-indigo-600 bg-indigo-100 border-indigo-200';
      default: return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getActionIcon = (actionType) => {
    switch (actionType) {
      case 'restock': return <Package className="h-5 w-5" />;
      case 'pricing': return <DollarSign className="h-5 w-5" />;
      case 'route': return <Truck className="h-5 w-5" />;
      case 'dispatch': return <Zap className="h-5 w-5" />;
      case 'forecasting': return <TrendingUp className="h-5 w-5" />;
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

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <Brain className="h-8 w-8 text-blue-600 mr-3" />
              AI Agent Monitor
            </h1>
            <p className="text-gray-600 mt-2">Review and approve autonomous AI decisions</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-sm text-gray-600">Active Agent</div>
              <div className="font-semibold text-gray-900">
                {selectedAgent ? selectedAgent.name : 'None Available'}
              </div>
            </div>
            <div className={`w-3 h-3 ${selectedAgent ? 'bg-green-500' : 'bg-gray-300'} rounded-full animate-pulse`}></div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('decisions')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'decisions'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Pending Decisions ({pendingDecisions.length})
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'history'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Decision History ({decisionHistory.length})
            </button>
            <button
              onClick={() => setActiveTab('agents')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'agents'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Agent Status
            </button>
          </nav>
        </div>
      </div>

      {/* Content based on active tab */}
      {!selectedAgent ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <AlertTriangle className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Agent Available</h3>
          <p className="text-gray-600">
            No agent is currently running. Please check your backend configuration.
          </p>
        </div>
      ) : (
        <>
          {activeTab === 'decisions' && (
            <div className="space-y-6">
              {pendingDecisions.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-lg shadow">
                  <Brain className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Pending Decisions</h3>
                  <p className="text-gray-600">
                    The AI agent is currently analyzing the system. New decisions will appear here when ready for review.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {pendingDecisions.map((decision) => (
                    <div key={decision.decision_id} className="bg-white rounded-lg shadow-lg border-2 border-yellow-200 hover:border-yellow-300 transition-all duration-200">
                      {/* Decision Header */}
                      <div className="p-6 border-b border-gray-200">
                        <div className="flex items-center justify-between mb-4">
                          <div className="flex items-center space-x-3">
                            <div className={`p-2 rounded-lg ${getActionTypeColor(decision.action_type)}`}>
                              {getActionIcon(decision.action_type)}
                            </div>
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900 capitalize">
                                {decision.action_type} Decision
                              </h3>
                              <p className="text-sm text-gray-500">
                                Generated {formatTimestamp(decision.timestamp)}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className={`text-sm font-medium ${getConfidenceColor(decision.confidence)}`}>
                              {Math.round(decision.confidence * 100)}% Confidence
                            </div>
                            <div className={`text-xs px-2 py-1 rounded-full ${getRiskColor(decision.estimated_impact.risk_level)}`}>
                              {decision.estimated_impact.risk_level} Risk
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Decision Content */}
                      <div className="p-6">
                        <div className="mb-4">
                          <h4 className="font-medium text-gray-900 mb-2">Reasoning</h4>
                          <p className="text-gray-700 text-sm leading-relaxed">{decision.reasoning}</p>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mb-6">
                          <div className="bg-gray-50 p-3 rounded-lg">
                            <div className="text-xs text-gray-500 uppercase tracking-wide">Estimated Cost</div>
                            <div className="text-lg font-semibold text-gray-900">${decision.estimated_impact.cost}</div>
                          </div>
                          <div className="bg-gray-50 p-3 rounded-lg">
                            <div className="text-xs text-gray-500 uppercase tracking-wide">Efficiency Gain</div>
                            <div className="text-lg font-semibold text-green-600">{decision.estimated_impact.efficiency_gain}</div>
                          </div>
                        </div>

                        <div className="mb-6">
                          <h4 className="font-medium text-gray-900 mb-2">Parameters</h4>
                          <div className="bg-gray-50 p-3 rounded-lg text-xs font-mono text-gray-700 max-h-24 overflow-y-auto">
                            {JSON.stringify(decision.parameters, null, 2)}
                          </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex space-x-3">
                          <button
                            onClick={() => approveDecision(selectedAgent.agent_key, decision.decision_id)}
                            className="flex-1 flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200 font-medium"
                          >
                            <CheckCircle className="h-5 w-5 mr-2" />
                            Approve Decision
                          </button>
                          <button
                            onClick={() => declineDecision(selectedAgent.agent_key, decision.decision_id)}
                            className="flex-1 flex items-center justify-center px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200 font-medium"
                          >
                            <XCircle className="h-5 w-5 mr-2" />
                            Decline Decision
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-xl font-semibold text-gray-900">Decision History</h2>
              </div>
              <div className="p-6">
                {decisionHistory.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No decision history available</p>
                ) : (
                  <div className="space-y-4">
                    {decisionHistory.slice(0, 10).map((decision) => (
                      <div key={decision.decision_id} className="border rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={`p-2 rounded-lg ${getActionTypeColor(decision.action_type)}`}>
                              {getActionIcon(decision.action_type)}
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900 capitalize">{decision.action_type}</h4>
                              <p className="text-sm text-gray-600">{decision.reasoning.substring(0, 80)}...</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                              decision.approval_status === 'approved' ? 'text-green-600 bg-green-100' :
                              decision.approval_status === 'denied' ? 'text-red-600 bg-red-100' :
                              'text-yellow-600 bg-yellow-100'
                            }`}>
                              {decision.approval_status}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">{formatTimestamp(decision.timestamp)}</div>
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
                  
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <div className="text-sm text-gray-600">Tasks Completed</div>
                      <div className="text-lg font-semibold text-gray-900">{agent.tasks_completed}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Tasks Failed</div>
                      <div className="text-lg font-semibold text-red-600">{agent.tasks_failed}</div>
                    </div>
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => controlAgent(agent.agent_key, 'start')}
                      disabled={agent.status === 'running'}
                      className="flex-1 px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
                    >
                      Start
                    </button>
                    <button
                      onClick={() => controlAgent(agent.agent_key, 'stop')}
                      disabled={agent.status === 'stopped'}
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
        </>
      )}
    </div>
  );
};

export default AgentMonitor; 