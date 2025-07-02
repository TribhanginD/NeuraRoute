-- NeuraRoute Database Initialization
-- This script creates all necessary tables and initial data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE agent_status AS ENUM ('stopped', 'running', 'error', 'starting', 'stopping');
CREATE TYPE agent_type AS ENUM ('restock', 'route', 'pricing', 'dispatch', 'forecasting');
CREATE TYPE simulation_status AS ENUM ('stopped', 'running', 'paused', 'error');
CREATE TYPE order_status AS ENUM ('pending', 'assigned', 'in_transit', 'delivered', 'cancelled');
CREATE TYPE vehicle_status AS ENUM ('available', 'busy', 'maintenance', 'offline');
CREATE TYPE inventory_status AS ENUM ('in_stock', 'low_stock', 'out_of_stock', 'reserved');

-- Create tables

-- Agents table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    agent_type agent_type NOT NULL,
    status agent_status DEFAULT 'stopped',
    config JSONB DEFAULT '{}',
    memory JSONB DEFAULT '{}',
    last_cycle TIMESTAMP WITH TIME ZONE,
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
    speed_multiplier DECIMAL DEFAULT 1.0,
    config JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Merchants table
CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    address TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    business_hours JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- SKUs table
CREATE TABLE skus (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    unit_price DECIMAL(10, 2),
    cost_price DECIMAL(10, 2),
    weight_kg DECIMAL(8, 3),
    volume_m3 DECIMAL(8, 3),
    shelf_life_days INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inventory items table
CREATE TABLE inventory_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku_id UUID REFERENCES skus(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 0,
    reserved_quantity INTEGER DEFAULT 0,
    status inventory_status DEFAULT 'in_stock',
    last_restock_date TIMESTAMP WITH TIME ZONE,
    expiry_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(sku_id, merchant_id)
);

-- Vehicles table
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    vehicle_type VARCHAR(50),
    capacity_kg DECIMAL(8, 2),
    capacity_m3 DECIMAL(8, 2),
    current_lat DECIMAL(10, 8),
    current_lng DECIMAL(11, 8),
    status vehicle_status DEFAULT 'available',
    current_route_id UUID,
    driver_name VARCHAR(100),
    fuel_level DECIMAL(5, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Routes table
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    name VARCHAR(200),
    waypoints JSONB DEFAULT '[]',
    total_distance_km DECIMAL(8, 2),
    estimated_duration_minutes INTEGER,
    status VARCHAR(50) DEFAULT 'planned',
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    customer_name VARCHAR(200),
    customer_email VARCHAR(255),
    customer_phone VARCHAR(20),
    delivery_address TEXT,
    delivery_lat DECIMAL(10, 8),
    delivery_lng DECIMAL(11, 8),
    status order_status DEFAULT 'pending',
    total_amount DECIMAL(10, 2),
    priority INTEGER DEFAULT 1,
    requested_delivery_time TIMESTAMP WITH TIME ZONE,
    assigned_vehicle_id UUID REFERENCES vehicles(id),
    assigned_route_id UUID REFERENCES routes(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order items table
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    sku_id UUID REFERENCES skus(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Demand forecasts table
CREATE TABLE demand_forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku_id UUID REFERENCES skus(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    predicted_demand INTEGER,
    confidence_lower INTEGER,
    confidence_upper INTEGER,
    confidence_level DECIMAL(3, 2),
    context JSONB DEFAULT '{}',
    model_version VARCHAR(50),
    accuracy_score DECIMAL(3, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(sku_id, merchant_id, forecast_date)
);

-- Agent logs table
CREATE TABLE agent_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Simulation events table
CREATE TABLE simulation_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tick_number INTEGER NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pricing history table
CREATE TABLE pricing_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku_id UUID REFERENCES skus(id) ON DELETE CASCADE,
    merchant_id UUID REFERENCES merchants(id) ON DELETE CASCADE,
    old_price DECIMAL(10, 2),
    new_price DECIMAL(10, 2),
    reason TEXT,
    agent_id UUID REFERENCES agents(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_agents_type_status ON agents(agent_type, status);
CREATE INDEX idx_inventory_sku_merchant ON inventory_items(sku_id, merchant_id);
CREATE INDEX idx_orders_status_priority ON orders(status, priority);
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_routes_vehicle_status ON routes(vehicle_id, status);
CREATE INDEX idx_forecasts_sku_merchant_date ON demand_forecasts(sku_id, merchant_id, forecast_date);
CREATE INDEX idx_agent_logs_agent_timestamp ON agent_logs(agent_id, timestamp);
CREATE INDEX idx_simulation_events_tick ON simulation_events(tick_number);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_simulation_state_updated_at BEFORE UPDATE ON simulation_state FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_merchants_updated_at BEFORE UPDATE ON merchants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_skus_updated_at BEFORE UPDATE ON skus FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_inventory_items_updated_at BEFORE UPDATE ON inventory_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vehicles_updated_at BEFORE UPDATE ON vehicles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_routes_updated_at BEFORE UPDATE ON routes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_demand_forecasts_updated_at BEFORE UPDATE ON demand_forecasts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial data

-- Insert default agents
INSERT INTO agents (name, agent_type, status, config) VALUES
('Restock Agent', 'restock', 'stopped', '{"memory_retention_days": 30, "restock_threshold": 0.2}'),
('Route Agent', 'route', 'stopped', '{"optimization_algorithm": "genetic", "max_vehicles": 10}'),
('Pricing Agent', 'pricing', 'stopped', '{"base_margin": 0.15, "dynamic_factor": 0.1}'),
('Dispatch Agent', 'dispatch', 'stopped', '{"max_orders_per_vehicle": 5, "time_window_minutes": 30}'),
('Forecasting Agent', 'forecasting', 'stopped', '{"forecast_horizon_days": 7, "confidence_level": 0.95}');

-- Insert initial simulation state
INSERT INTO simulation_state (status, current_tick, speed_multiplier) VALUES
('stopped', 0, 1.0);

-- Insert sample merchants
INSERT INTO merchants (name, location_lat, location_lng, address, contact_email, business_hours) VALUES
('Downtown Market', 40.7128, -74.0060, '123 Main St, New York, NY', 'downtown@market.com', '{"monday": {"open": "08:00", "close": "20:00"}, "tuesday": {"open": "08:00", "close": "20:00"}, "wednesday": {"open": "08:00", "close": "20:00"}, "thursday": {"open": "08:00", "close": "20:00"}, "friday": {"open": "08:00", "close": "22:00"}, "saturday": {"open": "09:00", "close": "22:00"}, "sunday": {"open": "10:00", "close": "18:00"}}'),
('Uptown Grocery', 40.7589, -73.9851, '456 Park Ave, New York, NY', 'uptown@grocery.com', '{"monday": {"open": "07:00", "close": "21:00"}, "tuesday": {"open": "07:00", "close": "21:00"}, "wednesday": {"open": "07:00", "close": "21:00"}, "thursday": {"open": "07:00", "close": "21:00"}, "friday": {"open": "07:00", "close": "22:00"}, "saturday": {"open": "08:00", "close": "22:00"}, "sunday": {"open": "08:00", "close": "20:00"}}'),
('Brooklyn Deli', 40.7182, -73.9584, '789 Bedford Ave, Brooklyn, NY', 'brooklyn@deli.com', '{"monday": {"open": "06:00", "close": "19:00"}, "tuesday": {"open": "06:00", "close": "19:00"}, "wednesday": {"open": "06:00", "close": "19:00"}, "thursday": {"open": "06:00", "close": "19:00"}, "friday": {"open": "06:00", "close": "20:00"}, "saturday": {"open": "07:00", "close": "20:00"}, "sunday": {"open": "07:00", "close": "18:00"}}');

-- Insert sample SKUs
INSERT INTO skus (name, description, category, unit_price, cost_price, weight_kg, volume_m3, shelf_life_days) VALUES
('Fresh Milk 1L', 'Organic whole milk', 'Dairy', 4.99, 3.50, 1.0, 0.001, 7),
('Bread Loaf', 'Artisan sourdough bread', 'Bakery', 3.99, 2.50, 0.5, 0.0005, 5),
('Bananas 1kg', 'Organic yellow bananas', 'Produce', 2.99, 1.80, 1.0, 0.002, 7),
('Chicken Breast 500g', 'Free-range chicken breast', 'Meat', 8.99, 6.00, 0.5, 0.0008, 3),
('Tomatoes 500g', 'Vine-ripened tomatoes', 'Produce', 3.49, 2.20, 0.5, 0.001, 7),
('Cheese Block 250g', 'Aged cheddar cheese', 'Dairy', 5.99, 4.00, 0.25, 0.0003, 14),
('Apples 1kg', 'Red delicious apples', 'Produce', 4.49, 2.80, 1.0, 0.002, 14),
('Ground Beef 500g', 'Lean ground beef', 'Meat', 7.99, 5.50, 0.5, 0.0006, 2);

-- Insert sample inventory
INSERT INTO inventory_items (sku_id, merchant_id, quantity, status) 
SELECT s.id, m.id, 
       CASE 
           WHEN s.category = 'Dairy' THEN 50
           WHEN s.category = 'Bakery' THEN 30
           WHEN s.category = 'Produce' THEN 40
           WHEN s.category = 'Meat' THEN 25
           ELSE 35
       END,
       'in_stock'
FROM skus s CROSS JOIN merchants m;

-- Insert sample vehicles
INSERT INTO vehicles (name, vehicle_type, capacity_kg, capacity_m3, current_lat, current_lng, status, driver_name, fuel_level) VALUES
('Delivery Van 1', 'Van', 1000.0, 5.0, 40.7128, -74.0060, 'available', 'John Smith', 85.5),
('Delivery Van 2', 'Van', 1000.0, 5.0, 40.7589, -73.9851, 'available', 'Jane Doe', 92.3),
('Truck 1', 'Truck', 2000.0, 10.0, 40.7182, -73.9584, 'available', 'Mike Johnson', 78.9),
('Scooter 1', 'Scooter', 50.0, 0.2, 40.7128, -74.0060, 'available', 'Alex Brown', 95.0);

-- Insert sample orders
INSERT INTO orders (merchant_id, customer_name, customer_email, delivery_address, delivery_lat, delivery_lng, status, total_amount, priority) VALUES
((SELECT id FROM merchants WHERE name = 'Downtown Market'), 'Alice Johnson', 'alice@email.com', '100 Broadway, New York, NY', 40.7589, -73.9851, 'pending', 25.45, 1),
((SELECT id FROM merchants WHERE name = 'Uptown Grocery'), 'Bob Wilson', 'bob@email.com', '200 5th Ave, New York, NY', 40.7182, -73.9584, 'pending', 18.99, 2),
((SELECT id FROM merchants WHERE name = 'Brooklyn Deli'), 'Carol Davis', 'carol@email.com', '300 Bedford Ave, Brooklyn, NY', 40.7128, -74.0060, 'pending', 32.50, 1);

-- Insert sample order items
INSERT INTO order_items (order_id, sku_id, quantity, unit_price, total_price)
SELECT o.id, s.id, 
       CASE 
           WHEN s.category = 'Dairy' THEN 2
           WHEN s.category = 'Bakery' THEN 1
           WHEN s.category = 'Produce' THEN 3
           WHEN s.category = 'Meat' THEN 1
           ELSE 2
       END,
       s.unit_price,
       s.unit_price * CASE 
           WHEN s.category = 'Dairy' THEN 2
           WHEN s.category = 'Bakery' THEN 1
           WHEN s.category = 'Produce' THEN 3
           WHEN s.category = 'Meat' THEN 1
           ELSE 2
       END
FROM orders o CROSS JOIN skus s
WHERE o.id IN (SELECT id FROM orders LIMIT 3) AND s.id IN (SELECT id FROM skus LIMIT 4);

-- Insert sample demand forecasts
INSERT INTO demand_forecasts (sku_id, merchant_id, forecast_date, predicted_demand, confidence_lower, confidence_upper, confidence_level, model_version, accuracy_score)
SELECT s.id, m.id, 
       CURRENT_DATE + INTERVAL '1 day',
       CASE 
           WHEN s.category = 'Dairy' THEN 45
           WHEN s.category = 'Bakery' THEN 28
           WHEN s.category = 'Produce' THEN 35
           WHEN s.category = 'Meat' THEN 22
           ELSE 30
       END,
       CASE 
           WHEN s.category = 'Dairy' THEN 40
           WHEN s.category = 'Bakery' THEN 25
           WHEN s.category = 'Produce' THEN 30
           WHEN s.category = 'Meat' THEN 18
           ELSE 25
       END,
       CASE 
           WHEN s.category = 'Dairy' THEN 50
           WHEN s.category = 'Bakery' THEN 31
           WHEN s.category = 'Produce' THEN 40
           WHEN s.category = 'Meat' THEN 26
           ELSE 35
       END,
       0.95,
       'v1.0',
       0.85
FROM skus s CROSS JOIN merchants m
WHERE s.id IN (SELECT id FROM skus LIMIT 4);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Create a view for system overview
CREATE VIEW system_overview AS
SELECT 
    (SELECT COUNT(*) FROM agents WHERE status = 'running') as active_agents,
    (SELECT COUNT(*) FROM orders WHERE status = 'pending') as pending_orders,
    (SELECT COUNT(*) FROM vehicles WHERE status = 'available') as available_vehicles,
    (SELECT COUNT(*) FROM inventory_items WHERE status = 'low_stock') as low_stock_items,
    (SELECT status FROM simulation_state ORDER BY updated_at DESC LIMIT 1) as simulation_status,
    (SELECT current_tick FROM simulation_state ORDER BY updated_at DESC LIMIT 1) as current_tick;

-- Create a view for agent performance
CREATE VIEW agent_performance AS
SELECT 
    a.name,
    a.agent_type,
    a.status,
    a.last_cycle,
    COUNT(al.id) as log_count,
    COUNT(CASE WHEN al.level = 'ERROR' THEN 1 END) as error_count
FROM agents a
LEFT JOIN agent_logs al ON a.id = al.agent_id AND al.timestamp > NOW() - INTERVAL '24 hours'
GROUP BY a.id, a.name, a.agent_type, a.status, a.last_cycle; 