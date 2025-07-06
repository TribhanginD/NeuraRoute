import React, { useEffect, useState } from 'react';
import { useQuery } from 'react-query';
import { Activity, Play, Pause, RotateCcw, AlertTriangle, CheckCircle } from 'lucide-react';
import { supabaseService } from '../services/supabaseService.ts';

const AgentMonitor: React.FC = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      setLoading(true);
      const data = await supabaseService.getAgents();
      console.log('Agents data:', data); // Debug log
      setAgents(data || []);
      setLoading(false);
    };
    fetchAgents();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-600 bg-green-100';
      case 'stopped': return 'text-red-600 bg-red-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getHealthColor = (health: number) => {
    if (health >= 90) return 'text-green-600';
    if (health >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <Activity className="w-4 h-4" />;
      case 'stopped': return <RotateCcw className="w-4 h-4" />;
      case 'starting': return <Play className="w-4 h-4" />;
      case 'stopping': return <Pause className="w-4 h-4" />;
      case 'error': return <AlertTriangle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
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
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agent Monitor</h1>
          <p className="text-gray-600">Monitor AI agent performance and status</p>
        </div>
        <div className="flex space-x-2">
          <button className="btn-primary">Start All</button>
          <button className="btn-secondary">Stop All</button>
        </div>
      </div>

      {/* Agent Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Agents</p>
              <p className="text-2xl font-bold text-gray-900">{agents.length}</p>
            </div>
            <div className="p-2 bg-blue-100 rounded-lg">
              <Activity className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Running</p>
              <p className="text-2xl font-bold text-green-600">{agents.filter(a => a.status === 'running').length}</p>
            </div>
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Stopped</p>
              <p className="text-2xl font-bold text-red-600">{agents.filter(a => a.status === 'stopped').length}</p>
            </div>
            <div className="p-2 bg-red-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Health</p>
              <p className="text-2xl font-bold text-gray-900">
                {agents.length > 0 
                  ? Math.round(agents.reduce((sum, agent) => sum + (agent.health || 0), 0) / agents.length)
                  : 0}%
              </p>
            </div>
            <div className="p-2 bg-gray-100 rounded-lg">
              <Activity className="w-6 h-6 text-gray-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Agent Status</h3>
          <div className="flex space-x-2">
            <input
              type="text"
              placeholder="Search agents..."
              className="input-field w-64"
            />
            <select className="input-field w-32">
              <option>All</option>
              <option>Running</option>
              <option>Stopped</option>
              <option>Error</option>
            </select>
          </div>
        </div>

        {agents.length === 0 ? (
          <div className="text-center py-12">
            <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Agents Available</h3>
            <p className="text-gray-600 mb-4">
              The agents system is not yet implemented. This would show AI agents for:
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
              <div className="text-sm text-gray-600">
                <div className="font-medium">Restock Agent</div>
                <div>Inventory optimization</div>
              </div>
              <div className="text-sm text-gray-600">
                <div className="font-medium">Route Agent</div>
                <div>Delivery optimization</div>
              </div>
              <div className="text-sm text-gray-600">
                <div className="font-medium">Pricing Agent</div>
                <div>Dynamic pricing</div>
              </div>
              <div className="text-sm text-gray-600">
                <div className="font-medium">Dispatch Agent</div>
                <div>Order assignment</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent) => (
              <div key={agent.id} className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900">{agent.name || agent.id}</h4>
                    <p className="text-sm text-gray-600">{agent.type || 'Unknown Type'}</p>
                  </div>
                  <span className={`status-badge ${getStatusColor(agent.status)}`}>
                    {agent.status || 'unknown'}
                  </span>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Health</span>
                    <span className={`text-sm font-medium ${getHealthColor(agent.health || 0)}`}>
                      {agent.health || 0}%
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Performance</span>
                    <span className="text-sm font-medium text-gray-900">{agent.performance || 0}%</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Uptime</span>
                    <span className="text-sm font-medium text-gray-900">{agent.uptime || 'Unknown'}</span>
                  </div>

                  <div className="pt-3 border-t border-gray-200">
                    <p className="text-sm text-gray-600 mb-3">
                      Last Action: {agent.lastAction || 'No recent activity'}
                    </p>
                  </div>

                  <div className="flex space-x-2">
                    {agent.status === 'running' ? (
                      <button className="flex-1 btn-secondary text-sm">Stop</button>
                    ) : (
                      <button className="flex-1 btn-primary text-sm">Start</button>
                    )}
                    <button className="flex-1 btn-secondary text-sm">Restart</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentMonitor; 