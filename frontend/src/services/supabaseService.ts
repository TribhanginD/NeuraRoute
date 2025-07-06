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

  // Agent operations (placeholder - you may need to create an agents table)
  async getAgents(): Promise<any[]> {
    // For now, return empty array since agents table may not exist
    // You can create an agents table in Supabase if needed
    console.log('Agents table not implemented yet')
    return []
  }

  // Route operations (placeholder - you may need to create a routes table)
  async getRoutes(): Promise<any[]> {
    // For now, return empty array since routes table may not exist
    // You can create a routes table in Supabase if needed
    console.log('Routes table not implemented yet')
    return []
  }

  // Weather operations (placeholder)
  async getWeather(): Promise<any> {
    // For now, return mock weather data
    return {
      condition: 'sunny',
      temperature: 25,
      humidity: 60,
      wind_speed: 10
    }
  }

  // System health operations (placeholder)
  async getSystemHealth(): Promise<any> {
    // For now, return mock health data
    return {
      database: 'healthy',
      redis: 'healthy',
      agents: 'healthy',
      simulation: 'healthy'
    }
  }
}

// Export singleton instance
export const supabaseService = new SupabaseService() 