const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

export interface AgentStatus {
  manager_running: boolean;
  agents_running: boolean;
  agents: {
    [key: string]: {
      is_active: boolean;
      agent_type: string;
      last_action_time: string | null;
    };
  };
  total_agents: number;
}

export interface AgentLog {
  id: string;
  agent_id: string;
  agent_type: string;
  action: string;
  details: string;
  status: string;
  timestamp: string;
}

export interface AgentAction {
  id: string;
  agent_id: string;
  action_type: string;
  target_table: string;
  status: string;
  created_at: number;
  [key: string]: any;
}

export interface SystemStats {
  inventory_items: number;
  orders: number;
  fleet_vehicles: number;
  agent_logs: number;
  agent_actions: number;
  agents_running: boolean;
}

class AgenticApiService {
  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${BACKEND_URL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Health check
  async getHealth(): Promise<any> {
    return this.makeRequest('/health');
  }

  // Agent management
  async startAgents(): Promise<any> {
    return this.makeRequest('/api/v1/agents/start', {
      method: 'POST',
    });
  }

  async stopAgents(): Promise<any> {
    return this.makeRequest('/api/v1/agents/stop', {
      method: 'POST',
    });
  }

  async getAgentStatus(): Promise<AgentStatus> {
    return this.makeRequest('/api/v1/agents/status');
  }

  // Agent logs and actions
  async getAgentLogs(limit: number = 50, agentId?: string): Promise<{ logs: AgentLog[]; total: number }> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (agentId) {
      params.append('agent_id', agentId);
    }
    
    return this.makeRequest(`/api/v1/agents/logs?${params.toString()}`);
  }

  async getAgentActions(limit: number = 50, status?: string): Promise<{ actions: AgentAction[]; total: number }> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (status) {
      params.append('status', status);
    }
    
    return this.makeRequest(`/api/v1/agents/actions?${params.toString()}`);
  }

  // Trigger specific agent actions
  async triggerAgentAction(agentType: string, action: string, data?: any): Promise<any> {
    const params = new URLSearchParams();
    params.append('agent_type', agentType);
    params.append('action', action);
    
    return this.makeRequest(`/api/v1/agents/trigger?${params.toString()}`, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // System statistics
  async getSystemStats(): Promise<SystemStats> {
    return this.makeRequest('/api/v1/system/stats');
  }

  async getSimulationStatus(): Promise<any> {
    return this.makeRequest('/api/v1/simulation/status');
  }

  async startSimulation(): Promise<any> {
    return this.makeRequest('/api/v1/simulation/start', { method: 'POST' });
  }

  async stopSimulation(): Promise<any> {
    return this.makeRequest('/api/v1/simulation/stop', { method: 'POST' });
  }

  async stepSimulation(): Promise<any> {
    return this.makeRequest('/api/v1/simulation/tick', { method: 'POST' });
  }

  async approveAction(actionId: string): Promise<any> {
    return this.makeRequest(`/api/v1/agents/actions/${actionId}/approve`, { method: 'POST' });
  }

  async declineAction(actionId: string): Promise<any> {
    return this.makeRequest(`/api/v1/agents/actions/${actionId}/decline`, { method: 'POST' });
  }

  // Inventory agent actions
  async triggerInventoryCheck(): Promise<any> {
    return this.triggerAgentAction('inventory', 'check_low_stock');
  }

  async triggerInventoryOptimization(): Promise<any> {
    return this.triggerAgentAction('inventory', 'optimize_inventory');
  }

  async triggerExpiredItemsHandling(): Promise<any> {
    return this.triggerAgentAction('inventory', 'handle_expired_items');
  }

  // Routing agent actions
  async triggerRouteOptimization(): Promise<any> {
    return this.triggerAgentAction('routing', 'optimize_routes');
  }

  async triggerVehicleAssignment(): Promise<any> {
    return this.triggerAgentAction('routing', 'assign_vehicles');
  }

  async triggerDynamicRouting(): Promise<any> {
    return this.triggerAgentAction('routing', 'handle_dynamic_routing');
  }

  // Pricing agent actions
  async triggerMarketAnalysis(): Promise<any> {
    return this.triggerAgentAction('pricing', 'analyze_market_conditions');
  }

  async triggerPricingOptimization(): Promise<any> {
    return this.triggerAgentAction('pricing', 'optimize_inventory_pricing');
  }

  async triggerDynamicPricing(): Promise<any> {
    return this.triggerAgentAction('pricing', 'handle_dynamic_pricing');
  }
}

export const agenticApi = new AgenticApiService(); 

// Export WebSocket helper separately for direct subscriptions where needed
export { agenticWebSocket } from './agenticWebSocket';
