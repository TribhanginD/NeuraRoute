-- NeuraRoute Database Initialization
-- This script creates sample data for the AI-Native Logistics System

-- Create sample locations
INSERT INTO locations (name, address, latitude, longitude, location_type) VALUES
('Downtown Warehouse', '123 Main St, San Francisco, CA', 37.7749, -122.4194, 'warehouse'),
('North Distribution Center', '456 Oak Ave, Oakland, CA', 37.8044, -122.2711, 'distribution_center'),
('South Retail Store', '789 Pine St, San Jose, CA', 37.3382, -121.8863, 'retail'),
('East Fulfillment Center', '321 Elm Blvd, Fremont, CA', 37.5485, -121.9886, 'fulfillment_center');

-- Create sample SKUs
INSERT INTO skus (sku_id, name, category, unit, description) VALUES
('SKU001', 'Organic Bananas', 'produce', 'kg', 'Fresh organic bananas'),
('SKU002', 'Whole Milk', 'dairy', 'liter', 'Fresh whole milk'),
('SKU003', 'Bread Loaf', 'bakery', 'piece', 'Fresh baked bread'),
('SKU004', 'Chicken Breast', 'meat', 'kg', 'Fresh chicken breast'),
('SKU005', 'Tomatoes', 'produce', 'kg', 'Fresh red tomatoes');

-- Create sample inventory items
INSERT INTO inventory_items (sku_id, location_id, quantity, reserved_quantity, available_quantity, last_updated) VALUES
('SKU001', 1, 100, 10, 90, NOW()),
('SKU001', 2, 50, 5, 45, NOW()),
('SKU002', 1, 200, 20, 180, NOW()),
('SKU002', 3, 75, 8, 67, NOW()),
('SKU003', 2, 30, 3, 27, NOW()),
('SKU003', 4, 25, 2, 23, NOW()),
('SKU004', 1, 80, 15, 65, NOW()),
('SKU005', 3, 60, 7, 53, NOW());

-- Create sample vehicles
INSERT INTO vehicles (vehicle_id, vehicle_type, status, capacity_kg, current_load_kg, average_speed_kmh, current_location_id) VALUES
('V001', 'delivery_van', 'available', 1000, 0, 45, 1),
('V002', 'delivery_van', 'in_transit', 1000, 750, 40, 2),
('V003', 'truck', 'available', 5000, 0, 35, 1),
('V004', 'motorcycle', 'in_transit', 50, 25, 60, 3);

-- Create sample merchants
INSERT INTO merchants (merchant_id, name, business_type, status, contact_email, contact_phone, location_id) VALUES
('M001', 'Fresh Foods Market', 'grocery', 'active', 'contact@freshfoods.com', '+1-555-0101', 3),
('M002', 'Urban Deli', 'restaurant', 'active', 'info@urbandeli.com', '+1-555-0102', 3),
('M003', 'Corner Store', 'convenience', 'active', 'hello@cornerstore.com', '+1-555-0103', 3);

-- Create sample customers
INSERT INTO customers (customer_id, name, email, phone, customer_rating) VALUES
('C001', 'John Smith', 'john@email.com', '+1-555-0201', 4.5),
('C002', 'Jane Doe', 'jane@email.com', '+1-555-0202', 4.8),
('C003', 'Bob Wilson', 'bob@email.com', '+1-555-0203', 4.2);

-- Create sample orders
INSERT INTO orders (order_id, merchant_id, customer_id, status, total_amount, created_at) VALUES
('O001', 'M001', 'C001', 'processing', 45.50, NOW() - INTERVAL '2 hours'),
('O002', 'M002', 'C002', 'shipped', 32.75, NOW() - INTERVAL '4 hours'),
('O003', 'M003', 'C003', 'pending', 18.25, NOW() - INTERVAL '1 hour');

-- Create sample agents
INSERT INTO agents (agent_id, name, agent_type, status, config, last_heartbeat, tasks_completed, tasks_failed, average_response_time) VALUES
('A001', 'Restock Agent', 'restock', 'active', '{"check_interval": 300}', NOW(), 15, 1, 250),
('A002', 'Route Agent', 'route', 'active', '{"check_interval": 180}', NOW(), 23, 0, 180),
('A003', 'Pricing Agent', 'pricing', 'active', '{"check_interval": 600}', NOW(), 8, 2, 320),
('A004', 'Dispatch Agent', 'dispatch', 'active', '{"check_interval": 120}', NOW(), 31, 1, 150),
('A005', 'Forecasting Agent', 'forecasting', 'active', '{"check_interval": 3600}', NOW(), 5, 0, 450); 