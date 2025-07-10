import React, { useState, useEffect } from 'react';
import { Truck, MapPin, Map, Clock } from 'lucide-react';
import { supabaseService } from '../services/supabaseService.ts';

const FleetMap = () => {
  const [vehicles, setVehicles] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [selectedVehicle, setSelectedVehicle] = useState(null);

  useEffect(() => {
    fetchFleetData();
    const interval = setInterval(fetchFleetData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchFleetData = async () => {
    try {
      const vehiclesData = await supabaseService.getFleet();
      const routesData = await supabaseService.getRoutes();
      
      setVehicles(vehiclesData || []);
      setRoutes(routesData || []);
    } catch (error) {
      console.error('Error fetching fleet data:', error);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Fleet Map</h1>
        <p className="text-gray-600 mt-2">Live tracking of vehicles and delivery routes</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Map */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Live Map</h2>
            </div>
            <div className="p-6">
              {/* Placeholder for Mapbox map */}
              <div className="w-full h-96 bg-gray-100 rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <MapPin className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600">Mapbox integration would be here</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Showing {vehicles.length} vehicles and {routes.length} active routes
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Fleet Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Fleet Status</h2>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <Truck className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-blue-600">{vehicles.length}</p>
                  <p className="text-sm text-blue-600">Total Vehicles</p>
                </div>
                
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <Map className="h-8 w-8 text-green-600 mx-auto mb-2" />
                  <p className="text-2xl font-bold text-green-600">{routes.length}</p>
                  <p className="text-sm text-green-600">Active Routes</p>
                </div>
              </div>

              {/* Vehicle List */}
              <div className="mt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Vehicles</h3>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {vehicles.map((vehicle) => (
                    <div
                      key={vehicle.vehicle_id}
                      onClick={() => setSelectedVehicle(vehicle)}
                      className={`p-3 border rounded-lg cursor-pointer hover:bg-gray-50 ${
                        selectedVehicle?.vehicle_id === vehicle.vehicle_id ? 'border-blue-500 bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900">{vehicle.vehicle_id}</p>
                          <p className="text-sm text-gray-600">{vehicle.vehicle_type}</p>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          vehicle.status === 'available' ? 'bg-green-100 text-green-800' :
                          vehicle.status === 'in_use' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {vehicle.status}
                        </span>
                      </div>
                      <div className="mt-2 text-xs text-gray-500">
                        Capacity: {vehicle.capacity}kg
                      </div>
                      <div className="mt-2 text-xs text-gray-500">
                        Location: {vehicle.current_location}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Vehicle Details */}
      {selectedVehicle && (
        <div className="mt-6 bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Vehicle Details</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Vehicle Information</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">ID:</span>
                    <span className="ml-2 font-medium">{selectedVehicle.vehicle_id}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Type:</span>
                    <span className="ml-2 font-medium">{selectedVehicle.vehicle_type}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Status:</span>
                    <span className={`ml-2 px-2 py-1 rounded-full text-xs font-medium ${
                      selectedVehicle.status === 'available' ? 'bg-green-100 text-green-800' :
                      selectedVehicle.status === 'in_use' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {selectedVehicle.status}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Capacity:</span>
                    <span className="ml-2 font-medium">{selectedVehicle.capacity}kg</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Location:</span>
                    <span className="ml-2 font-medium">{selectedVehicle.current_location}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-medium text-gray-900 mb-2">Location</h3>
                {selectedVehicle.current_location ? (
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-gray-600">Address:</span>
                      <span className="ml-2 font-medium">{selectedVehicle.current_location.address}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Coordinates:</span>
                      <span className="ml-2 font-medium">
                        {selectedVehicle.current_location.latitude}, {selectedVehicle.current_location.longitude}
                      </span>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">No location data</p>
                )}
              </div>

              <div>
                <h3 className="font-medium text-gray-900 mb-2">Performance</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">Avg Speed:</span>
                    <span className="ml-2 font-medium">{selectedVehicle.average_speed_kmh} km/h</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Utilization:</span>
                    <span className="ml-2 font-medium">
                      {Math.round((selectedVehicle.current_load_kg / selectedVehicle.capacity_kg) * 100)}%
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

export default FleetMap; 