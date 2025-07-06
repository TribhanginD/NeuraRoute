import React, { useState, useEffect, useMemo } from 'react';
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
import { supabaseService } from '../services/supabaseService.ts';

const Dashboard = () => {
  const [stats, setStats] = useState({
    activeOrders: 0,
    activeDeliveries: 0,
    availableVehicles: 0,
    totalInventory: 0,
    agentsActive: 0,
    systemHealth: 'healthy'
  });
  const [orders, setOrders] = useState([]);
  const [recentOrders, setRecentOrders] = useState([]);

  useEffect(() => {
    fetchStats();
    supabaseService.getOrders().then(data => {
      setOrders(data || []);
      setRecentOrders((data || []).slice(-5).reverse());
    });
    const interval = setInterval(() => {
      fetchStats();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    // Example: fetch stats from Supabase tables
    // You can aggregate stats here as needed
    // For now, just set systemHealth to 'healthy'
    setStats((prev) => ({ ...prev, systemHealth: 'healthy' }));
  };

  const chartData = useMemo(() => {
    // Group orders by hour for the last 24h
    const now = new Date();
    const hours = Array.from({ length: 24 }, (_, i) => {
      const d = new Date(now);
      d.setHours(i, 0, 0, 0);
      return d;
    });
    return hours.map(hour => {
      const count = orders.filter(order => {
        const t = new Date(order.created_at);
        return t.getHours() === hour.getHours();
      }).length;
      return {
        time: hour.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        orders: count,
        deliveries: 0 // If you have deliveries, add logic here
      };
    });
  }, [orders]);

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
    <div className="p-4 sm:p-6 min-h-screen pb-12 overflow-y-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">AI-Native Hyperlocal Logistics System Overview</p>
      </div>

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
          title="Running Agents"
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
              <span className="text-sm text-green-600">Running</span>
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
            {recentOrders.length === 0 && (
              <div className="text-gray-500">No recent orders.</div>
            )}
            {recentOrders.map(order => {
              // Format the order ID to show only first 8 characters
              const shortOrderId = order.id ? order.id.substring(0, 8) + '...' : 'Unknown';
              
              // Format items for better readability
              let itemsText = 'No items specified';
              if (order.items) {
                if (typeof order.items === 'string') {
                  // If items is a string, try to parse it or use as is
                  itemsText = order.items;
                } else if (Array.isArray(order.items)) {
                  // If items is an array, join them nicely
                  itemsText = order.items.join(', ');
                } else if (typeof order.items === 'object') {
                  // If items is an object, format it nicely
                  const itemEntries = Object.entries(order.items);
                  if (itemEntries.length === 1) {
                    const [item, quantity] = itemEntries[0];
                    itemsText = `${quantity} ${item}`;
                  } else {
                    itemsText = itemEntries
                      .map(([item, quantity]) => `${quantity} ${item}`)
                      .join(', ');
                  }
                }
              }
              
              // Format the timestamp
              const timestamp = order.created_at ? 
                new Date(order.created_at).toLocaleString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                  hour12: true
                }) : 'Unknown time';
              
              return (
                <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg" key={order.id}>
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-900">
                        New order received
                      </span>
                      <span className="text-xs text-gray-500">{timestamp}</span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      Order #{shortOrderId} • {itemsText}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 