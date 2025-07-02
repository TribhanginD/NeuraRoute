import React from 'react';
import { render, screen, fireEvent, waitFor } from '../test-utils';
import FleetMap from '../../pages/FleetMap';
import { mockFleet, mockFetchResponse } from '../test-utils';

describe('FleetMap Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders fleet map container', () => {
    render(<FleetMap />);
    
    expect(screen.getByText(/Fleet Map/i)).toBeInTheDocument();
    expect(screen.getByTestId('map-container')).toBeInTheDocument();
  });

  test('displays map controls', () => {
    render(<FleetMap />);
    
    expect(screen.getByLabelText(/zoom in/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/zoom out/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/fullscreen/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/my location/i)).toBeInTheDocument();
  });

  test('shows fleet status panel', async () => {
    mockFetchResponse('/api/v1/fleet', mockFleet);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      expect(screen.getByText(/Fleet Status/i)).toBeInTheDocument();
      expect(screen.getByText(/Available/i)).toBeInTheDocument();
      expect(screen.getByText(/In Transit/i)).toBeInTheDocument();
    });
  });

  test('displays vehicle markers on map', async () => {
    mockFetchResponse('/api/v1/fleet', mockFleet);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      expect(screen.getByText(/fleet_001/i)).toBeInTheDocument();
      expect(screen.getByText(/fleet_002/i)).toBeInTheDocument();
    });
  });

  test('shows vehicle details on marker click', async () => {
    mockFetchResponse('/api/v1/fleet', mockFleet);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      const vehicleMarker = screen.getByText(/fleet_001/i);
      fireEvent.click(vehicleMarker);
      
      expect(screen.getByText(/Vehicle Details/i)).toBeInTheDocument();
      expect(screen.getByText(/van/i)).toBeInTheDocument();
      expect(screen.getByText(/1000/i)).toBeInTheDocument();
      expect(screen.getByText(/75%/i)).toBeInTheDocument();
    });
  });

  test('displays route information', async () => {
    mockFetchResponse('/api/v1/fleet', mockFleet);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      const inTransitVehicle = screen.getByText(/fleet_002/i);
      fireEvent.click(inTransitVehicle);
      
      expect(screen.getByText(/Current Route/i)).toBeInTheDocument();
      expect(screen.getByText(/route_001/i)).toBeInTheDocument();
      expect(screen.getByText(/Estimated Completion/i)).toBeInTheDocument();
    });
  });

  test('shows real-time location updates', async () => {
    render(<FleetMap />);
    
    // Simulate WebSocket location update
    const mockLocationUpdate = {
      type: 'location_update',
      data: {
        fleet_id: 'fleet_001',
        location: { lat: 40.7200, lng: -74.0100 },
        timestamp: new Date().toISOString()
      }
    };
    
    const event = new CustomEvent('websocket_message', { detail: mockLocationUpdate });
    window.dispatchEvent(event);
    
    await waitFor(() => {
      expect(screen.getByText(/Location Updated/i)).toBeInTheDocument();
    });
  });

  test('handles map zoom controls', () => {
    render(<FleetMap />);
    
    const zoomInButton = screen.getByLabelText(/zoom in/i);
    const zoomOutButton = screen.getByLabelText(/zoom out/i);
    
    fireEvent.click(zoomInButton);
    fireEvent.click(zoomOutButton);
    
    // Map should respond to zoom controls
    expect(zoomInButton).toBeInTheDocument();
    expect(zoomOutButton).toBeInTheDocument();
  });

  test('displays traffic information', async () => {
    const mockTraffic = {
      congestion_level: 'medium',
      affected_routes: ['route_001'],
      estimated_delay: 15
    };
    
    mockFetchResponse('/api/v1/traffic', mockTraffic);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      expect(screen.getByText(/Traffic Info/i)).toBeInTheDocument();
      expect(screen.getByText(/Medium Congestion/i)).toBeInTheDocument();
      expect(screen.getByText(/15 min delay/i)).toBeInTheDocument();
    });
  });

  test('shows weather overlay', async () => {
    const mockWeather = {
      condition: 'rainy',
      temperature: 18,
      visibility: 'good',
      wind_speed: 15
    };
    
    mockFetchResponse('/api/v1/weather', mockWeather);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      const weatherToggle = screen.getByLabelText(/weather overlay/i);
      fireEvent.click(weatherToggle);
      
      expect(screen.getByText(/Weather/i)).toBeInTheDocument();
      expect(screen.getByText(/18°C/i)).toBeInTheDocument();
      expect(screen.getByText(/rainy/i)).toBeInTheDocument();
    });
  });

  test('handles route optimization', async () => {
    mockFetchResponse('/api/v1/fleet', mockFleet);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      const optimizeButton = screen.getByText(/Optimize Routes/i);
      fireEvent.click(optimizeButton);
      
      expect(screen.getByText(/Optimizing/i)).toBeInTheDocument();
    });
  });

  test('displays fuel levels', async () => {
    mockFetchResponse('/api/v1/fleet', mockFleet);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      const vehicleMarker = screen.getByText(/fleet_001/i);
      fireEvent.click(vehicleMarker);
      
      expect(screen.getByText(/Fuel Level/i)).toBeInTheDocument();
      expect(screen.getByText(/80%/i)).toBeInTheDocument();
    });
  });

  test('shows driver information', async () => {
    mockFetchResponse('/api/v1/fleet', mockFleet);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      const vehicleMarker = screen.getByText(/fleet_001/i);
      fireEvent.click(vehicleMarker);
      
      expect(screen.getByText(/Driver/i)).toBeInTheDocument();
      expect(screen.getByText(/driver_001/i)).toBeInTheDocument();
    });
  });

  test('handles map layer toggles', () => {
    render(<FleetMap />);
    
    const satelliteToggle = screen.getByLabelText(/satellite view/i);
    const trafficToggle = screen.getByLabelText(/traffic layer/i);
    
    fireEvent.click(satelliteToggle);
    fireEvent.click(trafficToggle);
    
    expect(satelliteToggle).toBeChecked();
    expect(trafficToggle).toBeChecked();
  });

  test('displays emergency alerts', async () => {
    const mockAlerts = [
      {
        id: 'alert_001',
        type: 'emergency',
        message: 'Vehicle breakdown reported',
        location: { lat: 40.7128, lng: -74.0060 },
        severity: 'high'
      }
    ];
    
    mockFetchResponse('/api/v1/alerts', mockAlerts);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      expect(screen.getByText(/Emergency Alert/i)).toBeInTheDocument();
      expect(screen.getByText(/Vehicle breakdown reported/i)).toBeInTheDocument();
    });
  });

  test('handles search functionality', () => {
    render(<FleetMap />);
    
    const searchInput = screen.getByPlaceholderText(/Search vehicles/i);
    fireEvent.change(searchInput, { target: { value: 'fleet_001' } });
    
    expect(searchInput).toHaveValue('fleet_001');
  });

  test('shows performance metrics', async () => {
    const mockMetrics = {
      average_speed: 35,
      total_distance: 1250,
      fuel_efficiency: 8.5,
      on_time_delivery: 0.92
    };
    
    mockFetchResponse('/api/v1/fleet/metrics', mockMetrics);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      expect(screen.getByText(/Performance/i)).toBeInTheDocument();
      expect(screen.getByText(/35 mph/i)).toBeInTheDocument();
      expect(screen.getByText(/92%/i)).toBeInTheDocument();
    });
  });

  test('handles fullscreen mode', () => {
    render(<FleetMap />);
    
    const fullscreenButton = screen.getByLabelText(/fullscreen/i);
    fireEvent.click(fullscreenButton);
    
    // Should toggle fullscreen state
    expect(fullscreenButton).toBeInTheDocument();
  });

  test('displays time-based information', async () => {
    mockFetchResponse('/api/v1/fleet', mockFleet);
    
    render(<FleetMap />);
    
    await waitFor(() => {
      expect(screen.getByText(/Last Updated/i)).toBeInTheDocument();
      expect(screen.getByText(/ETA/i)).toBeInTheDocument();
    });
  });

  test('handles error states', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
    
    render(<FleetMap />);
    
    await waitFor(() => {
      expect(screen.getByText(/Error loading fleet data/i)).toBeInTheDocument();
    });
  });

  test('shows loading state', () => {
    render(<FleetMap />);
    
    expect(screen.getByText(/Loading map/i)).toBeInTheDocument();
  });

  test('handles responsive design', () => {
    render(<FleetMap />);
    
    const mapContainer = screen.getByTestId('map-container');
    expect(mapContainer).toHaveClass('h-full');
    expect(mapContainer).toHaveClass('w-full');
  });
}); 