import React from 'react';
import { render, screen, fireEvent, waitFor } from '../test-utils';
import AgentMonitor from '../../pages/AgentMonitor';
import { mockAgents, mockFetchResponse } from '../test-utils';

describe('AgentMonitor Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders agent monitor with title', () => {
    render(<AgentMonitor />);
    
    expect(screen.getByText(/Agent Monitor/i)).toBeInTheDocument();
    expect(screen.getByText(/Real-time Agent Status/i)).toBeInTheDocument();
  });

  test('displays agent status grid', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText(/restock_agent/i)).toBeInTheDocument();
      expect(screen.getByText(/route_agent/i)).toBeInTheDocument();
      expect(screen.getByText(/pricing_agent/i)).toBeInTheDocument();
    });
  });

  test('shows agent health indicators', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      const healthyAgents = screen.getAllByText(/healthy/i);
      const warningAgents = screen.getAllByText(/warning/i);
      
      expect(healthyAgents.length).toBeGreaterThan(0);
      expect(warningAgents.length).toBeGreaterThan(0);
    });
  });

  test('displays agent performance metrics', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText(/Success Rate/i)).toBeInTheDocument();
      expect(screen.getByText(/95%/i)).toBeInTheDocument();
      expect(screen.getByText(/Response Time/i)).toBeInTheDocument();
      expect(screen.getByText(/2.5s/i)).toBeInTheDocument();
    });
  });

  test('shows agent control buttons', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      const startButtons = screen.getAllByText(/Start/i);
      const stopButtons = screen.getAllByText(/Stop/i);
      
      expect(startButtons.length).toBeGreaterThan(0);
      expect(stopButtons.length).toBeGreaterThan(0);
    });
  });

  test('handles agent start action', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      const startButton = screen.getByText(/Start/i);
      fireEvent.click(startButton);
      
      expect(screen.getByText(/Starting agent/i)).toBeInTheDocument();
    });
  });

  test('handles agent stop action', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      const stopButton = screen.getByText(/Stop/i);
      fireEvent.click(stopButton);
      
      expect(screen.getByText(/Stopping agent/i)).toBeInTheDocument();
    });
  });

  test('displays agent logs', async () => {
    const mockLogs = [
      {
        timestamp: '2024-01-01T12:00:00Z',
        level: 'info',
        message: 'Agent started successfully',
        agent_id: 'restock_agent'
      },
      {
        timestamp: '2024-01-01T12:01:00Z',
        level: 'warning',
        message: 'Low inventory detected',
        agent_id: 'restock_agent'
      }
    ];
    
    mockFetchResponse('/api/v1/agents/restock_agent/logs', mockLogs);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      const viewLogsButton = screen.getByText(/View Logs/i);
      fireEvent.click(viewLogsButton);
      
      expect(screen.getByText(/Agent started successfully/i)).toBeInTheDocument();
      expect(screen.getByText(/Low inventory detected/i)).toBeInTheDocument();
    });
  });

  test('shows agent uptime information', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText(/Uptime/i)).toBeInTheDocument();
      expect(screen.getByText(/1h/i)).toBeInTheDocument();
      expect(screen.getByText(/30m/i)).toBeInTheDocument();
    });
  });

  test('displays last heartbeat time', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText(/Last Heartbeat/i)).toBeInTheDocument();
      expect(screen.getByText(/12:00 PM/i)).toBeInTheDocument();
    });
  });

  test('shows agent type indicators', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText(/restock/i)).toBeInTheDocument();
      expect(screen.getByText(/route/i)).toBeInTheDocument();
      expect(screen.getByText(/pricing/i)).toBeInTheDocument();
    });
  });

  test('handles real-time updates from WebSocket', async () => {
    render(<AgentMonitor />);
    
    // Simulate WebSocket agent update
    const mockAgentUpdate = {
      type: 'agent_update',
      data: {
        agent_id: 'restock_agent',
        status: 'running',
        health: 'healthy',
        performance: {
          actions_per_hour: 20,
          success_rate: 0.98,
          average_response_time: 2.0
        }
      }
    };
    
    const event = new CustomEvent('websocket_message', { detail: mockAgentUpdate });
    window.dispatchEvent(event);
    
    await waitFor(() => {
      expect(screen.getByText(/98%/i)).toBeInTheDocument();
      expect(screen.getByText(/2.0s/i)).toBeInTheDocument();
    });
  });

  test('shows agent configuration', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      const configButton = screen.getByText(/Configuration/i);
      fireEvent.click(configButton);
      
      expect(screen.getByText(/Agent Configuration/i)).toBeInTheDocument();
      expect(screen.getByText(/Settings/i)).toBeInTheDocument();
    });
  });

  test('displays agent statistics', async () => {
    const mockStats = {
      total_actions: 1500,
      successful_actions: 1425,
      failed_actions: 75,
      average_response_time: 2.5,
      uptime_percentage: 99.5
    };
    
    mockFetchResponse('/api/v1/agents/restock_agent/stats', mockStats);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      const statsButton = screen.getByText(/Statistics/i);
      fireEvent.click(statsButton);
      
      expect(screen.getByText(/Total Actions/i)).toBeInTheDocument();
      expect(screen.getByText(/1500/i)).toBeInTheDocument();
      expect(screen.getByText(/99.5%/i)).toBeInTheDocument();
    });
  });

  test('handles agent filtering', () => {
    render(<AgentMonitor />);
    
    const filterInput = screen.getByPlaceholderText(/Filter agents/i);
    fireEvent.change(filterInput, { target: { value: 'restock' } });
    
    expect(filterInput).toHaveValue('restock');
  });

  test('shows agent alerts', async () => {
    const mockAlerts = [
      {
        id: 'alert_001',
        agent_id: 'restock_agent',
        type: 'warning',
        message: 'High memory usage detected',
        timestamp: new Date().toISOString(),
        severity: 'medium'
      }
    ];
    
    mockFetchResponse('/api/v1/agents/alerts', mockAlerts);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText(/High memory usage detected/i)).toBeInTheDocument();
    });
  });

  test('displays agent dependencies', async () => {
    const mockDependencies = {
      database: 'connected',
      redis: 'connected',
      external_api: 'disconnected'
    };
    
    mockFetchResponse('/api/v1/agents/restock_agent/dependencies', mockDependencies);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      const depsButton = screen.getByText(/Dependencies/i);
      fireEvent.click(depsButton);
      
      expect(screen.getByText(/Database/i)).toBeInTheDocument();
      expect(screen.getByText(/Connected/i)).toBeInTheDocument();
      expect(screen.getByText(/Disconnected/i)).toBeInTheDocument();
    });
  });

  test('handles agent restart', async () => {
    mockFetchResponse('/api/v1/agents', mockAgents);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      const restartButton = screen.getByText(/Restart/i);
      fireEvent.click(restartButton);
      
      expect(screen.getByText(/Restarting agent/i)).toBeInTheDocument();
    });
  });

  test('shows agent memory usage', async () => {
    const mockMemory = {
      current_usage: 256,
      max_usage: 512,
      heap_size: 1024,
      gc_count: 15
    };
    
    mockFetchResponse('/api/v1/agents/restock_agent/memory', mockMemory);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      const memoryButton = screen.getByText(/Memory/i);
      fireEvent.click(memoryButton);
      
      expect(screen.getByText(/Current Usage/i)).toBeInTheDocument();
      expect(screen.getByText(/256 MB/i)).toBeInTheDocument();
      expect(screen.getByText(/50%/i)).toBeInTheDocument();
    });
  });

  test('displays agent error history', async () => {
    const mockErrors = [
      {
        timestamp: '2024-01-01T11:30:00Z',
        error_type: 'ConnectionError',
        message: 'Failed to connect to database',
        stack_trace: 'Error: Connection timeout'
      }
    ];
    
    mockFetchResponse('/api/v1/agents/restock_agent/errors', mockErrors);
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      const errorsButton = screen.getByText(/Errors/i);
      fireEvent.click(errorsButton);
      
      expect(screen.getByText(/ConnectionError/i)).toBeInTheDocument();
      expect(screen.getByText(/Failed to connect to database/i)).toBeInTheDocument();
    });
  });

  test('handles error states gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
    
    render(<AgentMonitor />);
    
    await waitFor(() => {
      expect(screen.getByText(/Error loading agents/i)).toBeInTheDocument();
    });
  });

  test('shows loading state', () => {
    render(<AgentMonitor />);
    
    expect(screen.getByText(/Loading agents/i)).toBeInTheDocument();
  });

  test('handles responsive design', () => {
    render(<AgentMonitor />);
    
    const gridContainer = screen.getByTestId('agent-grid');
    expect(gridContainer).toHaveClass('grid');
    expect(gridContainer).toHaveClass('md:grid-cols-2');
    expect(gridContainer).toHaveClass('lg:grid-cols-3');
  });

  test('displays refresh controls', () => {
    render(<AgentMonitor />);
    
    const refreshButton = screen.getByLabelText(/refresh agents/i);
    fireEvent.click(refreshButton);
    
    expect(screen.getByText(/Refreshing/i)).toBeInTheDocument();
  });
}); 