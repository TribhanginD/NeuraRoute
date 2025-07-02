import { 
  AgenticWebSocketMessage, 
  WebSocketSubscription, 
  WebSocketSubscriptionResponse,
  SituationProcessedMessage,
  ActionApprovedMessage,
  ActionDeniedMessage,
  StatusUpdateMessage,
  SimulationModeChangedMessage
} from '../types/agentic';

export type WebSocketEventHandler = (message: AgenticWebSocketMessage) => void;

class AgenticWebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private eventHandlers: Map<string, WebSocketEventHandler[]> = new Map();
  private isConnecting = false;
  private url: string;

  constructor(baseUrl: string = '') {
    this.url = `${baseUrl}/api/v1/agentic/ws`;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      if (this.isConnecting) {
        reject(new Error('Connection already in progress'));
        return;
      }

      this.isConnecting = true;

      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('Agentic WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          
          // Subscribe to all events by default
          this.subscribe(['all']);
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: AgenticWebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('Agentic WebSocket disconnected:', event.code, event.reason);
          this.isConnecting = false;
          
          if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          console.error('Agentic WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  private scheduleReconnect(): void {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Scheduling WebSocket reconnect attempt ${this.reconnectAttempts} in ${delay}ms`);
    
    setTimeout(() => {
      this.connect().catch(error => {
        console.error('WebSocket reconnect failed:', error);
      });
    }, delay);
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this.eventHandlers.clear();
  }

  subscribe(eventTypes: string[]): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const subscription: WebSocketSubscription = {
        type: 'subscribe',
        events: eventTypes
      };
      this.ws.send(JSON.stringify(subscription));
    }
  }

  on(eventType: string, handler: WebSocketEventHandler): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType)!.push(handler);
  }

  off(eventType: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private handleMessage(message: AgenticWebSocketMessage): void {
    // Call handlers for specific event type
    const handlers = this.eventHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error('Error in WebSocket event handler:', error);
        }
      });
    }

    // Call handlers for 'all' events
    const allHandlers = this.eventHandlers.get('all');
    if (allHandlers) {
      allHandlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error('Error in WebSocket all event handler:', error);
        }
      });
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getConnectionState(): string {
    if (!this.ws) return 'disconnected';
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'connecting';
      case WebSocket.OPEN: return 'connected';
      case WebSocket.CLOSING: return 'closing';
      case WebSocket.CLOSED: return 'closed';
      default: return 'unknown';
    }
  }
}

// Export singleton instance
export const agenticWebSocket = new AgenticWebSocketService();

// Export types for convenience
export type { WebSocketEventHandler }; 