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

class AgenticWebSocketService {
  private url: string;
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    // Remove WebSocket URL and connection logic
    // Only keep HTTP API methods
  }

  // API Methods for HTTP requests
  async getAgentStatus() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/agents/status`);
      if (!response.ok) throw new Error('Failed to fetch agent status');
      return await response.json();
    } catch (error) {
      console.error('Error fetching agent status:', error);
      return { agents: {} };
    }
  }

  async getAgentActions() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/agents/actions`);
      if (!response.ok) throw new Error('Failed to fetch agent actions');
      return await response.json();
    } catch (error) {
      console.error('Error fetching agent actions:', error);
      return { actions: [] };
    }
  }

  async getAgentLogs() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/agents/logs`);
      if (!response.ok) throw new Error('Failed to fetch agent logs');
      return await response.json();
    } catch (error) {
      console.error('Error fetching agent logs:', error);
      return { logs: [] };
    }
  }

  async approveAction(actionId: string) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/agents/actions/${actionId}/approve`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to approve action');
      return await response.json();
    } catch (error) {
      console.error('Error approving action:', error);
      throw error;
    }
  }

  async declineAction(actionId: string) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/agents/actions/${actionId}/decline`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to decline action');
      return await response.json();
    } catch (error) {
      console.error('Error declining action:', error);
      throw error;
    }
  }

  async triggerAgent(agentType: string, action: string) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/agents/trigger?agent_type=${agentType}&action=${action}`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to trigger agent');
      return await response.json();
    } catch (error) {
      console.error('Error triggering agent:', error);
      throw error;
    }
  }

  async getSimulationStatus() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/system/stats`);
      if (!response.ok) throw new Error('Failed to fetch simulation status');
      return await response.json();
    } catch (error) {
      console.error('Error fetching simulation status:', error);
      return { status: 'unknown' };
    }
  }

  async startAgents() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/agents/start`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to start agents');
      return await response.json();
    } catch (error) {
      console.error('Error starting agents:', error);
      throw error;
    }
  }

  async stopAgents() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/agents/stop`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to stop agents');
      return await response.json();
    } catch (error) {
      console.error('Error stopping agents:', error);
      throw error;
    }
  }

  // Remove all WebSocket specific methods
  // connect(): Promise<void> { ... }
  // private scheduleReconnect(): void { ... }
  // disconnect(): void { ... }
  // subscribe(eventTypes: string[]): void { ... }
  // on(eventType: string, handler: WebSocketEventHandler): void { ... }
  // off(eventType: string, handler: WebSocketEventHandler): void { ... }
  // private handleMessage(message: AgenticWebSocketMessage): void { ... }
  // isConnected(): boolean { ... }
  // getConnectionState(): string { ... }

  // Only keep HTTP API methods and the class export
}

// Export singleton instance
export const agenticWebSocket = new AgenticWebSocketService(); 