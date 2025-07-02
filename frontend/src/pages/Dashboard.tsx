import React from 'react';
import { useQuery } from 'react-query';
import { 
  TrendingUp, 
  Package, 
  Truck, 
  Users, 
  Activity,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Mock data - replace with actual API calls
const mockMetrics = {
  totalOrders: 156,
  activeAgents: 5,
  vehiclesAvailable: 12,
  inventoryItems: 45,
  systemHealth: 98,
  pendingDeliveries: 23
};

const mockChartData = [
  { time: '00:00', orders: 12, deliveries: 8 },
  { time: '04:00', orders: 8, deliveries: 15 },
  { time: '08:00', orders: 25, deliveries: 22 },
  { time: '12:00', orders: 35, deliveries: 28 },
  { time: '16:00', orders: 28, deliveries: 35 },
  { time: '20:00', orders: 18, deliveries: 20 },
];

const Dashboard: React.FC = () => {
  const { data: metrics, isLoading } = useQuery('dashboard-metrics', () => {
    // Simulate API call
    return new Promise(resolve => setTimeout(() => resolve(mockMetrics), 1000));
  });

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
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Real-time overview of your logistics operations</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-600">Live</span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Orders</p>
              <p className="text-2xl font-bold text-gray-900">{metrics?.totalOrders}</p>
            </div>
            <div className="p-2 bg-blue-100 rounded-lg">
              <Package className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Running Agents</p>
              <p className="text-2xl font-bold text-gray-900">{metrics?.activeAgents}</p>
            </div>
            <div className="p-2 bg-green-100 rounded-lg">
              <Activity className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Available Vehicles</p>
              <p className="text-2xl font-bold text-gray-900">{metrics?.vehiclesAvailable}</p>
            </div>
            <div className="p-2 bg-purple-100 rounded-lg">
              <Truck className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Inventory Items</p>
              <p className="text-2xl font-bold text-gray-900">{metrics?.inventoryItems}</p>
            </div>
            <div className="p-2 bg-orange-100 rounded-lg">
              <Package className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">System Health</p>
              <p className="text-2xl font-bold text-gray-900">{metrics?.systemHealth}%</p>
            </div>
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Pending Deliveries</p>
              <p className="text-2xl font-bold text-gray-900">{metrics?.pendingDeliveries}</p>
            </div>
            <div className="p-2 bg-yellow-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Orders & Deliveries</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="orders" stroke="#3b82f6" strokeWidth={2} />
              <Line type="monotone" dataKey="deliveries" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Agent Performance</h3>
          <div className="space-y-4">
            {['Restock Agent', 'Route Agent', 'Pricing Agent', 'Dispatch Agent', 'Forecasting Agent'].map((agent, index) => (
              <div key={agent} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${index % 2 === 0 ? 'bg-green-500' : 'bg-blue-500'}`}></div>
                  <span className="text-sm font-medium text-gray-700">{agent}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full" 
                      style={{ width: `${75 + Math.random() * 20}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600">85%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {[
            { action: 'Route Agent optimized delivery route', time: '2 minutes ago', type: 'success' },
            { action: 'New order received from Customer #1234', time: '5 minutes ago', type: 'info' },
            { action: 'Inventory restocked for Product #567', time: '8 minutes ago', type: 'success' },
            { action: 'Weather alert: Rain expected in downtown', time: '12 minutes ago', type: 'warning' },
            { action: 'Vehicle #VH001 completed maintenance', time: '15 minutes ago', type: 'success' },
          ].map((activity, index) => (
            <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className={`w-2 h-2 rounded-full ${
                activity.type === 'success' ? 'bg-green-500' :
                activity.type === 'warning' ? 'bg-yellow-500' :
                'bg-blue-500'
              }`}></div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                <p className="text-xs text-gray-500">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 