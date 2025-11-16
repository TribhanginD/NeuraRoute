import React, { useEffect, useMemo, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Truck, Navigation } from 'lucide-react'

import { supabaseService } from '../services/supabaseService'

type RoutePoint = { lat: number; lng: number; address?: string }

const LOCATION_LOOKUP: Record<string, { lat: number; lng: number }> = {
  'New York, NY': { lat: 40.7128, lng: -74.006 },
  'New York Warehouse': { lat: 40.7128, lng: -74.006 },
  'Los Angeles, CA': { lat: 34.0522, lng: -118.2437 },
  'Los Angeles Warehouse': { lat: 34.0522, lng: -118.2437 },
  'Chicago, IL': { lat: 41.8781, lng: -87.6298 },
  'Chicago Warehouse': { lat: 41.8781, lng: -87.6298 },
  'Houston, TX': { lat: 29.7604, lng: -95.3698 },
  'Houston Warehouse': { lat: 29.7604, lng: -95.3698 },
  'Seattle, WA': { lat: 47.6062, lng: -122.3321 },
  'Seattle Warehouse': { lat: 47.6062, lng: -122.3321 },
}

const resolveCoords = (location?: string | null): { lat: number; lng: number } | null => {
  if (!location) return null
  if (LOCATION_LOOKUP[location]) return LOCATION_LOOKUP[location]
  const normalized = location.split('-')[0]?.trim()
  if (normalized && LOCATION_LOOKUP[normalized]) return LOCATION_LOOKUP[normalized]
  return null
}

const defaultIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
})

const FleetMap: React.FC = () => {
  const [vehicles, setVehicles] = useState<any[]>([])
  const [routes, setRoutes] = useState<any[]>([])
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchFleet = async () => {
      setLoading(true)
      const [vehiclesData, routesData] = await Promise.all([
        supabaseService.getFleet(),
        supabaseService.getRoutes(),
      ])
      const enrichedVehicles = (vehiclesData || []).map((vehicle) => {
        const geoLat = (vehicle as any).geo_lat
        const geoLng = (vehicle as any).geo_lng
        const coords =
          (typeof geoLat === 'number' && typeof geoLng === 'number' && { lat: geoLat, lng: geoLng }) ||
          resolveCoords(vehicle.current_location)
        return { ...vehicle, coords }
      })
      const enrichedRoutes = (routesData || []).map((route) => {
        const parsedPoints: RoutePoint[] = route.route_points?.points || []
        const normalizedPoints = parsedPoints.map((point) => {
          if (typeof point.lat === 'number' && typeof point.lng === 'number') {
            return point
          }
          const fallback = resolveCoords(point.address || '')
          return fallback ? { ...point, ...fallback } : point
        })
        return { ...route, route_points: { ...route.route_points, points: normalizedPoints } }
      })
      setVehicles(enrichedVehicles)
      setRoutes(enrichedRoutes)
      setSelectedRouteId(routesData?.[0]?.id || null)
      setLoading(false)
    }
    fetchFleet()
  }, [])

  const selectedRoute = useMemo(() => routes.find((r) => r.id === selectedRouteId) || routes[0], [routes, selectedRouteId])

  const fallbackVehicle = vehicles.find((v) => v.coords)
  const center: [number, number] = selectedRoute?.route_points?.points?.[0]
    ? [selectedRoute.route_points.points[0].lat, selectedRoute.route_points.points[0].lng]
    : fallbackVehicle?.coords
    ? [fallbackVehicle.coords.lat, fallbackVehicle.coords.lng]
    : [40.7128, -74.006]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm uppercase text-blue-600 font-semibold tracking-wide">Live Logistics</p>
            <h1 className="text-3xl font-bold text-gray-900">Fleet Map</h1>
            <p className="text-gray-600">Track vehicles, inspect routes, and monitor utilization in real time.</p>
          </div>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <span className="flex items-center"><span className="w-3 h-3 bg-green-500 rounded-full mr-2" />Available {vehicles.filter((v) => v.status === 'available').length}</span>
            <span className="flex items-center"><span className="w-3 h-3 bg-blue-500 rounded-full mr-2" />In Transit {vehicles.filter((v) => v.status === 'in_transit').length}</span>
            <span className="flex items-center"><span className="w-3 h-3 bg-red-500 rounded-full mr-2" />Maintenance {vehicles.filter((v) => v.status === 'maintenance').length}</span>
          </div>
        </div>
      </div>

      <div className="flex flex-1 min-h-0">
        <div className="flex-1 relative">
          <MapContainer center={center} zoom={4} scrollWheelZoom className="absolute inset-0">
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
            {routes.map((route) => {
              const points: RoutePoint[] = route.route_points?.points || []
              if (!points.length) return null
              return (
                <Polyline
                  key={route.id}
                  positions={points.map((point) => [point.lat, point.lng])}
                  pathOptions={{
                    color: selectedRouteId === route.id ? '#2563eb' : '#38bdf8',
                    weight: selectedRouteId === route.id ? 5 : 3,
                    opacity: 0.85,
                  }}
                  eventHandlers={{ click: () => setSelectedRouteId(route.id) }}
                />
              )
            })}

            {vehicles.map((vehicle) => {
              if (!vehicle.coords) return null
              return (
                <Marker key={vehicle.id} position={[vehicle.coords.lat, vehicle.coords.lng]} icon={defaultIcon}>
                  <Popup>
                    <div className="space-y-1 text-sm">
                      <p className="font-semibold">{vehicle.vehicle_id}</p>
                      <p>Status: {vehicle.status}</p>
                      <p>Capacity: {vehicle.capacity} kg</p>
                    </div>
                  </Popup>
                </Marker>
              )
            })}
          </MapContainer>
        </div>

        <div className="w-full lg:w-96 border-l border-gray-200 bg-white overflow-y-auto">
          <div className="p-4 border-b border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Navigation className="w-4 h-4 mr-2 text-blue-600" /> Active Routes
            </h2>
            <div className="space-y-3 mt-4">
              {routes.map((route) => (
                <button
                  key={route.id}
                  onClick={() => setSelectedRouteId(route.id)}
                  className={`w-full text-left border rounded-lg p-3 ${selectedRouteId === route.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}
                >
                  <p className="text-sm font-semibold text-gray-900">{route.vehicle_id || route.id}</p>
                  <p className="text-xs text-gray-500">Waypoints: {route.route_points?.points?.length || 0}</p>
                </button>
              ))}
            </div>
          </div>

          <div className="p-4">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Truck className="w-4 h-4 mr-2 text-purple-600" /> Vehicles
            </h2>
            <div className="space-y-3 mt-4">
              {vehicles.map((vehicle) => (
                <div key={vehicle.id} className="border border-gray-200 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-semibold text-gray-900">{vehicle.vehicle_id}</p>
                      <p className="text-xs text-gray-500">{vehicle.vehicle_type}</p>
                    </div>
                    <span
                      className={`px-2 py-1 text-xs rounded-full ${
                        vehicle.status === 'available'
                          ? 'bg-green-100 text-green-700'
                          : vehicle.status === 'in_transit'
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {vehicle.status?.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-2">Location: {vehicle.current_location || 'Unknown'}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FleetMap
