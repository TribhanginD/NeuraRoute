import React, { useState, useEffect } from 'react';
import { 
  Package, 
  Truck, 
  Users, 
  TrendingUp,
  Activity,
  Clock,
  MapPin,
  ShoppingCart
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = () => {
  const [simulationStatus, setSimulationStatus] = useState(null);
  const [stats, setStats] = useState({
    activeOrders: 0,
    activeDeliveries: 0,
    availableVehicles: 0,
    totalInventory: 0,
    agentsActive: 0,
    systemHealth: 'healthy'
  });

  useEffect(() => {
    fetchSimulationStatus();
    fetchStats();
    const interval = setInterval(() => {
      fetchSimulationStatus();
      fetchStats();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchSimulationStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/simulation/status');
      const data = await response.json();
      setSimulationStatus(data);
    } catch (error) {
      console.error('Error fetching simulation status:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const [inventoryRes, fleetRes, merchantsRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/inventory/summary'),
        fetch('http://localhost:8000/api/v1/fleet/summary'),
        fetch('http://localhost:8000/api/v1/merchants/summary')
      ]);
      
      const inventoryData = await inventoryRes.json();
      const fleetData = await fleetRes.json();
      const merchantsData = await merchantsRes.json();
      
      setStats({
        activeOrders: merchantsData.pending_orders || 0,
        activeDeliveries: fleetData.active_routes || 0,
        availableVehicles: fleetData.available_vehicles || 0,
        totalInventory: inventoryData.total_items || 0,
        agentsActive: simulationStatus?.agents_active || 0,
        systemHealth: simulationStatus?.system_health || 'healthy'
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const chartData = [
    { time: '00:00', orders: 12, deliveries: 8 },
    { time: '04:00', orders: 8, deliveries: 15 },
    { time: '08:00', orders: 25, deliveries: 22 },
    { time: '12:00', orders: 35, deliveries: 30 },
    { time: '16:00', orders: 28, deliveries: 25 },
    { time: '20:00', orders: 18, deliveries: 12 },
  ];

  const StatCard = ({ icon: Icon, title, value, change, color }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {change && (
            <p className="text-sm text-green-600 flex items-center">
              <TrendingUp className="h-4 w-4 mr-1" />
              {change}
            </p>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">AI-Native Hyperlocal Logistics System Overview</p>
      </div>

      {/* Simulation Status */}
      {simulationStatus && (
        <div className="mb-6">
          <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
            simulationStatus.is_running 
              ? 'bg-green-100 text-green-800' 
              : 'bg-red-100 text-red-800'
          }`}>
            <Activity className="h-4 w-4 mr-2" />
            Simulation {simulationStatus.is_running ? 'Running' : 'Stopped'}
            {simulationStatus.is_running && (
              <span className="ml-2">
                Tick: {simulationStatus.tick_count} | 
                Time: {new Date(simulationStatus.current_time).toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={ShoppingCart}
          title="Active Orders"
          value={stats.activeOrders}
          change="+12% from last hour"
          color="bg-blue-500"
        />
        <StatCard
          icon={Truck}
          title="Active Deliveries"
          value={stats.activeDeliveries}
          change="+8% from last hour"
          color="bg-green-500"
        />
        <StatCard
          icon={Package}
          title="Available Vehicles"
          value={stats.availableVehicles}
          color="bg-purple-500"
        />
        <StatCard
          icon={Users}
          title="Active Agents"
          value={stats.agentsActive}
          color="bg-orange-500"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Orders & Deliveries (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="orders" stroke="#3b82f6" strokeWidth={2} />
              <Line type="monotone" dataKey="deliveries" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Database</span>
              <span className="text-sm text-green-600">Healthy</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Redis Cache</span>
              <span className="text-sm text-green-600">Healthy</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">AI Agents</span>
              <span className="text-sm text-green-600">Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Forecasting Engine</span>
              <span className="text-sm text-green-600">Running</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8 bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Route optimization completed for Vehicle #123</span>
              <span className="text-xs text-gray-400">2 minutes ago</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-gray-600">New order received from Merchant #456</span>
              <span className="text-xs text-gray-400">5 minutes ago</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Inventory restock recommendation generated</span>
              <span className="text-xs text-gray-400">8 minutes ago</span>
            </div>
            <div className="flex items-center space-x-3">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Demand forecast updated for SKU #789</span>
              <span className="text-xs text-gray-400">12 minutes ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 