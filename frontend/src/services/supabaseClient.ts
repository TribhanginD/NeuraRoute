import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Database types (you can generate these from your Supabase dashboard)
export interface Database {
  public: {
    Tables: {
      fleet: {
        Row: {
          id: string
          vehicle_id: string
          vehicle_type: string
          capacity: number
          current_location: string
          status: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          vehicle_id: string
          vehicle_type: string
          capacity: number
          current_location: string
          status: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          vehicle_id?: string
          vehicle_type?: string
          capacity?: number
          current_location?: string
          status?: string
          created_at?: string
          updated_at?: string
        }
      }
      merchants: {
        Row: {
          id: string
          name: string
          location: string
          contact_info: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          name: string
          location: string
          contact_info: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          name?: string
          location?: string
          contact_info?: string
          created_at?: string
          updated_at?: string
        }
      }
      inventory: {
        Row: {
          id: string
          item_name: string
          quantity: number
          location: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          item_name: string
          quantity: number
          location: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          item_name?: string
          quantity?: number
          location?: string
          created_at?: string
          updated_at?: string
        }
      }
      orders: {
        Row: {
          id: string
          merchant_id: string
          items: string
          status: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          merchant_id: string
          items: string
          status: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          merchant_id?: string
          items?: string
          status?: string
          created_at?: string
          updated_at?: string
        }
      },
      routes: {
        Row: {
          id: string
          vehicle_id: string
          route_points: any // JSON array of coordinates or steps
          status: string
          created_at: string
          updated_at: string
        }
        Insert: {
          id?: string
          vehicle_id: string
          route_points: any
          status: string
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          vehicle_id?: string
          route_points?: any
          status?: string
          created_at?: string
          updated_at?: string
        }
      }
    }
  }
}

// Typed Supabase client
export const typedSupabase = createClient<Database>(supabaseUrl, supabaseAnonKey) 