// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

// Mock WebSocket
global.WebSocket = class MockWebSocket {
  url: string;
  readyState: number;
  onopen: ((event: Event) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  send: (data: string | ArrayBufferLike | Blob | ArrayBufferView) => void;

  constructor(url: string) {
    this.url = url;
    this.readyState = WebSocket.CONNECTING;
    this.send = jest.fn();
    
    // Simulate connection
    setTimeout(() => {
      this.readyState = WebSocket.OPEN;
      if (this.onopen) {
        this.onopen(new Event('open'));
      }
    }, 0);
  }

  close() {
    this.readyState = WebSocket.CLOSED;
    if (this.onclose) {
      this.onclose(new CloseEvent('close'));
    }
  }
} as any;

// Mock Mapbox
global.mapboxgl = {
  Map: jest.fn().mockImplementation(() => ({
    on: jest.fn(),
    off: jest.fn(),
    addSource: jest.fn(),
    addLayer: jest.fn(),
    removeLayer: jest.fn(),
    removeSource: jest.fn(),
    setPaintProperty: jest.fn(),
    setLayoutProperty: jest.fn(),
    getSource: jest.fn(),
    getLayer: jest.fn(),
    resize: jest.fn(),
    remove: jest.fn(),
  })),
  LngLat: jest.fn().mockImplementation((lng: number, lat: number) => ({
    lng,
    lat,
    toArray: () => [lng, lat],
  })),
  LngLatBounds: jest.fn().mockImplementation(() => ({
    extend: jest.fn().mockReturnThis(),
    toArray: () => [[-180, -90], [180, 90]],
  })),
  Popup: jest.fn().mockImplementation(() => ({
    setLngLat: jest.fn().mockReturnThis(),
    setHTML: jest.fn().mockReturnThis(),
    addTo: jest.fn().mockReturnThis(),
    remove: jest.fn(),
  })),
  Marker: jest.fn().mockImplementation(() => ({
    setLngLat: jest.fn().mockReturnThis(),
    setPopup: jest.fn().mockReturnThis(),
    addTo: jest.fn().mockReturnThis(),
    remove: jest.fn(),
  })),
  NavigationControl: jest.fn().mockImplementation(() => ({
    addTo: jest.fn().mockReturnThis(),
  })),
  GeolocateControl: jest.fn().mockImplementation(() => ({
    addTo: jest.fn().mockReturnThis(),
  })),
  FullscreenControl: jest.fn().mockImplementation(() => ({
    addTo: jest.fn().mockReturnThis(),
  })),
  accessToken: 'test-token',
} as any;

// Mock Leaflet
global.L = {
  map: jest.fn().mockImplementation(() => ({
    setView: jest.fn().mockReturnThis(),
    addLayer: jest.fn().mockReturnThis(),
    removeLayer: jest.fn().mockReturnThis(),
    on: jest.fn().mockReturnThis(),
    off: jest.fn().mockReturnThis(),
    invalidateSize: jest.fn(),
    remove: jest.fn(),
  })),
  tileLayer: jest.fn().mockImplementation(() => ({
    addTo: jest.fn().mockReturnThis(),
  })),
  marker: jest.fn().mockImplementation(() => ({
    addTo: jest.fn().mockReturnThis(),
    bindPopup: jest.fn().mockReturnThis(),
    setLatLng: jest.fn().mockReturnThis(),
  })),
  popup: jest.fn().mockImplementation(() => ({
    setLatLng: jest.fn().mockReturnThis(),
    setContent: jest.fn().mockReturnThis(),
    openOn: jest.fn().mockReturnThis(),
  })),
  latLng: jest.fn().mockImplementation((lat: number, lng: number) => ({
    lat,
    lng,
  })),
  icon: jest.fn().mockImplementation(() => ({
    iconUrl: '',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
  })),
} as any;

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn();

// Mock console methods to reduce noise in tests
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  console.error = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
  
  console.warn = (...args: any[]) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning: componentWillReceiveProps') ||
       args[0].includes('Warning: componentWillUpdate'))
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
  console.warn = originalWarn;
}); 