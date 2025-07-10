-- Agentic System Tables for NeuraRoute

-- Agent Logs Table
CREATE TABLE IF NOT EXISTS agent_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,
    agent_type VARCHAR(255) NOT NULL,
    action VARCHAR(255) NOT NULL,
    details JSONB,
    status VARCHAR(50) DEFAULT 'completed',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agentic Actions Table
CREATE TABLE IF NOT EXISTS agentic_actions (
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
    duration VARCHAR(255)
);

-- Agentic Decisions Table
CREATE TABLE IF NOT EXISTS agentic_decisions (
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_agent_logs_agent_id ON agent_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_logs_timestamp ON agent_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_agent_logs_status ON agent_logs(status);

CREATE INDEX IF NOT EXISTS idx_agentic_actions_agent_id ON agentic_actions(agent_id);
CREATE INDEX IF NOT EXISTS idx_agentic_actions_status ON agentic_actions(status);
CREATE INDEX IF NOT EXISTS idx_agentic_actions_created_at ON agentic_actions(created_at);

CREATE INDEX IF NOT EXISTS idx_agentic_decisions_decision_type ON agentic_decisions(decision_type);
CREATE INDEX IF NOT EXISTS idx_agentic_decisions_status ON agentic_decisions(status);
CREATE INDEX IF NOT EXISTS idx_agentic_decisions_created_at ON agentic_decisions(created_at);

-- Insert some sample data for testing
INSERT INTO agent_logs (agent_id, agent_type, action, details, status) VALUES
('inventory_agent_001', 'inventory_management', 'system_started', '{"message": "Inventory agent initialized"}', 'completed'),
('routing_agent_001', 'route_optimization', 'system_started', '{"message": "Routing agent initialized"}', 'completed'),
('pricing_agent_001', 'pricing_optimization', 'system_started', '{"message": "Pricing agent initialized"}', 'completed');

-- Insert sample agentic actions
INSERT INTO agentic_actions (agent_id, action_type, target_table, item_id, quantity, priority, reasoning, status) VALUES
('inventory_agent_001', 'reorder', 'inventory', 'item_001', 50, 'high', 'Low stock detected', 'pending'),
('pricing_agent_001', 'dynamic_pricing', 'inventory', 'item_002', NULL, 'medium', 'High demand detected', 'pending');

-- Insert sample agentic decisions
INSERT INTO agentic_decisions (decision_type, agent_id, context, decision, status, reasoning) VALUES
('inventory_optimization', 'inventory_agent_001', '{"current_stock": 10, "demand": "high"}', '{"action": "reorder", "quantity": 100}', 'pending', 'Stock levels below threshold'),
('route_optimization', 'routing_agent_001', '{"orders": 5, "vehicles": 3}', '{"route": "optimized", "savings": "15%"}', 'pending', 'Route optimization completed'); 