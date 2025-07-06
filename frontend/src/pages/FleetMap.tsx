import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { Truck, MapPin, Navigation } from 'lucide-react';
import { supabaseService } from '../services/supabaseService.ts';

const FleetMap: React.FC = () => {
  const [vehicles, setVehicles] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFleet = async () => {
      setLoading(true);
      const vehiclesData = await supabaseService.getFleet();
      const routesData = await supabaseService.getRoutes();
      console.log('Fleet data:', vehiclesData); // Debug log
      console.log('Routes data:', routesData); // Debug log
      setVehicles(vehiclesData || []);
      setRoutes(routesData || []);
      setLoading(false);
    };
    fetchFleet();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Fleet Map</h1>
            <p className="text-gray-600">Real-time vehicle tracking and route optimization</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Available ({vehicles.filter(v => v.status === 'available').length})</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-gray-600">In Transit ({vehicles.filter(v => v.status === 'in_transit').length})</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="text-sm text-gray-600">Maintenance ({vehicles.filter(v => v.status === 'maintenance').length})</span>
            </div>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <div className="flex-1 relative">
        <div className="absolute inset-0 bg-gray-100 flex items-center justify-center">
          <div className="text-center">
            <MapPin className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Interactive Map</h3>
            <p className="text-gray-600 mb-4">Map integration would be implemented here</p>
            
            {/* Vehicle List */}
            <div className="max-w-4xl mx-auto">
              <h4 className="text-lg font-semibold text-gray-900 mb-4">Fleet Vehicles ({vehicles.length})</h4>
              {vehicles.length === 0 ? (
                <div className="text-gray-500">No vehicles found</div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {vehicles.map((vehicle) => (
                    <div key={vehicle.id} className="bg-white p-4 rounded-lg shadow border">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <Truck className="w-5 h-5 text-blue-600" />
                          <span className="font-medium text-gray-900">{vehicle.id}</span>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          vehicle.status === 'available' ? 'bg-green-100 text-green-800' :
                          vehicle.status === 'in_transit' ? 'bg-blue-100 text-blue-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {vehicle.status?.replace('_', ' ') || 'unknown'}
                        </span>
                      </div>
                      <div className="space-y-1 text-sm text-gray-600">
                        <div>Type: {vehicle.vehicle_type || 'Unknown'}</div>
                        <div>Capacity: {vehicle.capacity || 0} kg</div>
                        <div>Location: {vehicle.current_location ? `${vehicle.current_location.lat?.toFixed(4)}, ${vehicle.current_location.lng?.toFixed(4)}` : 'Unknown'}</div>
                        <div>Driver: {vehicle.driver_id || 'Unassigned'}</div>
                        {vehicle.fuel_level && <div>Fuel: {vehicle.fuel_level * 100}%</div>}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Routes List */}
            {routes.length > 0 && (
              <div className="max-w-4xl mx-auto mt-8">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Active Routes ({routes.length})</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {routes.map((route) => (
                    <div key={route.id} className="bg-white p-4 rounded-lg shadow border">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <Navigation className="w-5 h-5 text-green-600" />
                          <span className="font-medium text-gray-900">{route.name || route.id}</span>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          route.status === 'running' ? 'bg-green-100 text-green-800' :
                          route.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {route.status || 'unknown'}
                        </span>
                      </div>
                      <div className="space-y-1 text-sm text-gray-600">
                        <div>Vehicle: {route.vehicle || 'Unassigned'}</div>
                        <div>Waypoints: {route.path?.length || 0}</div>
                        {route.estimated_completion && (
                          <div>ETA: {new Date(route.estimated_completion).toLocaleString()}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FleetMap; 