import React, { useEffect, useState } from 'react'
import { Package, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react'
import { supabaseService } from '../services/supabaseService'

const InventoryView: React.FC = () => {
  const [inventory, setInventory] = useState<any[]>([])
  const [purchaseOrders, setPurchaseOrders] = useState<any[]>([])
  const [disposalOrders, setDisposalOrders] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchInventory = async () => {
      setLoading(true)
      const [items, purchases, disposals] = await Promise.all([
        supabaseService.getInventory(),
        supabaseService.getPurchaseOrders(10),
        supabaseService.getDisposalOrders(10),
      ])
      setInventory(items || [])
      setPurchaseOrders(purchases || [])
      setDisposalOrders(disposals || [])
      setLoading(false)
    }
    fetchInventory()
  }, [])

  // Calculate stats from real data
  const stats = {
    totalItems: inventory.length,
    inStock: inventory.filter(item => item.quantity > (item.min_quantity || 0)).length,
    lowStock: inventory.filter(item => item.quantity <= (item.min_quantity || 0) && item.quantity > 0).length,
    outOfStock: inventory.filter(item => item.quantity === 0).length
  };

  console.log('Rendering inventory table with data:', inventory)

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
          <h1 className="text-3xl font-bold text-gray-900">Inventory Management</h1>
          <p className="text-gray-600">Monitor and manage inventory levels</p>
        </div>
        <div className="flex space-x-2">
          <button className="btn-primary">Add Item</button>
          <button className="btn-secondary">Export</button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Items</p>
              <p className="text-2xl font-bold text-gray-900">{stats.totalItems}</p>
            </div>
            <div className="p-2 bg-blue-100 rounded-lg">
              <Package className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">In Stock</p>
              <p className="text-2xl font-bold text-green-600">{stats.inStock}</p>
            </div>
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Low Stock</p>
              <p className="text-2xl font-bold text-yellow-600">{stats.lowStock}</p>
            </div>
            <div className="p-2 bg-yellow-100 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Out of Stock</p>
              <p className="text-2xl font-bold text-red-600">{stats.outOfStock}</p>
            </div>
            <div className="p-2 bg-red-100 rounded-lg">
              <TrendingDown className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Inventory Items</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created At</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Updated At</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {inventory.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    No inventory items found
                  </td>
                </tr>
              ) : (
                inventory.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">{item.item_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{item.quantity}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{item.location}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{item.created_at ? new Date(item.created_at).toLocaleString() : ''}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{item.updated_at ? new Date(item.updated_at).toLocaleString() : ''}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Order Workflow */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Purchase Orders</h3>
            <span className="text-sm text-gray-500">{purchaseOrders.length} records</span>
          </div>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {purchaseOrders.length === 0 && <p className="text-sm text-gray-500">No purchase orders have been created yet.</p>}
            {purchaseOrders.map((order) => (
              <div key={order.id} className="border border-gray-200 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{order.item_name}</p>
                    <p className="text-xs text-gray-500">{order.order_type} · {order.quantity} units</p>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-blue-50 text-blue-700 capitalize">{order.status}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">Requested by {order.requested_by}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Disposal Orders</h3>
            <span className="text-sm text-gray-500">{disposalOrders.length} records</span>
          </div>
          <div className="space-y-3 max-h-80 overflow-y-auto">
            {disposalOrders.length === 0 && <p className="text-sm text-gray-500">No disposal orders have been logged.</p>}
            {disposalOrders.map((order) => (
              <div key={order.id} className="border border-gray-200 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{order.item_id || 'Unknown Item'}</p>
                    <p className="text-xs text-gray-500">{order.disposal_type} · {order.quantity} units</p>
                  </div>
                  <span className="text-xs px-2 py-1 rounded-full bg-amber-50 text-amber-700 capitalize">{order.status}</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">{order.reason || 'No reason provided'}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InventoryView; 
