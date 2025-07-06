import axios from 'axios';
import toast from 'react-hot-toast';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    
    // Show error toast for non-401 errors
    if (error.response?.status !== 401) {
      toast.error(message);
    }
    
    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  // Health
  health: '/health',
  
  // Simulation
  simulation: {
    status: '/api/v1/simulation/status',
    start: '/api/v1/simulation/start',
    stop: '/api/v1/simulation/stop',
    pause: '/api/v1/simulation/pause',
    resume: '/api/v1/simulation/resume',
    reset: '/api/v1/simulation/reset',
    events: '/api/v1/simulation/events',
  },
  
  // Agents
  agents: {
    list: '/api/v1/agents',
    detail: (id) => `/api/v1/agents/${id}`,
    start: (id) => `/api/v1/agents/${id}/start`,
    stop: (id) => `/api/v1/agents/${id}/stop`,
    logs: (id) => `/api/v1/agents/${id}/logs`,
    performance: (id) => `/api/v1/agents/${id}/performance`,
  },
  
  // Fleet
  fleet: {
    vehicles: '/api/v1/fleet/vehicles',
    vehicle: (id) => `/api/v1/fleet/vehicles/${id}`,
    routes: '/api/v1/fleet/routes',
    route: (id) => `/api/v1/fleet/routes/${id}`,
    orders: '/api/v1/fleet/orders',
    order: (id) => `/api/v1/fleet/orders/${id}`,
  },
  
  // Inventory
  inventory: {
    skus: '/api/v1/inventory/skus',
    sku: (id) => `/api/v1/inventory/skus/${id}`,
    items: '/api/v1/inventory/items',
    item: (id) => `/api/v1/inventory/items/${id}`,
    merchants: '/api/v1/inventory/merchants',
    merchant: (id) => `/api/v1/inventory/merchants/${id}`,
  },
  
  // Forecasting
  forecasting: {
    forecasts: '/api/v1/forecasting/forecasts',
    forecast: (id) => `/api/v1/forecasting/forecasts/${id}`,
    generate: '/api/v1/forecasting/generate',
    accuracy: '/api/v1/forecasting/accuracy',
  },
};

// API methods
export const apiService = {
  // Health check
  getHealth: () => api.get(endpoints.health),
  
  // Simulation
  getSimulationStatus: () => api.get(endpoints.simulation.status),
  startSimulation: (data) => api.post(endpoints.simulation.start, data),
  stopSimulation: () => api.post(endpoints.simulation.stop),
  pauseSimulation: () => api.post(endpoints.simulation.pause),
  resumeSimulation: () => api.post(endpoints.simulation.resume),
  resetSimulation: () => api.post(endpoints.simulation.reset),
  getSimulationEvents: (params) => api.get(endpoints.simulation.events, { params }),
  
  // Agents
  getAgents: () => api.get(endpoints.agents.list),
  getAgent: (id) => api.get(endpoints.agents.detail(id)),
  startAgent: (id) => api.post(endpoints.agents.start(id)),
  stopAgent: (id) => api.post(endpoints.agents.stop(id)),
  getAgentLogs: (id, params) => api.get(endpoints.agents.logs(id), { params }),
  getAgentPerformance: (id) => api.get(endpoints.agents.performance(id)),
  
  // Fleet
  getVehicles: () => api.get(endpoints.fleet.vehicles),
  getVehicle: (id) => api.get(endpoints.fleet.vehicle(id)),
  updateVehicle: (id, data) => api.put(endpoints.fleet.vehicle(id), data),
  getRoutes: () => api.get(endpoints.fleet.routes),
  getRoute: (id) => api.get(endpoints.fleet.route(id)),
  updateRoute: (id, data) => api.put(endpoints.fleet.route(id), data),
  getOrders: (params) => api.get(endpoints.fleet.orders, { params }),
  getOrder: (id) => api.get(endpoints.fleet.order(id)),
  createOrder: (data) => api.post(endpoints.fleet.orders, data),
  updateOrder: (id, data) => api.put(endpoints.fleet.order(id), data),
  
  // Inventory
  getSKU: (id) => api.get(endpoints.inventory.sku(id)),
  createSKU: (data) => api.post(endpoints.inventory.skus, data),
  updateSKU: (id, data) => api.put(endpoints.inventory.sku(id), data),
  deleteSKU: (id) => api.delete(endpoints.inventory.sku(id)),
  
  getInventoryItems: (params) => api.get(endpoints.inventory.items, { params }),
  getInventoryItem: (id) => api.get(endpoints.inventory.item(id)),
  updateInventoryItem: (id, data) => api.put(endpoints.inventory.item(id), data),
  
  getMerchants: (params) => api.get(endpoints.inventory.merchants, { params }),
  getMerchant: (id) => api.get(endpoints.inventory.merchant(id)),
  createMerchant: (data) => api.post(endpoints.inventory.merchants, data),
  updateMerchant: (id, data) => api.put(endpoints.inventory.merchant(id), data),
  deleteMerchant: (id) => api.delete(endpoints.inventory.merchant(id)),
  
  // Forecasting
  getForecasts: (params) => api.get(endpoints.forecasting.forecasts, { params }),
  getForecast: (id) => api.get(endpoints.forecasting.forecast(id)),
  generateForecast: (data) => api.post(endpoints.forecasting.generate, data),
  getForecastAccuracy: (params) => api.get(endpoints.forecasting.accuracy, { params }),
};

export { api }; 