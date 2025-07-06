import React, { useEffect, useState, useCallback } from 'react';
import {
  PendingAction,
  AgenticSystemStatus,
  PendingActionsResponse,
  AgentPlanResponse,
  ActionHistoryResponse,
  AgenticWebSocketMessage,
} from '../types/agentic';
import { formatTimestamp } from '../types/agentic';
import { agenticWebSocket, WebSocketEventHandler } from '../services/agenticWebSocket';
import { supabaseService } from '../services/supabaseService.ts';

const AgenticAI: React.FC = () => {
  const [pendingActions, setPendingActions] = useState<PendingAction[]>([]);
  const [systemStatus, setSystemStatus] = useState<AgenticSystemStatus | null>(null);
  const [agentPlan, setAgentPlan] = useState<AgentPlanResponse | null>(null);
  const [actionHistory, setActionHistory] = useState<ActionHistoryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wsStatus, setWsStatus] = useState('disconnected');

  useEffect(() => {
    fetchAll();
  }, []);

  const fetchAll = async () => {
    setPendingActions(await supabaseService.getPendingActions());
    setSystemStatus(await supabaseService.getAgenticStatus());
    setAgentPlan(await supabaseService.getAgentPlan());
    setActionHistory(await supabaseService.getActionHistory());
  };

  // WebSocket event handler
  const handleWebSocketMessage: WebSocketEventHandler = useCallback((message: AgenticWebSocketMessage) => {
    switch (message.type) {
      case 'action_approved':
      case 'action_denied':
      case 'action_created':
      case 'situation_processed':
        fetchAll();
        break;
      case 'status_update':
        fetchAll();
        break;
      default:
        break;
    }
  }, []);

  // WebSocket connection
  useEffect(() => {
    agenticWebSocket.connect().then(() => {
      setWsStatus(agenticWebSocket.getConnectionState());
    });
    agenticWebSocket.on('action_approved', handleWebSocketMessage);
    agenticWebSocket.on('action_denied', handleWebSocketMessage);
    agenticWebSocket.on('action_created', handleWebSocketMessage);
    agenticWebSocket.on('situation_processed', handleWebSocketMessage);
    agenticWebSocket.on('status_update', handleWebSocketMessage);
    // Connection status polling
    const interval = setInterval(() => {
      setWsStatus(agenticWebSocket.getConnectionState());
    }, 1000);
    return () => {
      agenticWebSocket.disconnect();
      clearInterval(interval);
    };
  }, [handleWebSocketMessage]);

  const approveAction = async (actionId: string) => {
    await supabaseService.approveAction(actionId);
    fetchAll();
  };

  const denyAction = async (actionId: string) => {
    await supabaseService.denyAction(actionId);
    fetchAll();
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex items-center mb-4">
        <h1 className="text-3xl font-bold flex-1">Agentic AI Dashboard</h1>
        <span className={`ml-4 px-3 py-1 rounded text-xs font-semibold ${wsStatus === 'connected' ? 'bg-green-100 text-green-700' : 'bg-gray-200 text-gray-600'}`}>WebSocket: {wsStatus}</span>
      </div>
      {agentPlan && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg">
          <div className="font-semibold mb-1">Agent Plan & Reasoning</div>
          <div className="text-gray-800 mb-2">{agentPlan.current_reasoning}</div>
          <div className="flex flex-wrap gap-4 text-xs text-gray-600">
            <span>Memory size: {agentPlan.memory_size}</span>
            <span>Tools available: {agentPlan.tools_available}</span>
            <span>Simulation mode: {agentPlan.simulation_mode ? 'On' : 'Off'}</span>
            <span>Recent actions: {agentPlan.recent_actions.pending} pending, {agentPlan.recent_actions.approved} approved, {agentPlan.recent_actions.denied} denied</span>
          </div>
        </div>
      )}
      <h2 className="text-xl font-semibold mb-2">Pending Actions</h2>
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-600">{error}</div>}
      <div className="space-y-4 mb-8">
        {pendingActions.length === 0 && <div>No pending actions.</div>}
        {pendingActions.map(action => (
          <div key={action.action_id} className="bg-white shadow rounded-lg p-4 flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <div className="font-semibold">{action.action_type}</div>
              <div className="text-gray-600 text-sm">Reason: {action.reasoning || 'N/A'}</div>
              <div className="text-gray-500 text-xs">Confidence: {action.confidence.toFixed(2)}</div>
              <div className="text-gray-400 text-xs">{formatTimestamp(action.timestamp)}</div>
            </div>
            <div className="mt-2 md:mt-0 flex space-x-2">
              <button
                className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
                onClick={() => approveAction(action.action_id)}
                disabled={loading}
              >
                Approve
              </button>
              <button
                className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
                onClick={() => denyAction(action.action_id)}
                disabled={loading}
              >
                Deny
              </button>
            </div>
          </div>
        ))}
      </div>
      <h2 className="text-xl font-semibold mb-2">Action History</h2>
      <div className="bg-white shadow rounded-lg p-4">
        {!actionHistory ? (
          <div>Loading...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="font-semibold mb-1">Pending</div>
              {actionHistory.history.pending.length === 0 ? <div className="text-xs text-gray-400">None</div> :
                actionHistory.history.pending.map(a => (
                  <div key={a.action_id} className="text-xs text-gray-700 mb-1">{a.action_type} ({formatTimestamp(a.timestamp)})</div>
                ))}
            </div>
            <div>
              <div className="font-semibold mb-1">Approved</div>
              {actionHistory.history.approved.length === 0 ? <div className="text-xs text-gray-400">None</div> :
                actionHistory.history.approved.map(a => (
                  <div key={a.action_id} className="text-xs text-green-700 mb-1">{a.action_type} ({formatTimestamp(a.timestamp)})</div>
                ))}
            </div>
            <div>
              <div className="font-semibold mb-1">Denied</div>
              {actionHistory.history.denied.length === 0 ? <div className="text-xs text-gray-400">None</div> :
                actionHistory.history.denied.map(a => (
                  <div key={a.action_id} className="text-xs text-red-700 mb-1">{a.action_type} ({formatTimestamp(a.timestamp)})</div>
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgenticAI; 