import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { Truck, MapPin, Navigation } from 'lucide-react';

// Mock data
const mockVehicles = [
  {
    id: 'VH001',
    type: 'delivery_van',
    lat: 40.7128,
    lng: -74.0060,
    status: 'in_use',
    driver: 'John Doe',
    currentRoute: 'Route A',
    capacity: 500,
    fuelLevel: 85
  },
  {
    id: 'VH002',
    type: 'truck',
    lat: 40.7589,
    lng: -73.9851,
    status: 'available',
    driver: 'Jane Smith',
    currentRoute: 'Route B',
    capacity: 1000,
    fuelLevel: 92
  },
  {
    id: 'VH003',
    type: 'delivery_van',
    lat: 40.7505,
    lng: -73.9934,
    status: 'maintenance',
    driver: 'Mike Johnson',
    currentRoute: 'Route C',
    capacity: 500,
    fuelLevel: 45
  }
];

const mockRoutes = [
  {
    id: 'route1',
    name: 'Route A',
    path: [
      [40.7128, -74.0060],
      [40.7589, -73.9851],
      [40.7505, -73.9934]
    ],
    vehicle: 'VH001',
    status: 'running'
  }
];

const FleetMap: React.FC = () => {
  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Fleet Map</h1>
            <p className="text-gray-600">Real-time fleet tracking and route visualization</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Available</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-gray-600">In Use</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Maintenance</span>
            </div>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div className="flex-1 relative">
        <MapContainer
          center={[40.7128, -74.0060]}
          zoom={13}
          className="h-full w-full"
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          {/* Vehicle Markers */}
          {mockVehicles.map((vehicle) => (
            <Marker
              key={vehicle.id}
              position={[vehicle.lat, vehicle.lng]}
              icon={L.divIcon({
                className: 'custom-marker',
                html: `<div class="w-8 h-8 rounded-full border-2 border-white shadow-lg flex items-center justify-center ${
                  vehicle.status === 'available' ? 'bg-green-500' :
                  vehicle.status === 'in_use' ? 'bg-blue-500' :
                  'bg-yellow-500'
                }">
                  <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"/>
                    <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1V8a1 1 0 00-1-1h-3z"/>
                  </svg>
                </div>`,
                iconSize: [32, 32],
                iconAnchor: [16, 16]
              })}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-semibold text-gray-900">{vehicle.id}</h3>
                  <p className="text-sm text-gray-600">{vehicle.type}</p>
                  <p className="text-sm text-gray-600">Driver: {vehicle.driver}</p>
                  <p className="text-sm text-gray-600">Route: {vehicle.currentRoute}</p>
                  <p className="text-sm text-gray-600">Fuel: {vehicle.fuelLevel}%</p>
                  <p className="text-sm text-gray-600">Capacity: {vehicle.capacity}kg</p>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Route Lines */}
          {mockRoutes.map((route) => (
            <Polyline
              key={route.id}
              positions={route.path}
              color="#3b82f6"
              weight={3}
              opacity={0.7}
            />
          ))}
        </MapContainer>

        {/* Fleet Stats Panel */}
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-4 w-64">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Fleet Overview</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Vehicles</span>
              <span className="text-sm font-medium text-gray-900">12</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Available</span>
              <span className="text-sm font-medium text-green-600">8</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">In Use</span>
              <span className="text-sm font-medium text-blue-600">3</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Maintenance</span>
              <span className="text-sm font-medium text-yellow-600">1</span>
            </div>
            <div className="pt-2 border-t border-gray-200">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Avg Fuel Level</span>
                <span className="text-sm font-medium text-gray-900">87%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FleetMap; 