-- NeuraRoute Database Initialization Script
-- This script creates all necessary tables, enums, indexes, and sample data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enums
CREATE TYPE agent_status AS ENUM ('idle', 'running', 'error', 'stopped');
CREATE TYPE agent_type AS ENUM ('restock', 'route', 'pricing', 'dispatch', 'forecasting');
CREATE TYPE simulation_status AS ENUM ('stopped', 'running', 'paused', 'error');
CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'in_transit', 'delivered', 'cancelled');
CREATE TYPE vehicle_status AS ENUM ('available', 'in_use', 'maintenance', 'offline');
CREATE TYPE inventory_status AS ENUM ('in_stock', 'low_stock', 'out_of_stock', 'reserved');
CREATE TYPE weather_condition AS ENUM ('sunny', 'cloudy', 'rainy', 'snowy', 'stormy');
CREATE TYPE event_type AS ENUM ('weather', 'traffic', 'demand_spike', 'supply_shortage', 'system_alert');

-- Create tables

-- Agents table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    agent_type agent_type NOT NULL,
    status agent_status DEFAULT 'idle',
    config JSONB DEFAULT '{}',
    memory JSONB DEFAULT '{}',
    last_heartbeat TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Simulation state table
CREATE TABLE simulation_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    status simulation_status DEFAULT 'stopped',
    current_tick INTEGER DEFAULT 0,
    start_time TIMESTAMP WITH TIME ZONE,
    last_tick_time TIMESTAMP WITH TIME ZONE,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inventory table
CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id VARCHAR(100) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    quantity INTEGER DEFAULT 0,
    min_quantity INTEGER DEFAULT 0,
    max_quantity INTEGER DEFAULT 1000,
    status inventory_status DEFAULT 'in_stock',
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fleet table
CREATE TABLE fleet (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id VARCHAR(100) UNIQUE NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL,
    current_location_lat DECIMAL(10, 8),
    current_location_lng DECIMAL(11, 8),
    status vehicle_status DEFAULT 'available',
    fuel_level DECIMAL(5, 2) DEFAULT 100.0,
    last_maintenance TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Routes table
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID REFERENCES fleet(id),
    route_data JSONB NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'planned',
    optimization_score DECIMAL(5, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id VARCHAR(100) NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    status order_status DEFAULT 'pending',
    priority INTEGER DEFAULT 1,
    pickup_location_lat DECIMAL(10, 8),
    pickup_location_lng DECIMAL(11, 8),
    delivery_location_lat DECIMAL(10, 8),
    delivery_location_lng DECIMAL(11, 8),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Demand forecasts table
CREATE TABLE demand_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id VARCHAR(100) NOT NULL,
    forecast_data JSONB NOT NULL,
    confidence_score DECIMAL(5, 4),
    forecast_horizon_hours INTEGER DEFAULT 24,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pricing table
CREATE TABLE pricing (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id VARCHAR(100) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    current_price DECIMAL(10, 2) NOT NULL,
    demand_factor DECIMAL(5, 4) DEFAULT 1.0,
    supply_factor DECIMAL(5, 4) DEFAULT 1.0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Events table
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type event_type NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    description TEXT,
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    impact_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Weather data table
CREATE TABLE weather_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_lat DECIMAL(10, 8) NOT NULL,
    location_lng DECIMAL(11, 8) NOT NULL,
    condition weather_condition NOT NULL,
    temperature DECIMAL(5, 2),
    humidity DECIMAL(5, 2),
    wind_speed DECIMAL(5, 2),
    precipitation_chance DECIMAL(5, 4),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent logs table
CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id),
    action VARCHAR(100) NOT NULL,
    result JSONB,
    duration_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Simulation logs table
CREATE TABLE simulation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tick_number INTEGER NOT NULL,
    events_processed INTEGER DEFAULT 0,
    agents_active INTEGER DEFAULT 0,
    duration_ms INTEGER,
    status VARCHAR(50) DEFAULT 'success',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance metrics table
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 4) NOT NULL,
    metric_unit VARCHAR(20),
    tags JSONB DEFAULT '{}',
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_agents_type_status ON agents(agent_type, status);
CREATE INDEX idx_agents_last_heartbeat ON agents(last_heartbeat);
CREATE INDEX idx_inventory_product_status ON inventory(product_id, status);
CREATE INDEX idx_inventory_location ON inventory(location_lat, location_lng);
CREATE INDEX idx_fleet_status_location ON fleet(status, current_location_lat, current_location_lng);
CREATE INDEX idx_orders_status_priority ON orders(status, priority);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_routes_vehicle_status ON routes(vehicle_id, status);
CREATE INDEX idx_demand_forecasts_product ON demand_forecasts(product_id);
CREATE INDEX idx_events_type_time ON events(event_type, start_time, end_time);
CREATE INDEX idx_weather_location_time ON weather_data(location_lat, location_lng, recorded_at);
CREATE INDEX idx_agent_logs_agent_time ON agent_logs(agent_id, created_at);
CREATE INDEX idx_simulation_logs_tick ON simulation_logs(tick_number);
CREATE INDEX idx_performance_metrics_name_time ON performance_metrics(metric_name, recorded_at);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fleet_updated_at BEFORE UPDATE ON fleet
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pricing_updated_at BEFORE UPDATE ON pricing
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data

-- Sample agents
INSERT INTO agents (name, agent_type, status, config) VALUES
('Restock Agent 1', 'restock', 'idle', '{"reorder_threshold": 0.2, "safety_stock": 0.1}'),
('Route Agent 1', 'route', 'idle', '{"algorithm": "genetic", "max_vehicles": 50}'),
('Pricing Agent 1', 'pricing', 'idle', '{"base_markup": 0.15, "dynamic_threshold": 0.3}'),
('Dispatch Agent 1', 'dispatch', 'idle', '{"max_capacity": 1000, "priority_weight": 0.7}'),
('Forecasting Agent 1', 'forecasting', 'idle', '{"horizon_hours": 24, "confidence_threshold": 0.7}');

-- Sample inventory
INSERT INTO inventory (product_id, product_name, quantity, min_quantity, max_quantity, location_lat, location_lng) VALUES
('PROD001', 'Fresh Groceries', 150, 50, 500, 40.7128, -74.0060),
('PROD002', 'Electronics', 75, 25, 200, 40.7128, -74.0060),
('PROD003', 'Clothing', 200, 100, 1000, 40.7128, -74.0060),
('PROD004', 'Home Goods', 120, 60, 300, 40.7128, -74.0060),
('PROD005', 'Pharmaceuticals', 80, 30, 150, 40.7128, -74.0060);

-- Sample fleet
INSERT INTO fleet (vehicle_id, vehicle_type, capacity, current_location_lat, current_location_lng, status) VALUES
('VEH001', 'delivery_van', 500, 40.7128, -74.0060, 'available'),
('VEH002', 'delivery_van', 500, 40.7128, -74.0060, 'available'),
('VEH003', 'truck', 1000, 40.7128, -74.0060, 'available'),
('VEH004', 'motorcycle', 50, 40.7128, -74.0060, 'available'),
('VEH005', 'delivery_van', 500, 40.7128, -74.0060, 'maintenance');

-- Sample orders
INSERT INTO orders (customer_id, product_id, quantity, status, priority, pickup_location_lat, pickup_location_lng, delivery_location_lat, delivery_location_lng) VALUES
('CUST001', 'PROD001', 10, 'pending', 1, 40.7128, -74.0060, 40.7589, -73.9851),
('CUST002', 'PROD002', 2, 'pending', 2, 40.7128, -74.0060, 40.7505, -73.9934),
('CUST003', 'PROD003', 5, 'pending', 1, 40.7128, -74.0060, 40.7829, -73.9654),
('CUST004', 'PROD004', 3, 'pending', 3, 40.7128, -74.0060, 40.7549, -73.9840),
('CUST005', 'PROD005', 1, 'pending', 1, 40.7128, -74.0060, 40.7614, -73.9776);

-- Sample pricing
INSERT INTO pricing (product_id, base_price, current_price, demand_factor, supply_factor) VALUES
('PROD001', 25.00, 25.00, 1.0, 1.0),
('PROD002', 150.00, 150.00, 1.0, 1.0),
('PROD003', 45.00, 45.00, 1.0, 1.0),
('PROD004', 80.00, 80.00, 1.0, 1.0),
('PROD005', 35.00, 35.00, 1.0, 1.0);

-- Sample weather data
INSERT INTO weather_data (location_lat, location_lng, condition, temperature, humidity, wind_speed, precipitation_chance) VALUES
(40.7128, -74.0060, 'sunny', 22.5, 65.0, 12.0, 0.1),
(40.7589, -73.9851, 'cloudy', 20.0, 70.0, 15.0, 0.3),
(40.7505, -73.9934, 'sunny', 23.0, 60.0, 10.0, 0.05),
(40.7829, -73.9654, 'rainy', 18.5, 85.0, 20.0, 0.8),
(40.7549, -73.9840, 'cloudy', 21.0, 75.0, 14.0, 0.4);

-- Sample events
INSERT INTO events (event_type, severity, description, location_lat, location_lng, start_time, end_time) VALUES
('traffic', 'medium', 'Traffic congestion on main route', 40.7128, -74.0060, NOW(), NOW() + INTERVAL '2 hours'),
('weather', 'low', 'Light rain expected', 40.7589, -73.9851, NOW(), NOW() + INTERVAL '4 hours'),
('demand_spike', 'high', 'High demand for electronics', 40.7505, -73.9934, NOW(), NOW() + INTERVAL '6 hours');

-- Initialize simulation state
INSERT INTO simulation_state (status, current_tick, config) VALUES
('stopped', 0, '{"tick_interval": 900, "speed_multiplier": 1.0}');

-- Create views for common queries
CREATE VIEW agent_status_summary AS
SELECT 
    agent_type,
    status,
    COUNT(*) as count,
    MAX(last_heartbeat) as last_heartbeat
FROM agents
GROUP BY agent_type, status;

CREATE VIEW inventory_summary AS
SELECT 
    status,
    COUNT(*) as product_count,
    SUM(quantity) as total_quantity,
    AVG(quantity) as avg_quantity
FROM inventory
GROUP BY status;

CREATE VIEW fleet_status_summary AS
SELECT 
    status,
    COUNT(*) as vehicle_count,
    SUM(capacity) as total_capacity
FROM fleet
GROUP BY status;

CREATE VIEW order_status_summary AS
SELECT 
    status,
    COUNT(*) as order_count,
    SUM(quantity) as total_quantity,
    AVG(priority) as avg_priority
FROM orders
GROUP BY status;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO neuraroute_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO neuraroute_user;

-- Create function to get system health
CREATE OR REPLACE FUNCTION get_system_health()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'database', 'healthy',
        'agents', (SELECT COUNT(*) FROM agents WHERE status = 'running'),
        'fleet', (SELECT COUNT(*) FROM fleet WHERE status = 'available'),
        'orders', (SELECT COUNT(*) FROM orders WHERE status = 'pending'),
        'inventory', (SELECT COUNT(*) FROM inventory WHERE status = 'low_stock'),
        'timestamp', NOW()
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Create function to get agent performance
CREATE OR REPLACE FUNCTION get_agent_performance(hours_back INTEGER DEFAULT 24)
RETURNS TABLE(agent_id UUID, agent_name VARCHAR, actions_count BIGINT, success_rate DECIMAL, avg_duration DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        a.id,
        a.name,
        COUNT(al.id) as actions_count,
        AVG(CASE WHEN al.success THEN 1.0 ELSE 0.0 END) as success_rate,
        AVG(al.duration_ms) as avg_duration
    FROM agents a
    LEFT JOIN agent_logs al ON a.id = al.agent_id 
        AND al.created_at >= NOW() - INTERVAL '1 hour' * hours_back
    GROUP BY a.id, a.name;
END;
$$ LANGUAGE plpgsql; 