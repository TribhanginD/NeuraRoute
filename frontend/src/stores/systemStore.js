import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

const useSystemStore = create(
  devtools(
    (set, get) => ({
      // System status
      systemStatus: {
        status: 'unknown',
        services: {
          database: 'unknown',
          redis: 'unknown',
          agent_manager: 'unknown',
          simulation_engine: 'unknown',
        },
        timestamp: null,
      },
      
      // Agent status
      agentStatus: {
        total_agents: 0,
        active_agents: 0,
        agents_by_type: {},
        agents_by_status: {},
      },
      
      // Simulation status
      simulationStatus: {
        is_running: false,
        current_tick: 0,
        total_ticks: 0,
        speed_multiplier: 1.0,
        start_time: null,
        last_tick_time: null,
        uptime_seconds: 0,
        status: 'stopped',
      },
      
      // Fleet status
      fleetStatus: {
        total_vehicles: 0,
        available_vehicles: 0,
        busy_vehicles: 0,
        maintenance_vehicles: 0,
        total_routes: 0,
        active_routes: 0,
        total_orders: 0,
        pending_orders: 0,
        delivered_orders: 0,
      },
      
      // Inventory status
      inventoryStatus: {
        total_skus: 0,
        total_items: 0,
        low_stock_items: 0,
        out_of_stock_items: 0,
        expired_items: 0,
        total_value: 0,
        items_by_status: {},
        items_by_category: {},
      },
      
      // UI state
      ui: {
        sidebarOpen: false,
        currentPage: 'dashboard',
        theme: 'light',
        notifications: [],
      },
      
      // Actions
      setSystemStatus: (status) => set({ systemStatus: status }),
      
      setAgentStatus: (status) => set({ agentStatus: status }),
      
      setSimulationStatus: (status) => set({ simulationStatus: status }),
      
      setFleetStatus: (status) => set({ fleetStatus: status }),
      
      setInventoryStatus: (status) => set({ inventoryStatus: status }),
      
      setSidebarOpen: (open) => set((state) => ({
        ui: { ...state.ui, sidebarOpen: open }
      })),
      
      setCurrentPage: (page) => set((state) => ({
        ui: { ...state.ui, currentPage: page }
      })),
      
      setTheme: (theme) => set((state) => ({
        ui: { ...state.ui, theme }
      })),
      
      addNotification: (notification) => set((state) => ({
        ui: {
          ...state.ui,
          notifications: [...state.ui.notifications, { ...notification, id: Date.now() }]
        }
      })),
      
      removeNotification: (id) => set((state) => ({
        ui: {
          ...state.ui,
          notifications: state.ui.notifications.filter(n => n.id !== id)
        }
      })),
      
      clearNotifications: () => set((state) => ({
        ui: { ...state.ui, notifications: [] }
      })),
      
      // Computed values
      getSystemHealth: () => {
        const { systemStatus } = get();
        return systemStatus.status === 'healthy';
      },
      
      getActiveAgentsCount: () => {
        const { agentStatus } = get();
        return agentStatus.active_agents;
      },
      
      getSimulationProgress: () => {
        const { simulationStatus } = get();
        if (simulationStatus.total_ticks === 0) return 0;
        return (simulationStatus.current_tick / simulationStatus.total_ticks) * 100;
      },
      
      getFleetUtilization: () => {
        const { fleetStatus } = get();
        if (fleetStatus.total_vehicles === 0) return 0;
        return ((fleetStatus.total_vehicles - fleetStatus.available_vehicles) / fleetStatus.total_vehicles) * 100;
      },
      
      getInventoryHealth: () => {
        const { inventoryStatus } = get();
        if (inventoryStatus.total_items === 0) return 100;
        const healthyItems = inventoryStatus.total_items - inventoryStatus.out_of_stock_items - inventoryStatus.expired_items;
        return (healthyItems / inventoryStatus.total_items) * 100;
      },
    }),
    {
      name: 'system-store',
    }
  )
);

export { useSystemStore }; 