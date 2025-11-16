-- Agentic System Tables for NeuraRoute

-- Agent Logs Table
CREATE TABLE IF NOT EXISTS agent_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    agent_type VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    details JSONB,
    payload JSONB,
    status VARCHAR(50) DEFAULT 'completed',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Actions Table
CREATE TABLE IF NOT EXISTS agent_actions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(255) NOT NULL,
    target_table VARCHAR(255),
    item_id VARCHAR(255),
    quantity INTEGER,
    priority VARCHAR(50) DEFAULT 'medium',
    reasoning TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_at TIMESTAMP WITH TIME ZONE,
    route_data JSONB,
    new_price DECIMAL(10,2),
    strategy VARCHAR(255),
    duration VARCHAR(255),
    payload JSONB
);

-- Agent Decisions Table
CREATE TABLE IF NOT EXISTS agent_decisions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    decision_type VARCHAR(255) NOT NULL,
    agent_id VARCHAR(255) NOT NULL,
    context JSONB,
    decision JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    reasoning TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_at TIMESTAMP WITH TIME ZONE
);

-- Simulation status table keeps the dashboard in sync
CREATE TABLE IF NOT EXISTS simulation_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    is_running BOOLEAN DEFAULT FALSE,
    current_tick INTEGER DEFAULT 0,
    total_ticks INTEGER DEFAULT 96,
    tick_interval_seconds INTEGER DEFAULT 900,
    current_time TIMESTAMP WITH TIME ZONE,
    last_tick_time TIMESTAMP WITH TIME ZONE,
    started_at TIMESTAMP WITH TIME ZONE,
    estimated_completion TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent_id ON agent_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp ON agent_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_agent_logs_status ON agent_logs(status);

CREATE INDEX IF NOT EXISTS idx_agent_actions_agent_id ON agent_actions(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_actions_status ON agent_actions(status);
CREATE INDEX IF NOT EXISTS idx_agent_actions_created_at ON agent_actions(created_at);

CREATE INDEX IF NOT EXISTS idx_agent_decisions_decision_type ON agent_decisions(decision_type);
CREATE INDEX IF NOT EXISTS idx_agent_decisions_status ON agent_decisions(status);
CREATE INDEX IF NOT EXISTS idx_agent_decisions_created_at ON agent_decisions(created_at);

CREATE INDEX IF NOT EXISTS idx_simulation_status_updated_at ON simulation_status(updated_at);

-- Insert some sample data for testing
INSERT INTO agent_logs (agent_id, agent_type, action, details, status) VALUES
('inventory_agent_001', 'inventory_management', 'system_started', '{"message": "Inventory agent initialized"}', 'completed'),
('routing_agent_001', 'route_optimization', 'system_started', '{"message": "Routing agent initialized"}', 'completed'),
('pricing_agent_001', 'pricing_optimization', 'system_started', '{"message": "Pricing agent initialized"}', 'completed');

-- Insert sample agent actions
INSERT INTO agent_actions (agent_id, action_type, target_table, item_id, quantity, priority, reasoning, status) VALUES
('inventory_agent_001', 'reorder', 'inventory', 'item_001', 50, 'high', 'Low stock detected', 'pending'),
('pricing_agent_001', 'dynamic_pricing', 'inventory', 'item_002', NULL, 'medium', 'High demand detected', 'pending');

-- Insert sample agent decisions
INSERT INTO agent_decisions (decision_type, agent_id, context, decision, status, reasoning) VALUES
('inventory_optimization', 'inventory_agent_001', '{"current_stock": 10, "demand": "high"}', '{"action": "reorder", "quantity": 100}', 'pending', 'Stock levels below threshold'),
('route_optimization', 'routing_agent_001', '{"orders": 5, "vehicles": 3}', '{"route": "optimized", "savings": "15%"}', 'pending', 'Route optimization completed'); 
