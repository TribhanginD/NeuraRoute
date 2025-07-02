import React from 'react';
import { useQuery } from 'react-query';
import { Activity, Play, Pause, RotateCcw, AlertTriangle, CheckCircle } from 'lucide-react';

// Mock data
const mockAgents = [
  {
    id: '1',
    name: 'Restock Agent',
    type: 'restock',
    status: 'running',
    health: 95,
    lastAction: 'Optimized inventory levels',
    uptime: '2h 15m',
    performance: 87
  },
  {
    id: '2',
    name: 'Route Agent',
    type: 'route',
    status: 'running',
    health: 92,
    lastAction: 'Updated delivery routes',
    uptime: '1h 45m',
    performance: 91
  },
  {
    id: '3',
    name: 'Pricing Agent',
    type: 'pricing',
    status: 'stopped',
    health: 88,
    lastAction: 'Adjusted product prices',
    uptime: '45m',
    performance: 78
  },
  {
    id: '4',
    name: 'Dispatch Agent',
    type: 'dispatch',
    status: 'error',
    health: 65,
    lastAction: 'Failed to assign order',
    uptime: '30m',
    performance: 45
  },
  {
    id: '5',
    name: 'Forecasting Agent',
    type: 'forecasting',
    status: 'running',
    health: 97,
    lastAction: 'Generated demand forecast',
    uptime: '3h 20m',
    performance: 94
  }
];

const AgentMonitor: React.FC = () => {
  const { data: agents, isLoading } = useQuery('agents', () => {
    return new Promise(resolve => setTimeout(() => resolve(mockAgents), 1000));
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'text-green-600 bg-green-100';
      case 'stopped': return 'text-gray-600 bg-gray-100';
      case 'starting': return 'text-blue-600 bg-blue-100';
      case 'stopping': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
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

  if (isLoading) {
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
          <p className="text-gray-600">Monitor and control autonomous agents</p>
        </div>
        <div className="flex space-x-2">
          <button className="btn-success flex items-center space-x-2">
            <Play className="w-4 h-4" />
            <span>Start All</span>
          </button>
          <button className="btn-secondary flex items-center space-x-2">
            <Pause className="w-4 h-4" />
            <span>Pause All</span>
          </button>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {agents?.map((agent) => (
          <div key={agent.id} className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${getStatusColor(agent.status).split(' ')[1]}`}>
                  {getStatusIcon(agent.status)}
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                  <p className="text-sm text-gray-500 capitalize">{agent.type} Agent</p>
                </div>
              </div>
              <span className={`status-badge ${getStatusColor(agent.status)}`}>
                {agent.status}
              </span>
            </div>

            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Last Action</p>
                <p className="text-sm font-medium text-gray-900">{agent.lastAction}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Health</p>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          agent.health > 80 ? 'bg-green-500' : 
                          agent.health > 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${agent.health}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900">{agent.health}%</span>
                  </div>
                </div>

                <div>
                  <p className="text-sm text-gray-600">Performance</p>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          agent.performance > 80 ? 'bg-blue-500' : 
                          agent.performance > 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${agent.performance}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900">{agent.performance}%</span>
                  </div>
                </div>
              </div>

              <div>
                <p className="text-sm text-gray-600">Uptime</p>
                <p className="text-sm font-medium text-gray-900">{agent.uptime}</p>
              </div>

              <div className="flex space-x-2 pt-2">
                <button className="btn-primary flex-1 text-sm py-1">
                  {agent.status === 'running' ? 'Pause' : 'Start'}
                </button>
                <button className="btn-secondary text-sm py-1 px-3">
                  Logs
                </button>
                <button className="btn-secondary text-sm py-1 px-3">
                  Config
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* System Overview */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">3</p>
            <p className="text-sm text-gray-600">Running</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-yellow-600">1</p>
            <p className="text-sm text-gray-600">Stopped</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-red-600">1</p>
            <p className="text-sm text-gray-600">Error</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">87%</p>
            <p className="text-sm text-gray-600">Avg Performance</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentMonitor; 