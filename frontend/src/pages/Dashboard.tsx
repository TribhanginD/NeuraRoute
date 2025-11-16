import React, { useEffect, useState } from 'react'
import { Package, Truck, Activity, AlertTriangle, CheckCircle } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

import { supabaseService } from '../services/supabaseService'
import { agenticApi } from '../services/agenticApi'

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState({
    totalOrders: 0,
    activeAgents: 0,
    vehiclesAvailable: 0,
    inventoryItems: 0,
    systemHealth: 0,
    pendingDeliveries: 0,
  })
  const [chartData, setChartData] = useState([] as Array<{ time: string; orders: number; deliveries: number }>)
  const [recentActivity, setRecentActivity] = useState([] as Array<{ action: string; time: string; type: string }>)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      const [stats, orders, vehicles, inventory, logs] = await Promise.all([
        agenticApi.getSystemStats(),
        supabaseService.getOrders(),
        supabaseService.getFleet(),
        supabaseService.getInventory(),
        supabaseService.getAgentLogs(null, 5),
      ])

      setMetrics({
        totalOrders: stats.orders,
        activeAgents: stats.agent_actions,
        vehiclesAvailable: vehicles.length,
        inventoryItems: inventory.length,
        systemHealth: stats.agents_running ? 100 : 65,
        pendingDeliveries: orders.filter((o) => o.status === 'pending').length,
      })

      const grouped = orders.reduce<Record<string, { orders: number; deliveries: number }>>((acc, order) => {
        const key = new Date(order.created_at || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        if (!acc[key]) {
          acc[key] = { orders: 0, deliveries: 0 }
        }
        acc[key].orders += 1
        if (order.status === 'delivered') {
          acc[key].deliveries += 1
        }
        return acc
      }, {})
      setChartData(
        Object.entries(grouped).map(([time, value]) => ({ time, ...value }))
      )

      setRecentActivity(
        logs.map((log: any) => ({
          action: log.action,
          time: new Date(log.timestamp).toLocaleTimeString(),
          type: log.status === 'completed' ? 'success' : 'info',
        }))
      )

      setIsLoading(false)
    }
    fetchData()
  }, [])

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
          {recentActivity.length === 0 && (
            <p className="text-sm text-gray-500">No agent activity recorded yet.</p>
          )}
          {recentActivity.map((activity, index) => (
            <div key={`${activity.action}-${index}`} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className={`w-2 h-2 rounded-full ${activity.type === 'success' ? 'bg-green-500' : 'bg-blue-500'}`} />
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
