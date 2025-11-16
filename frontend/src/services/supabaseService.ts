const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000'

async function request<T>(path: string, params?: Record<string, string | number | undefined>): Promise<T> {
  const url = new URL(`${API_BASE}${path}`)
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value))
      }
    })
  }

  const response = await fetch(url.toString())
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

export class SupabaseService {
  async getFleet() {
    const data = await request<{ items: any[] }>('/api/v1/fleet')
    return data.items || []
  }

  async getRoutes() {
    const data = await request<{ items: any[] }>('/api/v1/routes')
    return data.items || []
  }

  async getOrders() {
    const data = await request<{ items: any[] }>('/api/v1/orders')
    return data.items || []
  }

  async getInventory() {
    const data = await request<{ items: any[] }>('/api/v1/inventory')
    return data.items || []
  }

  async getPurchaseOrders(limit = 20) {
    const data = await request<{ items: any[] }>('/api/v1/purchase-orders', { limit })
    return data.items || []
  }

  async getDisposalOrders(limit = 20) {
    const data = await request<{ items: any[] }>('/api/v1/disposal-orders', { limit })
    return data.items || []
  }

  async getAgentLogs(agentId: string | null = null, limit = 50) {
    const response = await request<{ logs: any[]; total: number }>('/api/v1/agents/logs', {
      limit,
      agent_id: agentId || undefined,
    })
    return response.logs || []
  }
}

export const supabaseService = new SupabaseService()
