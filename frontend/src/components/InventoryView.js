import React, { useState, useEffect } from 'react';
import { Package, Search, Filter, AlertTriangle } from 'lucide-react';

const InventoryView = () => {
  const [inventory, setInventory] = useState([]);
  const [skus, setSkus] = useState([]);
  const [locations, setLocations] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterLocation, setFilterLocation] = useState('');

  useEffect(() => {
    fetchInventoryData();
    const interval = setInterval(fetchInventoryData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchInventoryData = async () => {
    try {
      const [inventoryRes, skusRes, locationsRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/inventory/items'),
        fetch('http://localhost:8000/api/v1/inventory/skus'),
        fetch('http://localhost:8000/api/v1/inventory/locations')
      ]);
      
      const inventoryData = await inventoryRes.json();
      const skusData = await skusRes.json();
      const locationsData = await locationsRes.json();
      
      setInventory(inventoryData.items || []);
      setSkus(skusData.skus || []);
      setLocations(locationsData.locations || []);
    } catch (error) {
      console.error('Error fetching inventory data:', error);
    }
  };

  const filteredInventory = inventory.filter(item => {
    const matchesSearch = item.sku?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.sku_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = !filterLocation || item.location_id === parseInt(filterLocation);
    return matchesSearch && matchesLocation;
  });

  const lowStockItems = inventory.filter(item => item.available_quantity < 10);

  const getStockLevelColor = (available, total) => {
    const percentage = (available / total) * 100;
    if (percentage < 20) return 'text-red-600 bg-red-100';
    if (percentage < 50) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Inventory Management</h1>
        <p className="text-gray-600 mt-2">Monitor and manage inventory across all locations</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Package className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Items</p>
              <p className="text-2xl font-semibold text-gray-900">{inventory.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-red-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Low Stock</p>
              <p className="text-2xl font-semibold text-gray-900">{lowStockItems.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Package className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">SKUs</p>
              <p className="text-2xl font-semibold text-gray-900">{skus.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <Package className="h-8 w-8 text-purple-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Locations</p>
              <p className="text-2xl font-semibold text-gray-900">{locations.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search by SKU name or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div className="md:w-48">
            <select
              value={filterLocation}
              onChange={(e) => setFilterLocation(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Locations</option>
              {locations.map((location) => (
                <option key={location.id} value={location.id}>
                  {location.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Inventory Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">Inventory Items</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  SKU
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Quantity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Available
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Reserved
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Updated
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredInventory.map((item) => (
                <tr
                  key={item.id}
                  onClick={() => setSelectedItem(item)}
                  className="hover:bg-gray-50 cursor-pointer"
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{item.sku?.name || item.sku_id}</div>
                      <div className="text-sm text-gray-500">{item.sku?.category}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{item.location?.name || `Location ${item.location_id}`}</div>
                    <div className="text-sm text-gray-500">{item.location?.address}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.quantity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.available_quantity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.reserved_quantity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStockLevelColor(item.available_quantity, item.quantity)}`}>
                      {item.available_quantity < 10 ? 'Low Stock' : 'In Stock'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(item.last_updated).toLocaleDateString()}
                  </td>
                </tr>
              ))}
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
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">SKU Information</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">SKU ID:</span>
                    <span className="ml-2 font-medium">{selectedItem.sku_id}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Name:</span>
                    <span className="ml-2 font-medium">{selectedItem.sku?.name}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Category:</span>
                    <span className="ml-2 font-medium">{selectedItem.sku?.category}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Unit:</span>
                    <span className="ml-2 font-medium">{selectedItem.sku?.unit}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-medium text-gray-900 mb-2">Inventory Status</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">Total Quantity:</span>
                    <span className="ml-2 font-medium">{selectedItem.quantity}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Available:</span>
                    <span className="ml-2 font-medium">{selectedItem.available_quantity}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Reserved:</span>
                    <span className="ml-2 font-medium">{selectedItem.reserved_quantity}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Stock Level:</span>
                    <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${getStockLevelColor(selectedItem.available_quantity, selectedItem.quantity)}`}>
                      {Math.round((selectedItem.available_quantity / selectedItem.quantity) * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryView; 