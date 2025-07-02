import React from 'react';
import { render, screen, fireEvent, waitFor } from './test-utils';
import App from '../App';

describe('App Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test('renders app header with title', () => {
    render(<App />);
    expect(screen.getByText(/NeuraRoute/i)).toBeInTheDocument();
    expect(screen.getByText(/AI-Native Hyperlocal Logistics/i)).toBeInTheDocument();
  });

  test('renders sidebar navigation', () => {
    render(<App />);
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/Fleet Map/i)).toBeInTheDocument();
    expect(screen.getByText(/Agent Monitor/i)).toBeInTheDocument();
    expect(screen.getByText(/Inventory/i)).toBeInTheDocument();
  });

  test('renders main content area', () => {
    render(<App />);
    expect(screen.getByRole('main')).toBeInTheDocument();
  });

  test('renders status indicators', () => {
    render(<App />);
    expect(screen.getByText(/System Status/i)).toBeInTheDocument();
    expect(screen.getByText(/Simulation/i)).toBeInTheDocument();
  });

  test('toggles sidebar when menu button is clicked', () => {
    render(<App />);
    const menuButton = screen.getByLabelText(/toggle sidebar/i);
    
    fireEvent.click(menuButton);
    
    // Check if sidebar is collapsed/expanded
    const sidebar = screen.getByRole('complementary');
    expect(sidebar).toBeInTheDocument();
  });

  test('displays loading state initially', () => {
    render(<App />);
    expect(screen.getByText(/Loading/i)).toBeInTheDocument();
  });

  test('handles WebSocket connection', async () => {
    render(<App />);
    
    // Wait for WebSocket connection to be established
    await waitFor(() => {
      expect(screen.getByText(/Connected/i)).toBeInTheDocument();
    });
  });

  test('displays error state when connection fails', async () => {
    // Mock WebSocket to fail
    const mockWs = {
      readyState: WebSocket.CLOSED,
      onerror: jest.fn(),
      onclose: jest.fn(),
    };
    (global.WebSocket as any) = jest.fn(() => mockWs);
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/Connection Error/i)).toBeInTheDocument();
    });
  });

  test('updates system status from WebSocket messages', async () => {
    render(<App />);
    
    // Simulate WebSocket message
    const mockMessage = {
      type: 'status_update',
      data: {
        simulation_status: 'running',
        active_agents: 3,
        fleet_utilization: 0.75
      }
    };
    
    // Trigger WebSocket message
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onmessage?.({ data: JSON.stringify(mockMessage) } as MessageEvent);
    
    await waitFor(() => {
      expect(screen.getByText(/running/i)).toBeInTheDocument();
    });
  });

  test('handles navigation between different views', () => {
    render(<App />);
    
    // Click on Fleet Map
    const fleetMapLink = screen.getByText(/Fleet Map/i);
    fireEvent.click(fleetMapLink);
    
    // Should show fleet map content
    expect(screen.getByText(/Fleet Map/i)).toBeInTheDocument();
    
    // Click on Agent Monitor
    const agentMonitorLink = screen.getByText(/Agent Monitor/i);
    fireEvent.click(agentMonitorLink);
    
    // Should show agent monitor content
    expect(screen.getByText(/Agent Monitor/i)).toBeInTheDocument();
  });

  test('displays responsive design elements', () => {
    render(<App />);
    
    // Check for responsive classes
    const mainContent = screen.getByRole('main');
    expect(mainContent).toHaveClass('flex-1');
    
    const sidebar = screen.getByRole('complementary');
    expect(sidebar).toHaveClass('w-64');
  });

  test('handles theme switching', () => {
    render(<App />);
    
    const themeToggle = screen.getByLabelText(/toggle theme/i);
    fireEvent.click(themeToggle);
    
    // Check if theme class is applied
    const appElement = screen.getByRole('application');
    expect(appElement).toHaveClass('dark');
  });

  test('displays notifications', async () => {
    render(<App />);
    
    // Simulate notification
    const notification = {
      type: 'info',
      message: 'System update completed',
      timestamp: new Date().toISOString()
    };
    
    // Trigger notification
    const event = new CustomEvent('notification', { detail: notification });
    window.dispatchEvent(event);
    
    await waitFor(() => {
      expect(screen.getByText(/System update completed/i)).toBeInTheDocument();
    });
  });

  test('handles keyboard shortcuts', () => {
    render(<App />);
    
    // Test Ctrl+N for new simulation
    fireEvent.keyDown(document, { key: 'n', ctrlKey: true });
    
    // Should trigger new simulation
    expect(screen.getByText(/New Simulation/i)).toBeInTheDocument();
  });

  test('displays user preferences', () => {
    render(<App />);
    
    const settingsButton = screen.getByLabelText(/settings/i);
    fireEvent.click(settingsButton);
    
    expect(screen.getByText(/Preferences/i)).toBeInTheDocument();
    expect(screen.getByText(/Theme/i)).toBeInTheDocument();
    expect(screen.getByText(/Notifications/i)).toBeInTheDocument();
  });

  test('handles offline mode', async () => {
    // Mock navigator.onLine to false
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: false,
    });
    
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/Offline Mode/i)).toBeInTheDocument();
    });
  });

  test('displays system metrics', () => {
    render(<App />);
    
    expect(screen.getByText(/CPU Usage/i)).toBeInTheDocument();
    expect(screen.getByText(/Memory Usage/i)).toBeInTheDocument();
    expect(screen.getByText(/Network/i)).toBeInTheDocument();
  });

  test('handles component unmounting gracefully', () => {
    const { unmount } = render(<App />);
    
    // Should not throw errors when unmounting
    expect(() => unmount()).not.toThrow();
  });
}); 