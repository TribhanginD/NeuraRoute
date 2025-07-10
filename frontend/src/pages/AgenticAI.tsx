import React, { useEffect, useState, useCallback } from 'react';
import { agenticApi, AgentStatus, SystemStats } from '../services/agenticApi';

const AgenticAI: React.FC = () => {
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastAction, setLastAction] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
    // Poll for updates every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [status, stats] = await Promise.all([
        agenticApi.getAgentStatus(),
        agenticApi.getSystemStats()
      ]);
      setAgentStatus(status);
      setSystemStats(stats);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const startAgents = async () => {
    try {
      setLoading(true);
      await agenticApi.startAgents();
      setLastAction('Agents started successfully');
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start agents');
    } finally {
      setLoading(false);
    }
  };

  const stopAgents = async () => {
    try {
      setLoading(true);
      await agenticApi.stopAgents();
      setLastAction('Agents stopped successfully');
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to stop agents');
    } finally {
      setLoading(false);
    }
  };

  const triggerAgentAction = async (agentType: string, action: string) => {
    try {
      setLoading(true);
      await agenticApi.triggerAgentAction(agentType, action);
      setLastAction(`Triggered ${action} for ${agentType} agent`);
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger action');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Agentic AI Dashboard</h1>
        <div className="flex space-x-2">
          <button
            onClick={startAgents}
            disabled={loading || agentStatus?.agents_running}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
          >
            Start Agents
          </button>
          <button
            onClick={stopAgents}
            disabled={loading || !agentStatus?.agents_running}
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 disabled:opacity-50"
          >
            Stop Agents
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {lastAction && (
        <div className="mb-4 p-4 bg-green-100 border border-green-400 text-green-700 rounded">
          {lastAction}
        </div>
      )}

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          {loading ? (
            <div>Loading...</div>
          ) : agentStatus ? (
            <div className="space-y-3">
              <div className="flex justify-between">
                <span>Manager Running:</span>
                <span className={agentStatus.manager_running ? 'text-green-600' : 'text-red-600'}>
                  {agentStatus.manager_running ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Agents Running:</span>
                <span className={agentStatus.agents_running ? 'text-green-600' : 'text-red-600'}>
                  {agentStatus.agents_running ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Total Agents:</span>
                <span>{agentStatus.total_agents}</span>
              </div>
            </div>
          ) : (
            <div>No status available</div>
          )}
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">System Statistics</h2>
          {loading ? (
            <div>Loading...</div>
          ) : systemStats ? (
            <div className="space-y-3">
              <div className="flex justify-between">
                <span>Inventory Items:</span>
                <span>{systemStats.inventory_items}</span>
              </div>
              <div className="flex justify-between">
                <span>Orders:</span>
                <span>{systemStats.orders}</span>
              </div>
              <div className="flex justify-between">
                <span>Fleet Vehicles:</span>
                <span>{systemStats.fleet_vehicles}</span>
              </div>
              <div className="flex justify-between">
                <span>Agent Logs:</span>
                <span>{systemStats.agent_logs}</span>
              </div>
              <div className="flex justify-between">
                <span>Agent Actions:</span>
                <span>{systemStats.agent_actions}</span>
              </div>
            </div>
          ) : (
            <div>No stats available</div>
          )}
        </div>
      </div>

      {/* Agent Status */}
      {agentStatus && (
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Agent Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(agentStatus.agents).map(([agentId, agent]) => (
              <div key={agentId} className="border rounded p-4">
                <div className="font-semibold capitalize">{agentId} Agent</div>
                <div className="text-sm text-gray-600 mb-2">{agent.agent_type}</div>
                <div className="flex items-center space-x-2">
                  <span className={`w-2 h-2 rounded-full ${agent.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                  <span className="text-sm">{agent.is_active ? 'Active' : 'Inactive'}</span>
                </div>
                {agent.last_action_time && (
                  <div className="text-xs text-gray-500 mt-1">
                    Last action: {new Date(agent.last_action_time).toLocaleString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Agent Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold mb-4">Trigger Agent Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Inventory Agent */}
          <div className="border rounded p-4">
            <h3 className="font-semibold mb-3">Inventory Agent</h3>
            <div className="space-y-2">
              <button
                onClick={() => triggerAgentAction('inventory', 'check_low_stock')}
                disabled={loading}
                className="w-full bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                Check Low Stock
              </button>
              <button
                onClick={() => triggerAgentAction('inventory', 'optimize_inventory')}
                disabled={loading}
                className="w-full bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                Optimize Inventory
              </button>
              <button
                onClick={() => triggerAgentAction('inventory', 'handle_expired_items')}
                disabled={loading}
                className="w-full bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 disabled:opacity-50"
              >
                Handle Expired Items
              </button>
            </div>
          </div>

          {/* Routing Agent */}
          <div className="border rounded p-4">
            <h3 className="font-semibold mb-3">Routing Agent</h3>
            <div className="space-y-2">
              <button
                onClick={() => triggerAgentAction('routing', 'optimize_routes')}
                disabled={loading}
                className="w-full bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700 disabled:opacity-50"
              >
                Optimize Routes
              </button>
              <button
                onClick={() => triggerAgentAction('routing', 'assign_vehicles')}
                disabled={loading}
                className="w-full bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700 disabled:opacity-50"
              >
                Assign Vehicles
              </button>
              <button
                onClick={() => triggerAgentAction('routing', 'handle_dynamic_routing')}
                disabled={loading}
                className="w-full bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700 disabled:opacity-50"
              >
                Dynamic Routing
              </button>
            </div>
          </div>

          {/* Pricing Agent */}
          <div className="border rounded p-4">
            <h3 className="font-semibold mb-3">Pricing Agent</h3>
            <div className="space-y-2">
              <button
                onClick={() => triggerAgentAction('pricing', 'analyze_market_conditions')}
                disabled={loading}
                className="w-full bg-purple-600 text-white px-3 py-2 rounded text-sm hover:bg-purple-700 disabled:opacity-50"
              >
                Analyze Market
              </button>
              <button
                onClick={() => triggerAgentAction('pricing', 'optimize_inventory_pricing')}
                disabled={loading}
                className="w-full bg-purple-600 text-white px-3 py-2 rounded text-sm hover:bg-purple-700 disabled:opacity-50"
              >
                Optimize Pricing
              </button>
              <button
                onClick={() => triggerAgentAction('pricing', 'handle_dynamic_pricing')}
                disabled={loading}
                className="w-full bg-purple-600 text-white px-3 py-2 rounded text-sm hover:bg-purple-700 disabled:opacity-50"
              >
                Dynamic Pricing
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgenticAI; 