import React from 'react';
import { render, screen, fireEvent, waitFor } from '../test-utils';
import Dashboard from '../../pages/Dashboard';
import { mockAgents, mockFleet, mockSimulationStatus, mockFetchResponse } from '../test-utils';

describe('Dashboard Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders dashboard with main sections', () => {
    render(<Dashboard />);
    
    expect(screen.getByText(/System Overview/i)).toBeInTheDocument();
    expect(screen.getByText(/Agent Status/i)).toBeInTheDocument();
    expect(screen.getByText(/Fleet Overview/i)).toBeInTheDocument();
    expect(screen.getByText(/Simulation Control/i)).toBeInTheDocument();
  });

  test('displays system metrics cards', () => {
    render(<Dashboard />);
    
    expect(screen.getByText(/Active Agents/i)).toBeInTheDocument();
    expect(screen.getByText(/Fleet Utilization/i)).toBeInTheDocument();
    expect(screen.getByText(/Orders Today/i)).toBeInTheDocument();
    expect(screen.getByText(/Revenue/i)).toBeInTheDocument();
  });

  test('shows agent status grid', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/restock_agent/i)).toBeInTheDocument();
      expect(screen.getByText(/route_agent/i)).toBeInTheDocument();
      expect(screen.getByText(/pricing_agent/i)).toBeInTheDocument();
    });
  });

  test('displays agent health indicators', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      // Check for health status indicators
      expect(screen.getByText(/healthy/i)).toBeInTheDocument();
      expect(screen.getByText(/warning/i)).toBeInTheDocument();
    });
  });

  test('shows fleet utilization chart', async () => {
    mockFetchResponse('/api/v1/fleet', mockFleet);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Fleet Utilization/i)).toBeInTheDocument();
      expect(screen.getByText(/75%/i)).toBeInTheDocument();
      expect(screen.getByText(/90%/i)).toBeInTheDocument();
    });
  });

  test('displays simulation status', async () => {
    mockFetchResponse('/api/v1/simulation/status', mockSimulationStatus);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/running/i)).toBeInTheDocument();
      expect(screen.getByText(/Tick: 144/i)).toBeInTheDocument();
    });
  });

  test('handles simulation start/stop controls', async () => {
    mockFetchResponse('/api/v1/simulation/status', mockSimulationStatus);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      const stopButton = screen.getByText(/Stop Simulation/i);
      fireEvent.click(stopButton);
    });
    
    // Should show confirmation or update status
    expect(screen.getByText(/Stopping/i)).toBeInTheDocument();
  });

  test('shows real-time updates from WebSocket', async () => {
    render(<Dashboard />);
    
    // Simulate WebSocket message
    const mockMessage = {
      type: 'dashboard_update',
      data: {
        agents: mockAgents,
        fleet: mockFleet,
        simulation: mockSimulationStatus
      }
    };
    
    // Trigger WebSocket message
    const event = new CustomEvent('websocket_message', { detail: mockMessage });
    window.dispatchEvent(event);
    
    await waitFor(() => {
      expect(screen.getByText(/restock_agent/i)).toBeInTheDocument();
    });
  });

  test('displays performance metrics', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Success Rate/i)).toBeInTheDocument();
      expect(screen.getByText(/95%/i)).toBeInTheDocument();
      expect(screen.getByText(/Response Time/i)).toBeInTheDocument();
      expect(screen.getByText(/2.5s/i)).toBeInTheDocument();
    });
  });

  test('shows alert notifications', async () => {
    const mockAlerts = [
      {
        id: 'alert_001',
        type: 'warning',
        message: 'Low inventory detected',
        timestamp: new Date().toISOString(),
        severity: 'medium'
      }
    ];
    
    mockFetchResponse('/api/v1/alerts', mockAlerts);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Low inventory detected/i)).toBeInTheDocument();
    });
  });

  test('handles agent control actions', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      const startButton = screen.getByText(/Start/i);
      fireEvent.click(startButton);
    });
    
    // Should show loading state
    expect(screen.getByText(/Starting/i)).toBeInTheDocument();
  });

  test('displays revenue and order metrics', async () => {
    const mockMetrics = {
      revenue_today: 12500.50,
      orders_today: 45,
      average_order_value: 277.79,
      growth_rate: 0.15
    };
    
    mockFetchResponse('/api/v1/metrics', mockMetrics);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/\$12,500/i)).toBeInTheDocument();
      expect(screen.getByText(/45/i)).toBeInTheDocument();
      expect(screen.getByText(/15%/i)).toBeInTheDocument();
    });
  });

  test('shows weather and external factors', async () => {
    const mockWeather = {
      condition: 'sunny',
      temperature: 25,
      humidity: 60,
      wind_speed: 10
    };
    
    mockFetchResponse('/api/v1/weather', mockWeather);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Weather/i)).toBeInTheDocument();
      expect(screen.getByText(/25°C/i)).toBeInTheDocument();
      expect(screen.getByText(/sunny/i)).toBeInTheDocument();
    });
  });

  test('handles error states gracefully', async () => {
    // Mock fetch to return error
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Error loading data/i)).toBeInTheDocument();
    });
  });

  test('shows loading states', () => {
    render(<Dashboard />);
    
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  test('displays time-based metrics', async () => {
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/Last Updated/i)).toBeInTheDocument();
      expect(screen.getByText(/Uptime/i)).toBeInTheDocument();
    });
  });

  test('handles responsive design', () => {
    render(<Dashboard />);
    
    // Check for responsive grid classes
    const gridContainer = screen.getByTestId('dashboard-grid');
    expect(gridContainer).toHaveClass('grid');
    expect(gridContainer).toHaveClass('md:grid-cols-2');
    expect(gridContainer).toHaveClass('lg:grid-cols-3');
  });

  test('shows data refresh controls', () => {
    render(<Dashboard />);
    
    const refreshButton = screen.getByLabelText(/refresh data/i);
    fireEvent.click(refreshButton);
    
    // Should trigger data refresh
    expect(screen.getByText(/Refreshing/i)).toBeInTheDocument();
  });

  test('displays system health indicators', async () => {
    const mockHealth = {
      database: 'healthy',
      redis: 'healthy',
      agents: 'warning',
      simulation: 'healthy'
    };
    
    mockFetchResponse('/api/v1/health', mockHealth);
    
    render(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/System Health/i)).toBeInTheDocument();
      expect(screen.getByText(/healthy/i)).toBeInTheDocument();
      expect(screen.getByText(/warning/i)).toBeInTheDocument();
    });
  });
}); 