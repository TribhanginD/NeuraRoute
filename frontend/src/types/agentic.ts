/**
 * TypeScript interfaces for the Agentic AI system
 */

export enum ActionType {
  PLACE_ORDER = "place_order",
  REROUTE_DRIVER = "reroute_driver",
  UPDATE_INVENTORY = "update_inventory",
  ADJUST_PRICING = "adjust_pricing",
  DISPATCH_FLEET = "dispatch_fleet",
  FORECAST_DEMAND = "forecast_demand",
  ANALYZE_PERFORMANCE = "analyze_performance"
}

export enum ApprovalStatus {
  PENDING = "pending",
  APPROVED = "approved",
  DENIED = "denied",
  AUTO_APPROVED = "auto_approved"
}

export enum SimulationEventType {
  INVENTORY_UPDATE = "inventory_update",
  DEMAND_SPIKE = "demand_spike",
  DELIVERY_DELAY = "delivery_delay",
  WEATHER_CHANGE = "weather_change",
  EVENT_ANNOUNCEMENT = "event_announcement",
  TRAFFIC_UPDATE = "traffic_update"
}

// Base interfaces
export interface BaseAction {
  action_id: string;
  action_type: ActionType;
  parameters: Record<string, any>;
  reasoning: string;
  confidence: number;
  estimated_impact: Record<string, any>;
  approval_required: boolean;
  approval_status: ApprovalStatus;
  timestamp: string;
}

export interface PendingAction extends BaseAction {
  approval_status: ApprovalStatus.PENDING;
}

export interface ApprovedAction extends BaseAction {
  approval_status: ApprovalStatus.APPROVED | ApprovalStatus.AUTO_APPROVED;
  executed: boolean;
  execution_result?: Record<string, any>;
  error_message?: string;
}

export interface DeniedAction extends BaseAction {
  approval_status: ApprovalStatus.DENIED;
}

export type AgenticAction = PendingAction | ApprovedAction | DeniedAction;

// Context interfaces
export interface InventoryItem {
  sku_name: string;
  quantity: number;
  reorder_threshold: number;
}

export interface DemandForecast {
  sku_name: string;
  predicted_demand: number;
}

export interface DeliveryStatus {
  driver_id: string;
  status: string;
  estimated_arrival: string;
}

export interface MarketConditions {
  weather: string;
  events: string;
  traffic: string;
}

export interface SituationContext {
  inventory: InventoryItem[];
  demand_forecast: DemandForecast[];
  deliveries: DeliveryStatus[];
  market_conditions: MarketConditions;
}

// API Response interfaces
export interface ProcessSituationResponse {
  success: boolean;
  reasoning: string;
  actions: AgenticAction[];
  confidence: number;
  timestamp: string;
  pending_approvals: number;
}

export interface PendingActionsResponse {
  actions: PendingAction[];
  count: number;
}

export interface ActionHistoryResponse {
  history: {
    pending: PendingAction[];
    approved: ApprovedAction[];
    denied: DeniedAction[];
  };
  summary: {
    pending: number;
    approved: number;
    denied: number;
  };
}

export interface AgenticSystemStatus {
  status: string;
  simulation_mode: boolean;
  tools_available: number;
  pending_actions: number;
  approved_actions: number;
  denied_actions: number;
  memory_size: number;
}

export interface ToolInfo {
  name: string;
  description: string;
  approval_threshold: number;
}

export interface AvailableToolsResponse {
  tools: ToolInfo[];
  count: number;
}

// Simulation interfaces
export interface SimulationScenario {
  name: string;
  description: string;
  duration_hours: number;
  events_count: number;
}

export interface SimulationScenariosResponse {
  scenarios: SimulationScenario[];
  count: number;
}

export interface SimulationStats {
  scenario: string | null;
  is_running: boolean;
  current_time: string | null;
  events_processed: number;
  actions_generated: number;
  simulation_log_entries: number;
}

export interface SimulationStatusResponse {
  simulation: SimulationStats;
  available_scenarios: number;
}

export interface SimulationLogEntry {
  timestamp: string;
  events_triggered: string[];
  context_updates: Record<string, any>;
  agent_response?: ProcessSituationResponse;
}

export interface SimulationLogResponse {
  log_entries: SimulationLogEntry[];
  count: number;
}

export interface SimulationStepResult {
  step_completed: boolean;
  simulation_ended: boolean;
  current_time?: string;
  events_triggered?: number;
  actions_generated?: number;
  final_stats?: SimulationStats;
}

export interface SimulationStartResult {
  success: boolean;
  scenario: string;
  start_time: string;
  duration_hours: number;
  events_count: number;
  initial_actions: number;
}

export interface SimulationStopResult {
  success: boolean;
  message: string;
  stats: SimulationStats;
}

export interface AutoRunSimulationResult {
  success: boolean;
  start_result: SimulationStartResult;
  steps: SimulationStepResult[];
  final_stats: SimulationStats;
  total_steps: number;
}

// Tool execution interfaces
export interface ToolExecutionRequest {
  tool_name: string;
  parameters: Record<string, any>;
}

export interface ToolExecutionResponse {
  success: boolean;
  tool_name: string;
  parameters: Record<string, any>;
  result: string;
}

// Action approval interfaces
export interface ActionApprovalRequest {
  approved_by: string;
  notes?: string;
}

export interface ActionDenialRequest {
  denied_by: string;
  reason: string;
}

export interface ActionApprovalResponse {
  success: boolean;
  action_id: string;
  status: string;
  execution_result?: Record<string, any>;
}

export interface ActionDenialResponse {
  success: boolean;
  action_id: string;
  status: string;
}

// Demo interfaces
export interface MarketDayDemoResponse {
  success: boolean;
  demo_data: SituationContext;
  agent_response: ProcessSituationResponse;
  message: string;
}

// Error interfaces
export interface AgenticError {
  detail: string;
  status_code: number;
}

// WebSocket interfaces for real-time updates
export interface AgenticWebSocketMessage {
  type: 'action_created' | 'action_approved' | 'action_denied' | 'simulation_update' | 'status_update' | 'situation_processed' | 'simulation_mode_changed';
  data: any;
  timestamp: string;
}

export interface ActionCreatedMessage {
  type: 'action_created';
  data: PendingAction;
  timestamp: string;
}

export interface ActionApprovedMessage {
  type: 'action_approved';
  data: ApprovedAction;
  timestamp: string;
}

export interface ActionDeniedMessage {
  type: 'action_denied';
  data: DeniedAction;
  timestamp: string;
}

export interface SimulationUpdateMessage {
  type: 'simulation_update';
  data: SimulationStepResult;
  timestamp: string;
}

export interface StatusUpdateMessage {
  type: 'status_update';
  data: AgenticSystemStatus;
  timestamp: string;
}

export interface SituationProcessedMessage {
  type: 'situation_processed';
  data: {
    reasoning: string;
    actions: AgenticAction[];
    confidence: number;
    timestamp: string;
    pending_approvals: number;
  };
  timestamp: string;
}

export interface SimulationModeChangedMessage {
  type: 'simulation_mode_changed';
  data: {
    simulation_mode: boolean;
    message: string;
  };
  timestamp: string;
}

// Frontend state interfaces
export interface AgenticState {
  systemStatus: AgenticSystemStatus | null;
  pendingActions: PendingAction[];
  actionHistory: ActionHistoryResponse | null;
  availableTools: ToolInfo[];
  simulationStatus: SimulationStats | null;
  simulationLog: SimulationLogEntry[];
  availableScenarios: SimulationScenario[];
  isLoading: boolean;
  error: string | null;
}

export interface AgenticContextType {
  state: AgenticState;
  dispatch: React.Dispatch<AgenticAction>;
  processSituation: (context: SituationContext) => Promise<ProcessSituationResponse>;
  approveAction: (actionId: string, request: ActionApprovalRequest) => Promise<ActionApprovalResponse>;
  denyAction: (actionId: string, request: ActionDenialRequest) => Promise<ActionDenialResponse>;
  startSimulation: (scenarioName: string, speed?: number) => Promise<SimulationStartResult>;
  runSimulationStep: () => Promise<SimulationStepResult>;
  stopSimulation: () => Promise<SimulationStopResult>;
  autoRunSimulation: (scenarioName: string, speed?: number) => Promise<AutoRunSimulationResult>;
  executeTool: (request: ToolExecutionRequest) => Promise<ToolExecutionResponse>;
  resetSystem: () => Promise<void>;
}

// Component prop interfaces
export interface ActionCardProps {
  action: AgenticAction;
  onApprove: (actionId: string) => void;
  onDeny: (actionId: string) => void;
  onViewDetails: (action: AgenticAction) => void;
}

export interface SimulationControlProps {
  scenarios: SimulationScenario[];
  currentStatus: SimulationStats | null;
  onStart: (scenarioName: string, speed?: number) => void;
  onStep: () => void;
  onStop: () => void;
  onAutoRun: (scenarioName: string, speed?: number) => void;
}

export interface ActionHistoryProps {
  history: ActionHistoryResponse | null;
  onViewAction: (action: AgenticAction) => void;
  onRefresh: () => void;
}

export interface SystemStatusProps {
  status: AgenticSystemStatus | null;
  onRefresh: () => void;
}

export interface SimulationTimelineProps {
  logEntries: SimulationLogEntry[];
  onSelectEntry: (entry: SimulationLogEntry) => void;
}

export interface ToolPanelProps {
  tools: ToolInfo[];
  onExecuteTool: (toolName: string, parameters: Record<string, any>) => void;
}

// Form interfaces
export interface SituationContextForm {
  inventory: InventoryItem[];
  demand_forecast: DemandForecast[];
  deliveries: DeliveryStatus[];
  market_conditions: MarketConditions;
}

export interface ActionApprovalForm {
  approved_by: string;
  notes: string;
}

export interface ActionDenialForm {
  denied_by: string;
  reason: string;
}

export interface SimulationConfigForm {
  scenario_name: string;
  speed: number;
}

// Utility types
export type ActionTypeLabel = Record<ActionType, string>;
export type ApprovalStatusLabel = Record<ApprovalStatus, string>;
export type SimulationEventTypeLabel = Record<SimulationEventType, string>;

// Constants
export const ACTION_TYPE_LABELS: ActionTypeLabel = {
  [ActionType.PLACE_ORDER]: "Place Order",
  [ActionType.REROUTE_DRIVER]: "Reroute Driver",
  [ActionType.UPDATE_INVENTORY]: "Update Inventory",
  [ActionType.ADJUST_PRICING]: "Adjust Pricing",
  [ActionType.DISPATCH_FLEET]: "Dispatch Fleet",
  [ActionType.FORECAST_DEMAND]: "Forecast Demand",
  [ActionType.ANALYZE_PERFORMANCE]: "Analyze Performance"
};

export const APPROVAL_STATUS_LABELS: ApprovalStatusLabel = {
  [ApprovalStatus.PENDING]: "Pending",
  [ApprovalStatus.APPROVED]: "Approved",
  [ApprovalStatus.DENIED]: "Denied",
  [ApprovalStatus.AUTO_APPROVED]: "Auto-Approved"
};

export const SIMULATION_EVENT_TYPE_LABELS: SimulationEventTypeLabel = {
  [SimulationEventType.INVENTORY_UPDATE]: "Inventory Update",
  [SimulationEventType.DEMAND_SPIKE]: "Demand Spike",
  [SimulationEventType.DELIVERY_DELAY]: "Delivery Delay",
  [SimulationEventType.WEATHER_CHANGE]: "Weather Change",
  [SimulationEventType.EVENT_ANNOUNCEMENT]: "Event Announcement",
  [SimulationEventType.TRAFFIC_UPDATE]: "Traffic Update"
};

// Helper functions
export const isPendingAction = (action: AgenticAction): action is PendingAction => {
  return action.approval_status === ApprovalStatus.PENDING;
};

export const isApprovedAction = (action: AgenticAction): action is ApprovedAction => {
  return action.approval_status === ApprovalStatus.APPROVED || 
         action.approval_status === ApprovalStatus.AUTO_APPROVED;
};

export const isDeniedAction = (action: AgenticAction): action is DeniedAction => {
  return action.approval_status === ApprovalStatus.DENIED;
};

export const formatTimestamp = (timestamp: string): string => {
  return new Date(timestamp).toLocaleString();
};

export const getActionTypeLabel = (actionType: ActionType): string => {
  return ACTION_TYPE_LABELS[actionType];
};

export const getApprovalStatusLabel = (status: ApprovalStatus): string => {
  return APPROVAL_STATUS_LABELS[status];
};

export const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.8) return 'text-green-600';
  if (confidence >= 0.6) return 'text-yellow-600';
  return 'text-red-600';
};

export const getApprovalStatusColor = (status: ApprovalStatus): string => {
  switch (status) {
    case ApprovalStatus.APPROVED:
    case ApprovalStatus.AUTO_APPROVED:
      return 'text-green-600';
    case ApprovalStatus.DENIED:
      return 'text-red-600';
    case ApprovalStatus.PENDING:
      return 'text-yellow-600';
    default:
      return 'text-gray-600';
  }
};

// Agent Plan interfaces
export interface AgentPlan {
  current_reasoning: string;
  memory_size: number;
  recent_actions: {
    pending: number;
    approved: number;
    denied: number;
  };
  tools_available: number;
  simulation_mode: boolean;
}

export interface AgentPlanResponse {
  current_reasoning: string;
  memory_size: number;
  recent_actions: {
    pending: number;
    approved: number;
    denied: number;
  };
  tools_available: number;
  simulation_mode: boolean;
}

// WebSocket subscription types
export interface WebSocketSubscription {
  type: 'subscribe';
  events: string[];
}

export interface WebSocketSubscriptionResponse {
  type: 'subscription_confirmed';
  events: string[];
  timestamp: string;
} 