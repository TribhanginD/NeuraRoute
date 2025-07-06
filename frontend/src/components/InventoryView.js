import React, { useState, useEffect } from 'react';
import { Package, Search, Filter, AlertTriangle } from 'lucide-react';
import { supabaseService } from '../services/supabaseService.ts';

const InventoryView = () => {
  const [inventory, setInventory] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLocation, setFilterLocation] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInventoryData();
    const interval = setInterval(fetchInventoryData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchInventoryData = async () => {
    try {
      const inventoryData = await supabaseService.getInventory();
      setInventory(inventoryData || []);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching inventory data:', error);
      setLoading(false);
    }
  };

  const filteredInventory = inventory.filter(item => {
    const matchesSearch = item.item_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = !filterLocation || item.location === filterLocation;
    return matchesSearch && matchesLocation;
  });

  const lowStockItems = inventory.filter(item => item.quantity < 10);

  // Get unique locations from inventory
  const uniqueLocations = Array.from(new Set(inventory.map(item => item.location))).filter(Boolean);

  const getStockLevelColor = (available, total) => {
    const percentage = (available / total) * 100;
    if (percentage < 20) return 'text-red-600 bg-red-100';
    if (percentage < 50) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
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
          <h1 className="text-3xl font-bold text-gray-900">Inventory Management</h1>
          <p className="text-gray-600">Monitor and manage inventory levels</p>
        </div>
        <div className="flex space-x-2">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Add Item
          </button>
          <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700">
            Export
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm font-medium text-gray-600">Total Items</p>
          <p className="text-2xl font-semibold text-gray-900">{inventory ? inventory.length : 0}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm font-medium text-gray-600">In Stock</p>
          <p className="text-2xl font-semibold text-gray-900">{inventory ? inventory.filter(item => item.quantity > 0).length : 0}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm font-medium text-gray-600">Low Stock</p>
          <p className="text-2xl font-semibold text-gray-900">{inventory ? inventory.filter(item => item.quantity <= 10 && item.quantity > 0).length : 0}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm font-medium text-gray-600">Out of Stock</p>
          <p className="text-2xl font-semibold text-gray-900">{inventory ? inventory.filter(item => item.quantity === 0).length : 0}</p>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Inventory Items</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Updated</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Merchant ID</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {Array.isArray(inventory) && inventory.length > 0 ? (
                inventory.map((item) => (
                  <tr key={item.id}>
                    <td className="px-6 py-4 whitespace-nowrap">{item.item_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{item.location}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{item.quantity}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{item.updated_at}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{item.merchant_id}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-400">No inventory items found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Item Details */}
      {selectedItem && (
        <div className="mt-6 bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Item Details</h2>
          </div>
          <div className="p-6">
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-600">ID:</span>
                <span className="ml-2 font-medium">{selectedItem.id}</span>
              </div>
              <div>
                <span className="text-gray-600">Name:</span>
                <span className="ml-2 font-medium">{selectedItem.item_name}</span>
              </div>
              <div>
                <span className="text-gray-600">Location:</span>
                <span className="ml-2 font-medium">{selectedItem.location}</span>
              </div>
              <div>
                <span className="text-gray-600">Quantity:</span>
                <span className="ml-2 font-medium">{selectedItem.quantity}</span>
              </div>
              <div>
                <span className="text-gray-600">Merchant ID:</span>
                <span className="ml-2 font-medium">{selectedItem.merchant_id}</span>
              </div>
              <div>
                <span className="text-gray-600">Last Updated:</span>
                <span className="ml-2 font-medium">{selectedItem.updated_at ? new Date(selectedItem.updated_at).toLocaleString() : ''}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryView; 