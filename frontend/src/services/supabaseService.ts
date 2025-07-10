import { supabase, typedSupabase, Database } from './supabaseClient.ts'

type FleetRow = Database['public']['Tables']['fleet']['Row']
type FleetInsert = Database['public']['Tables']['fleet']['Insert']
type FleetUpdate = Database['public']['Tables']['fleet']['Update']

type MerchantRow = Database['public']['Tables']['merchants']['Row']
type MerchantInsert = Database['public']['Tables']['merchants']['Insert']
type MerchantUpdate = Database['public']['Tables']['merchants']['Update']

type InventoryRow = Database['public']['Tables']['inventory']['Row']
type InventoryInsert = Database['public']['Tables']['inventory']['Insert']
type InventoryUpdate = Database['public']['Tables']['inventory']['Update']

type OrderRow = Database['public']['Tables']['orders']['Row']
type OrderInsert = Database['public']['Tables']['orders']['Insert']
type OrderUpdate = Database['public']['Tables']['orders']['Update']

export class SupabaseService {
  // Fleet operations
  async getFleet(): Promise<FleetRow[]> {
    console.log('🔍 Fetching fleet data from Supabase...');
    try {
      const { data, error } = await typedSupabase
        .from('fleet')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) {
        console.error('❌ Error fetching fleet:', error);
        return []
      }
      
      console.log('✅ Fleet data fetched successfully:', data);
      return data || []
    } catch (err) {
      console.error('❌ Exception fetching fleet:', err);
      return []
    }
  }

  async getFleetById(id: string): Promise<FleetRow | null> {
    const { data, error } = await typedSupabase
      .from('fleet')
      .select('*')
      .eq('id', id)
      .single()
    
    if (error) {
      console.error('Error fetching fleet by ID:', error)
      return null
    }
    
    return data
  }

  async createFleet(fleet: FleetInsert): Promise<FleetRow | null> {
    const { data, error } = await typedSupabase
      .from('fleet')
      .insert(fleet)
      .select()
      .single()
    
    if (error) {
      console.error('Error creating fleet:', error)
      return null
    }
    
    return data
  }

  async updateFleet(id: string, updates: FleetUpdate): Promise<FleetRow | null> {
    const { data, error } = await typedSupabase
      .from('fleet')
      .update(updates)
      .eq('id', id)
      .select()
      .single()
    
    if (error) {
      console.error('Error updating fleet:', error)
      return null
    }
    
    return data
  }

  async deleteFleet(id: string): Promise<boolean> {
    const { error } = await typedSupabase
      .from('fleet')
      .delete()
      .eq('id', id)
    
    if (error) {
      console.error('Error deleting fleet:', error)
      return false
    }
    
    return true
  }

  // Merchant operations
  async getMerchants(): Promise<MerchantRow[]> {
    const { data, error } = await typedSupabase
      .from('merchants')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) {
      console.error('Error fetching merchants:', error)
      return []
    }
    
    return data || []
  }

  async getMerchantById(id: string): Promise<MerchantRow | null> {
    const { data, error } = await typedSupabase
      .from('merchants')
      .select('*')
      .eq('id', id)
      .single()
    
    if (error) {
      console.error('Error fetching merchant by ID:', error)
      return null
    }
    
    return data
  }

  async createMerchant(merchant: MerchantInsert): Promise<MerchantRow | null> {
    const { data, error } = await typedSupabase
      .from('merchants')
      .insert(merchant)
      .select()
      .single()
    
    if (error) {
      console.error('Error creating merchant:', error)
      return null
    }
    
    return data
  }

  async updateMerchant(id: string, updates: MerchantUpdate): Promise<MerchantRow | null> {
    const { data, error } = await typedSupabase
      .from('merchants')
      .update(updates)
      .eq('id', id)
      .select()
      .single()
    
    if (error) {
      console.error('Error updating merchant:', error)
      return null
    }
    
    return data
  }

  async deleteMerchant(id: string): Promise<boolean> {
    const { error } = await typedSupabase
      .from('merchants')
      .delete()
      .eq('id', id)
    
    if (error) {
      console.error('Error deleting merchant:', error)
      return false
    }
    
    return true
  }

  async getMerchantByName(name: string): Promise<MerchantRow | null> {
    const { data, error } = await typedSupabase
      .from('merchants')
      .select('*')
      .eq('name', name)
      .single();
    if (error) {
      console.error('Error fetching merchant by name:', error);
      return null;
    }
    return data;
  }

  // Inventory operations
  async getInventory(): Promise<InventoryRow[]> {
    console.log('🔍 Fetching inventory data from Supabase...');
    try {
      const { data, error } = await typedSupabase
        .from('inventory')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) {
        console.error('❌ Error fetching inventory:', error);
        return []
      }
      
      console.log('✅ Inventory data fetched successfully:', data);
      return data || []
    } catch (err) {
      console.error('❌ Exception fetching inventory:', err);
      return []
    }
  }

  async getInventoryById(id: string): Promise<InventoryRow | null> {
    const { data, error } = await typedSupabase
      .from('inventory')
      .select('*')
      .eq('id', id)
      .single()
    
    if (error) {
      console.error('Error fetching inventory by ID:', error)
      return null
    }
    
    return data
  }

  async createInventory(inventory: InventoryInsert): Promise<InventoryRow | null> {
    const { data, error } = await typedSupabase
      .from('inventory')
      .insert(inventory)
      .select()
      .single()
    
    if (error) {
      console.error('Error creating inventory:', error)
      return null
    }
    
    return data
  }

  async updateInventory(id: string, updates: InventoryUpdate): Promise<InventoryRow | null> {
    const { data, error } = await typedSupabase
      .from('inventory')
      .update(updates)
      .eq('id', id)
      .select()
      .single()
    
    if (error) {
      console.error('Error updating inventory:', error)
      return null
    }
    
    return data
  }

  async deleteInventory(id: string): Promise<boolean> {
    const { error } = await typedSupabase
      .from('inventory')
      .delete()
      .eq('id', id)
    
    if (error) {
      console.error('Error deleting inventory:', error)
      return false
    }
    
    return true
  }

  // Order operations
  async getOrders(): Promise<OrderRow[]> {
    const { data, error } = await typedSupabase
      .from('orders')
      .select('*')
      .order('created_at', { ascending: false })
    
    if (error) {
      console.error('Error fetching orders:', error)
      return []
    }
    
    return data || []
  }

  async getOrderById(id: string): Promise<OrderRow | null> {
    const { data, error } = await typedSupabase
      .from('orders')
      .select('*')
      .eq('id', id)
      .single()
    
    if (error) {
      console.error('Error fetching order by ID:', error)
      return null
    }
    
    return data
  }

  async createOrder(order: OrderInsert): Promise<OrderRow | null> {
    const { data, error } = await typedSupabase
      .from('orders')
      .insert(order)
      .select()
      .single()
    
    if (error) {
      console.error('Error creating order:', error)
      return null
    }
    
    return data
  }

  async updateOrder(id: string, updates: OrderUpdate): Promise<OrderRow | null> {
    const { data, error } = await typedSupabase
      .from('orders')
      .update(updates)
      .eq('id', id)
      .select()
      .single()
    
    if (error) {
      console.error('Error updating order:', error)
      return null
    }
    
    return data
  }

  async deleteOrder(id: string): Promise<boolean> {
    const { error } = await typedSupabase
      .from('orders')
      .delete()
      .eq('id', id)
    
    if (error) {
      console.error('Error deleting order:', error)
      return false
    }
    
    return true
  }

  // Summary operations
  async getFleetSummary() {
    const { count, error } = await typedSupabase
      .from('fleet')
      .select('*', { count: 'exact', head: true })
    
    if (error) {
      console.error('Error getting fleet summary:', error)
      return { total_count: 0, recent_records: [] }
    }
    
    const { data: recent } = await typedSupabase
      .from('fleet')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10)
    
    return {
      total_count: count || 0,
      recent_records: recent || []
    }
  }

  async getMerchantsSummary() {
    const { count, error } = await typedSupabase
      .from('merchants')
      .select('*', { count: 'exact', head: true })
    
    if (error) {
      console.error('Error getting merchants summary:', error)
      return { total_count: 0, recent_records: [] }
    }
    
    const { data: recent } = await typedSupabase
      .from('merchants')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10)
    
    return {
      total_count: count || 0,
      recent_records: recent || []
    }
  }

  async getInventorySummary() {
    const { count, error } = await typedSupabase
      .from('inventory')
      .select('*', { count: 'exact', head: true })
    
    if (error) {
      console.error('Error getting inventory summary:', error)
      return { total_count: 0, recent_records: [] }
    }
    
    const { data: recent } = await typedSupabase
      .from('inventory')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10)
    
    return {
      total_count: count || 0,
      recent_records: recent || []
    }
  }

  // System health operations (placeholder)
  async getSystemHealth(): Promise<any> {
    // For now, return mock health data
    return {
      status: 'healthy',
      services: {
        database: 'healthy',
        redis: 'healthy',
        agent_manager: 'healthy',
        simulation_engine: 'healthy'
      },
      timestamp: new Date().toISOString()
    }
  }

  // Agentic Actions and Decisions
  async getPendingActions(): Promise<any[]> {
    try {
      const { data, error } = await typedSupabase
        .from('agentic_actions')
        .select('*')
        .eq('status', 'pending')
        .order('created_at', { ascending: false })
      
      if (error) {
        console.error('Error fetching pending actions:', error)
        return []
      }
      
      return data || []
    } catch (err) {
      console.error('Exception fetching pending actions:', err)
      return []
    }
  }

  async getAgenticStatus(): Promise<any> {
    try {
      const { data, error } = await typedSupabase
        .from('simulation_status')
        .select('*')
        .single()
      
      if (error) {
        console.error('Error fetching agentic status:', error)
        return {
          is_running: false,
          tick_count: 0,
          current_time: new Date().toISOString(),
          agents_active: 0,
          system_health: 'healthy'
        }
      }
      
      return data || {
        is_running: false,
        tick_count: 0,
        current_time: new Date().toISOString(),
        agents_active: 0,
        system_health: 'healthy'
      }
    } catch (err) {
      console.error('Exception fetching agentic status:', err)
      return {
        is_running: false,
        tick_count: 0,
        current_time: new Date().toISOString(),
        agents_active: 0,
        system_health: 'healthy'
      }
    }
  }

  async getAgentPlan(): Promise<any> {
    try {
      const { data, error } = await typedSupabase
        .from('agent_plans')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(1)
        .single()
      
      if (error) {
        console.error('Error fetching agent plan:', error)
        return null
      }
      
      return data
    } catch (err) {
      console.error('Exception fetching agent plan:', err)
      return null
    }
  }

  async getActionHistory(): Promise<any[]> {
    try {
      const { data, error } = await typedSupabase
        .from('agentic_actions')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50)
      
      if (error) {
        console.error('Error fetching action history:', error)
        return []
      }
      
      return data || []
    } catch (err) {
      console.error('Exception fetching action history:', err)
      return []
    }
  }

  async approveAction(actionId: string): Promise<boolean> {
    try {
      const { error } = await typedSupabase
        .from('agentic_actions')
        .update({ 
          status: 'approved',
          approved_at: new Date().toISOString()
        })
        .eq('id', actionId)
      
      if (error) {
        console.error('Error approving action:', error)
        return false
      }
      
      return true
    } catch (err) {
      console.error('Exception approving action:', err)
      return false
    }
  }

  async denyAction(actionId: string): Promise<boolean> {
    try {
      const { error } = await typedSupabase
        .from('agentic_actions')
        .update({ 
          status: 'denied',
          denied_at: new Date().toISOString()
        })
        .eq('id', actionId)
      
      if (error) {
        console.error('Error denying action:', error)
        return false
      }
      
      return true
    } catch (err) {
      console.error('Exception denying action:', err)
      return false
    }
  }

  // Agent Decisions
  async getPendingAgentDecisions(): Promise<any[]> {
    try {
      const { data, error } = await typedSupabase
        .from('agent_decisions')
        .select('*')
        .eq('status', 'pending')
        .order('created_at', { ascending: false })
      
      if (error) {
        console.error('Error fetching pending agent decisions:', error)
        return []
      }
      
      return data || []
    } catch (err) {
      console.error('Exception fetching pending agent decisions:', err)
      return []
    }
  }

  async getAgentDecisionHistory(): Promise<any[]> {
    try {
      const { data, error } = await typedSupabase
        .from('agent_decisions')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50)
      
      if (error) {
        console.error('Error fetching agent decision history:', error)
        return []
      }
      
      return data || []
    } catch (err) {
      console.error('Exception fetching agent decision history:', err)
      return []
    }
  }

  async approveAgentDecision(decisionId: string): Promise<boolean> {
    try {
      const { error } = await typedSupabase
        .from('agent_decisions')
        .update({ 
          status: 'approved',
          approved_at: new Date().toISOString()
        })
        .eq('id', decisionId)
      
      if (error) {
        console.error('Error approving agent decision:', error)
        return false
      }
      
      return true
    } catch (err) {
      console.error('Exception approving agent decision:', err)
      return false
    }
  }

  async denyAgentDecision(decisionId: string): Promise<boolean> {
    try {
      const { error } = await typedSupabase
        .from('agent_decisions')
        .update({ 
          status: 'denied',
          denied_at: new Date().toISOString()
        })
        .eq('id', decisionId)
      
      if (error) {
        console.error('Error denying agent decision:', error)
        return false
      }
      
      return true
    } catch (err) {
      console.error('Exception denying agent decision:', err)
      return false
    }
  }

  // Enhanced Agent operations
  async getAgents(): Promise<any[]> {
    try {
      const { data, error } = await typedSupabase
        .from('agents')
        .select('*')
        .order('created_at', { ascending: false })
      
      if (error) {
        console.error('Error fetching agents:', error)
        return []
      }
      
      return data || []
    } catch (err) {
      console.error('Exception fetching agents:', err)
      return []
    }
  }

  async getAgentById(id: string): Promise<any | null> {
    try {
      const { data, error } = await typedSupabase
        .from('agents')
        .select('*')
        .eq('id', id)
        .single()
      
      if (error) {
        console.error('Error fetching agent by ID:', error)
        return null
      }
      
      return data
    } catch (err) {
      console.error('Exception fetching agent by ID:', err)
      return null
    }
  }

  async updateAgentStatus(id: string, status: string): Promise<boolean> {
    try {
      const { error } = await typedSupabase
        .from('agents')
        .update({ 
          status,
          updated_at: new Date().toISOString()
        })
        .eq('id', id)
      
      if (error) {
        console.error('Error updating agent status:', error)
        return false
      }
      
      return true
    } catch (err) {
      console.error('Exception updating agent status:', err)
      return false
    }
  }

  // Route operations
  async getRoutes(): Promise<Database['public']['Tables']['routes']['Row'][]> {
    try {
      const { data, error } = await typedSupabase
        .from('routes')
        .select('*')
        .order('created_at', { ascending: false })
      if (error) {
        console.error('Error fetching routes:', error)
        return []
      }
      return data || []
    } catch (err) {
      console.error('Exception fetching routes:', err)
      return []
    }
  }

  // Fetch agent logs from Supabase
  async getAgentLogs(agentId = null, limit = 50) {
    let query = typedSupabase
      .from('agent_logs')
      .select('*')
      .order('timestamp', { ascending: false })
      .limit(limit);
    if (agentId) {
      query = query.eq('agent_id', agentId);
    }
    const { data, error } = await query;
    if (error) {
      console.error('Error fetching agent logs:', error);
      return [];
    }
    return data;
  }
}

// Export singleton instance
export const supabaseService = new SupabaseService() 