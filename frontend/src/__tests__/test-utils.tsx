import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { BrowserRouter } from 'react-router-dom';

// Create a custom render function that includes providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  );
};

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>,
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react';

// Override render method
export { customRender as render };

// Mock data for tests
export const mockAgents = [
  {
    id: 'restock_agent',
    type: 'restock',
    status: 'running',
    health: 'healthy',
    last_heartbeat: '2024-01-01T12:00:00Z',
    uptime: 3600,
    performance: {
      actions_per_hour: 15,
      success_rate: 0.95,
      average_response_time: 2.5
    }
  },
  {
    id: 'route_agent',
    type: 'route',
    status: 'running',
    health: 'healthy',
    last_heartbeat: '2024-01-01T12:00:00Z',
    uptime: 3600,
    performance: {
      routes_optimized: 25,
      average_optimization_time: 1.8,
      fuel_savings: 0.12
    }
  },
  {
    id: 'pricing_agent',
    type: 'pricing',
    status: 'stopped',
    health: 'warning',
    last_heartbeat: '2024-01-01T11:45:00Z',
    uptime: 1800,
    performance: {
      price_updates: 8,
      revenue_impact: 0.08,
      market_accuracy: 0.87
    }
  }
];

export const mockFleet = [
  {
    id: 'fleet_001',
    vehicle_type: 'van',
    capacity: 1000,
    current_location: { lat: 40.7128, lng: -74.0060 },
    status: 'available',
    current_route: null,
    utilization_rate: 0.75,
    fuel_level: 0.8,
    driver_id: 'driver_001'
  },
  {
    id: 'fleet_002',
    vehicle_type: 'truck',
    capacity: 2000,
    current_location: { lat: 40.7589, lng: -73.9851 },
    status: 'in_transit',
    current_route: {
      id: 'route_001',
      waypoints: [
        { lat: 40.7589, lng: -73.9851 },
        { lat: 40.7505, lng: -73.9934 }
      ],
      estimated_completion: '2024-01-01T13:30:00Z'
    },
    utilization_rate: 0.9,
    fuel_level: 0.6,
    driver_id: 'driver_002'
  }
];

export const mockInventory = [
  {
    merchant_id: 'merchant_001',
    items: [
      { name: 'Item 1', quantity: 15, price: 5.99, threshold: 10 },
      { name: 'Item 2', quantity: 8, price: 12.99, threshold: 10 },
      { name: 'Item 3', quantity: 25, price: 3.50, threshold: 5 }
    ],
    last_updated: '2024-01-01T12:00:00Z',
    alerts: [
      { item_name: 'Item 2', current_quantity: 8, threshold: 10, severity: 'warning' }
    ]
  },
  {
    merchant_id: 'merchant_002',
    items: [
      { name: 'Product A', quantity: 50, price: 8.99, threshold: 20 },
      { name: 'Product B', quantity: 12, price: 15.99, threshold: 15 }
    ],
    last_updated: '2024-01-01T11:45:00Z',
    alerts: []
  }
];

export const mockMerchants = [
  {
    id: 'merchant_001',
    name: 'Downtown Deli',
    location: { lat: 40.7128, lng: -74.0060 },
    category: 'restaurant',
    status: 'active',
    rating: 4.5,
    order_volume: 150
  },
  {
    id: 'merchant_002',
    name: 'Uptown Market',
    location: { lat: 40.7589, lng: -73.9851 },
    category: 'retail',
    status: 'active',
    rating: 4.2,
    order_volume: 200
  }
];

export const mockForecasts = [
  {
    merchant_id: 'merchant_001',
    timestamp: '2024-01-01T12:00:00Z',
    demand_forecast: 180,
    confidence: 0.85,
    factors: {
      weather: 'sunny',
      events: ['local_festival'],
      seasonal_factor: 1.2
    }
  },
  {
    merchant_id: 'merchant_002',
    timestamp: '2024-01-01T12:00:00Z',
    demand_forecast: 220,
    confidence: 0.78,
    factors: {
      weather: 'partly_cloudy',
      events: [],
      seasonal_factor: 1.1
    }
  }
];

export const mockSimulationStatus = {
  status: 'running',
  is_running: true,
  current_tick: 144,
  total_ticks: 144,
  start_time: '2024-01-01T00:00:00Z',
  uptime: 21600,
  performance_metrics: {
    average_tick_time: 0.85,
    memory_usage: 512,
    cpu_usage: 0.25
  }
};

export const mockWebSocketMessage = {
  type: 'simulation_update',
  timestamp: '2024-01-01T12:00:00Z',
  data: {
    tick: 144,
    agents_status: mockAgents,
    fleet_status: mockFleet
  }
};

// Mock API responses
export const mockApiResponses = {
  agents: mockAgents,
  fleet: mockFleet,
  inventory: mockInventory,
  merchants: mockMerchants,
  forecasts: mockForecasts,
  simulationStatus: mockSimulationStatus
};

// Helper function to mock fetch responses
export const mockFetchResponse = (url: string, response: any) => {
  (global.fetch as jest.Mock).mockImplementation((requestUrl: string) => {
    if (requestUrl.includes(url)) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(response),
        status: 200,
      });
    }
    return Promise.resolve({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ error: 'Not found' }),
    });
  });
};

// Helper function to mock WebSocket
export const mockWebSocket = () => {
  const mockWs = {
    send: jest.fn(),
    close: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    readyState: WebSocket.OPEN,
  };
  
  (global.WebSocket as any) = jest.fn(() => mockWs);
  return mockWs;
};

// Helper function to wait for async operations
export const waitFor = (ms: number) => new Promise(resolve => setTimeout(resolve, ms)); 