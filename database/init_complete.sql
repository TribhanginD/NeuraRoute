-- NeuraRoute Complete Database Initialization Script
-- This script creates all tables with the correct schema and seeds them with sample data

-- Drop existing tables if they exist (for clean initialization)
DROP TABLE IF EXISTS inventory_items CASCADE;
DROP TABLE IF EXISTS sku CASCADE;
DROP TABLE IF EXISTS merchants CASCADE;
DROP TABLE IF EXISTS locations CASCADE;
DROP TABLE IF EXISTS vehicles CASCADE;
DROP TABLE IF EXISTS routes CASCADE;
DROP TABLE IF EXISTS deliveries CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS agents CASCADE;
DROP TABLE IF EXISTS simulation_states CASCADE;
DROP TABLE IF EXISTS demand_forecasts CASCADE;
DROP TABLE IF EXISTS pricing CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS weather_data CASCADE;
DROP TABLE IF EXISTS agent_logs CASCADE;
DROP TABLE IF EXISTS simulation_logs CASCADE;
DROP TABLE IF EXISTS performance_metrics CASCADE;
DROP TABLE IF EXISTS fleet CASCADE;

-- Create enum types (only if they don't exist)
DO $$ BEGIN
    CREATE TYPE route_status AS ENUM ('planned', 'in_progress', 'completed', 'cancelled', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE delivery_status AS ENUM ('pending', 'assigned', 'picked_up', 'in_transit', 'delivered', 'failed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE payment_status AS ENUM ('pending', 'paid', 'failed', 'refunded');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create locations table
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    address VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(50) DEFAULT 'USA' NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    location_type VARCHAR(50) DEFAULT 'warehouse',
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create merchants table
CREATE TABLE merchants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    merchant_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    business_type VARCHAR(50) NOT NULL,
    location_id INTEGER NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    website VARCHAR(200),
    operating_hours JSONB,
    delivery_radius_km DOUBLE PRECISION DEFAULT 5.0,
    minimum_order_amount DOUBLE PRECISION DEFAULT 0.0,
    delivery_fee DOUBLE PRECISION DEFAULT 0.0,
    total_orders INTEGER DEFAULT 0,
    average_rating DOUBLE PRECISION DEFAULT 0.0,
    total_revenue DOUBLE PRECISION DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create SKU table
CREATE TABLE sku (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    unit_price DOUBLE PRECISION NOT NULL,
    cost_price DOUBLE PRECISION NOT NULL,
    weight_kg DOUBLE PRECISION,
    volume_m3 DOUBLE PRECISION,
    shelf_life_days INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create inventory_items table
CREATE TABLE inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id VARCHAR(36) NOT NULL REFERENCES sku(id),
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    location_id UUID NOT NULL REFERENCES locations(id),
    quantity INTEGER DEFAULT 0 NOT NULL,
    reserved_quantity INTEGER DEFAULT 0 NOT NULL,
    status inventory_status DEFAULT 'in_stock',
    last_restock_date TIMESTAMP WITH TIME ZONE,
    expiry_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create vehicles table
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    vehicle_type VARCHAR(50) NOT NULL,
    capacity_kg DOUBLE PRECISION NOT NULL,
    capacity_m3 DOUBLE PRECISION NOT NULL,
    current_lat DOUBLE PRECISION,
    current_lng DOUBLE PRECISION,
    status VARCHAR(20) DEFAULT 'available',
    total_distance_km DOUBLE PRECISION DEFAULT 0.0,
    total_deliveries INTEGER DEFAULT 0,
    average_speed_kmh DOUBLE PRECISION DEFAULT 30.0,
    fuel_efficiency DOUBLE PRECISION,
    current_load_kg DOUBLE PRECISION DEFAULT 0.0,
    current_route_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create routes table
CREATE TABLE routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    route_id VARCHAR(50) UNIQUE NOT NULL,
    vehicle_id UUID REFERENCES vehicles(id),
    status VARCHAR(20) DEFAULT 'planned',
    start_location_id INTEGER NOT NULL,
    end_location_id INTEGER NOT NULL,
    waypoints JSONB,
    estimated_distance_km DOUBLE PRECISION,
    estimated_duration_minutes INTEGER,
    planned_start_time TIMESTAMP WITH TIME ZONE,
    actual_start_time TIMESTAMP WITH TIME ZONE,
    planned_end_time TIMESTAMP WITH TIME ZONE,
    actual_end_time TIMESTAMP WITH TIME ZONE,
    optimization_score DOUBLE PRECISION,
    traffic_factor DOUBLE PRECISION DEFAULT 1.0,
    weather_factor DOUBLE PRECISION DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(50) UNIQUE NOT NULL,
    merchant_id UUID NOT NULL REFERENCES merchants(id),
    customer_id VARCHAR(50) NOT NULL,
    status order_status DEFAULT 'pending',
    total_amount DOUBLE PRECISION NOT NULL,
    delivery_address TEXT,
    delivery_lat DOUBLE PRECISION,
    delivery_lng DOUBLE PRECISION,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create deliveries table
CREATE TABLE deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    delivery_id VARCHAR(50) UNIQUE NOT NULL,
    order_id INTEGER NOT NULL,
    vehicle_id UUID REFERENCES vehicles(id),
    route_id UUID REFERENCES routes(id),
    pickup_location_id INTEGER NOT NULL,
    delivery_location_id INTEGER NOT NULL,
    status delivery_status DEFAULT 'pending',
    requested_pickup_time TIMESTAMP WITH TIME ZONE,
    actual_pickup_time TIMESTAMP WITH TIME ZONE,
    requested_delivery_time TIMESTAMP WITH TIME ZONE,
    actual_delivery_time TIMESTAMP WITH TIME ZONE,
    weight_kg DOUBLE PRECISION NOT NULL,
    volume_m3 DOUBLE PRECISION,
    special_instructions TEXT,
    distance_km DOUBLE PRECISION,
    duration_minutes INTEGER,
    customer_rating INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create agents table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(50) UNIQUE NOT NULL,
    agent_type agent_type NOT NULL,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    config JSONB,
    performance_metrics JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create simulation_states table
CREATE TABLE simulation_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_id VARCHAR(50) UNIQUE NOT NULL,
    simulation_time TIMESTAMP WITH TIME ZONE NOT NULL,
    state_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_inventory_items_sku_id ON inventory_items(sku_id);
CREATE INDEX idx_inventory_items_merchant_id ON inventory_items(merchant_id);
CREATE INDEX idx_inventory_items_location_id ON inventory_items(location_id);
CREATE INDEX idx_inventory_items_status ON inventory_items(status);
CREATE INDEX idx_sku_name ON sku(name);
CREATE INDEX idx_sku_category ON sku(category);
CREATE INDEX idx_merchants_name ON merchants(name);
CREATE INDEX idx_merchants_business_type ON merchants(business_type);
CREATE INDEX idx_vehicles_vehicle_id ON vehicles(vehicle_id);
CREATE INDEX idx_vehicles_status ON vehicles(status);
CREATE INDEX idx_routes_route_id ON routes(route_id);
CREATE INDEX idx_routes_status ON routes(status);
CREATE INDEX idx_orders_order_id ON orders(order_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_deliveries_delivery_id ON deliveries(delivery_id);
CREATE INDEX idx_deliveries_status ON deliveries(status);
CREATE INDEX idx_agents_agent_id ON agents(agent_id);
CREATE INDEX idx_agents_type ON agents(agent_type);

-- Insert sample data

-- Insert locations
INSERT INTO locations (id, name, address, city, state, postal_code, latitude, longitude, location_type) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'Main Warehouse', '123 Industrial Blvd', 'Austin', 'TX', '78701', 30.2672, -97.7431, 'warehouse'),
('550e8400-e29b-41d4-a716-446655440002', 'Downtown Store', '456 Main St', 'Austin', 'TX', '78702', 30.2672, -97.7431, 'store'),
('550e8400-e29b-41d4-a716-446655440003', 'North Distribution Center', '789 North Ave', 'Austin', 'TX', '78703', 30.2672, -97.7431, 'warehouse'),
('550e8400-e29b-41d4-a716-446655440004', 'South Hub', '321 South Rd', 'Austin', 'TX', '78704', 30.2672, -97.7431, 'warehouse'),
('550e8400-e29b-41d4-a716-446655440005', 'East Pickup Point', '654 East Blvd', 'Austin', 'TX', '78705', 30.2672, -97.7431, 'pickup_point');

-- Insert merchants
INSERT INTO merchants (id, merchant_id, name, business_type, location_id, email, phone, operating_hours, delivery_radius_km, minimum_order_amount, delivery_fee, total_orders, average_rating, total_revenue) VALUES
('660e8400-e29b-41d4-a716-446655440001', 'MERCH001', 'Fresh Foods Market', 'grocery', 1, 'contact@freshfoods.com', '512-555-0101', '{"monday": {"open": 8, "close": 22}, "tuesday": {"open": 8, "close": 22}, "wednesday": {"open": 8, "close": 22}, "thursday": {"open": 8, "close": 22}, "friday": {"open": 8, "close": 22}, "saturday": {"open": 9, "close": 21}, "sunday": {"open": 9, "close": 20}}', 10.0, 25.0, 5.0, 150, 4.5, 15000.0),
('660e8400-e29b-41d4-a716-446655440002', 'MERCH002', 'Tech Gadgets Store', 'electronics', 2, 'sales@techgadgets.com', '512-555-0102', '{"monday": {"open": 10, "close": 20}, "tuesday": {"open": 10, "close": 20}, "wednesday": {"open": 10, "close": 20}, "thursday": {"open": 10, "close": 20}, "friday": {"open": 10, "close": 21}, "saturday": {"open": 10, "close": 18}, "sunday": {"open": 12, "close": 17}}', 15.0, 50.0, 8.0, 75, 4.2, 25000.0),
('660e8400-e29b-41d4-a716-446655440003', 'MERCH003', 'Quick Pharmacy', 'pharmacy', 3, 'info@quickpharmacy.com', '512-555-0103', '{"monday": {"open": 7, "close": 23}, "tuesday": {"open": 7, "close": 23}, "wednesday": {"open": 7, "close": 23}, "thursday": {"open": 7, "close": 23}, "friday": {"open": 7, "close": 23}, "saturday": {"open": 8, "close": 22}, "sunday": {"open": 8, "close": 22}}', 8.0, 15.0, 3.0, 200, 4.7, 12000.0),
('660e8400-e29b-41d4-a716-446655440004', 'MERCH004', 'Fashion Boutique', 'clothing', 4, 'hello@fashionboutique.com', '512-555-0104', '{"monday": {"open": 11, "close": 19}, "tuesday": {"open": 11, "close": 19}, "wednesday": {"open": 11, "close": 19}, "thursday": {"open": 11, "close": 19}, "friday": {"open": 11, "close": 20}, "saturday": {"open": 10, "close": 18}, "sunday": {"open": 12, "close": 17}}', 12.0, 30.0, 6.0, 100, 4.3, 18000.0),
('660e8400-e29b-41d4-a716-446655440005', 'MERCH005', 'Home & Garden Center', 'home_goods', 5, 'info@homegarden.com', '512-555-0105', '{"monday": {"open": 8, "close": 20}, "tuesday": {"open": 8, "close": 20}, "wednesday": {"open": 8, "close": 20}, "thursday": {"open": 8, "close": 20}, "friday": {"open": 8, "close": 21}, "saturday": {"open": 8, "close": 18}, "sunday": {"open": 9, "close": 17}}', 20.0, 40.0, 7.0, 60, 4.1, 22000.0);

-- Insert SKUs
INSERT INTO sku (id, name, description, category, unit_price, cost_price, weight_kg, volume_m3, shelf_life_days) VALUES
('SKU001', 'Organic Bananas', 'Fresh organic bananas from local farms', 'produce', 2.99, 1.50, 0.5, 0.001, 7),
('SKU002', 'Whole Milk', 'Fresh whole milk 1 gallon', 'dairy', 4.99, 2.50, 3.8, 0.004, 14),
('SKU003', 'iPhone 15 Pro', 'Latest iPhone model 128GB', 'electronics', 999.99, 750.00, 0.187, 0.0001, 365),
('SKU004', 'Wireless Headphones', 'Bluetooth noise-canceling headphones', 'electronics', 199.99, 120.00, 0.25, 0.0002, 365),
('SKU005', 'Aspirin 500mg', 'Pain relief tablets 100 count', 'pharmacy', 8.99, 4.50, 0.1, 0.0001, 730),
('SKU006', 'Vitamin D3', 'Vitamin D3 supplements 1000IU', 'pharmacy', 12.99, 6.50, 0.05, 0.00005, 1095),
('SKU007', 'Denim Jeans', 'Classic blue denim jeans size 32', 'clothing', 59.99, 25.00, 0.4, 0.002, 365),
('SKU008', 'Cotton T-Shirt', '100% cotton t-shirt size M', 'clothing', 19.99, 8.00, 0.15, 0.0005, 365),
('SKU009', 'Garden Hose', '50ft heavy-duty garden hose', 'home_goods', 29.99, 15.00, 2.5, 0.01, 1095),
('SKU010', 'Plant Pot', 'Ceramic plant pot 8-inch diameter', 'home_goods', 14.99, 7.50, 0.8, 0.003, 1095);

-- Insert inventory items
INSERT INTO inventory_items (id, sku_id, merchant_id, location_id, quantity, reserved_quantity, status, last_restock_date, expiry_date) VALUES
('770e8400-e29b-41d4-a716-446655440001', 'SKU001', '660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 500, 50, 'in_stock', '2024-01-15 08:00:00', '2024-01-22 08:00:00'),
('770e8400-e29b-41d4-a716-446655440002', 'SKU002', '660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 200, 20, 'in_stock', '2024-01-16 08:00:00', '2024-01-30 08:00:00'),
('770e8400-e29b-41d4-a716-446655440003', 'SKU003', '660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 25, 5, 'in_stock', '2024-01-10 08:00:00', '2025-01-10 08:00:00'),
('770e8400-e29b-41d4-a716-446655440004', 'SKU004', '660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 50, 10, 'in_stock', '2024-01-12 08:00:00', '2025-01-12 08:00:00'),
('770e8400-e29b-41d4-a716-446655440005', 'SKU005', '660e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440003', 100, 15, 'in_stock', '2024-01-14 08:00:00', '2026-01-14 08:00:00'),
('770e8400-e29b-41d4-a716-446655440006', 'SKU006', '660e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440003', 75, 8, 'in_stock', '2024-01-13 08:00:00', '2027-01-13 08:00:00'),
('770e8400-e29b-41d4-a716-446655440007', 'SKU007', '660e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440004', 40, 12, 'in_stock', '2024-01-11 08:00:00', '2025-01-11 08:00:00'),
('770e8400-e29b-41d4-a716-446655440008', 'SKU008', '660e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440004', 120, 25, 'in_stock', '2024-01-09 08:00:00', '2025-01-09 08:00:00'),
('770e8400-e29b-41d4-a716-446655440009', 'SKU009', '660e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440005', 30, 5, 'in_stock', '2024-01-08 08:00:00', '2027-01-08 08:00:00'),
('770e8400-e29b-41d4-a716-446655440010', 'SKU010', '660e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440005', 80, 10, 'in_stock', '2024-01-07 08:00:00', '2027-01-07 08:00:00'),
('770e8400-e29b-41d4-a716-446655440011', 'SKU001', '660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 5, 0, 'low_stock', '2024-01-15 08:00:00', '2024-01-22 08:00:00'),
('770e8400-e29b-41d4-a716-446655440012', 'SKU003', '660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 0, 0, 'out_of_stock', '2024-01-10 08:00:00', '2025-01-10 08:00:00');

-- Insert vehicles
INSERT INTO vehicles (id, vehicle_id, name, vehicle_type, capacity_kg, capacity_m3, current_lat, current_lng, status, total_distance_km, total_deliveries, average_speed_kmh, fuel_efficiency, current_load_kg) VALUES
('880e8400-e29b-41d4-a716-446655440001', 'VEH001', 'Delivery Van Alpha', 'van', 1000.0, 8.0, 30.2672, -97.7431, 'available', 1500.5, 45, 35.0, 12.5, 0.0),
('880e8400-e29b-41d4-a716-446655440002', 'VEH002', 'Truck Beta', 'truck', 3000.0, 20.0, 30.2672, -97.7431, 'available', 2800.2, 32, 40.0, 8.2, 0.0),
('880e8400-e29b-41d4-a716-446655440003', 'VEH003', 'Motorcycle Charlie', 'motorcycle', 50.0, 0.5, 30.2672, -97.7431, 'busy', 1200.8, 78, 45.0, 25.0, 15.0),
('880e8400-e29b-41d4-a716-446655440004', 'VEH004', 'Van Delta', 'van', 800.0, 6.0, 30.2672, -97.7431, 'maintenance', 2100.3, 56, 30.0, 15.0, 0.0),
('880e8400-e29b-41d4-a716-446655440005', 'VEH005', 'Truck Echo', 'truck', 2500.0, 15.0, 30.2672, -97.7431, 'offline', 1800.7, 28, 35.0, 10.5, 0.0);

-- Insert routes
INSERT INTO routes (id, route_id, vehicle_id, status, start_location_id, end_location_id, estimated_distance_km, estimated_duration_minutes, planned_start_time, optimization_score, traffic_factor, weather_factor) VALUES
('990e8400-e29b-41d4-a716-446655440001', 'ROUTE001', '880e8400-e29b-41d4-a716-446655440001', 'completed', 1, 2, 15.5, 25, '2024-01-20 09:00:00', 0.85, 1.1, 1.0),
('990e8400-e29b-41d4-a716-446655440002', 'ROUTE002', '880e8400-e29b-41d4-a716-446655440002', 'in_progress', 1, 3, 22.3, 35, '2024-01-20 10:00:00', 0.78, 1.2, 1.1),
('990e8400-e29b-41d4-a716-446655440003', 'ROUTE003', '880e8400-e29b-41d4-a716-446655440003', 'planned', 2, 4, 18.7, 30, '2024-01-20 11:00:00', 0.92, 1.0, 1.0),
('990e8400-e29b-41d4-a716-446655440004', 'ROUTE004', '880e8400-e29b-41d4-a716-446655440001', 'cancelled', 3, 5, 25.1, 40, '2024-01-20 12:00:00', 0.65, 1.3, 1.2),
('990e8400-e29b-41d4-a716-446655440005', 'ROUTE005', '880e8400-e29b-41d4-a716-446655440002', 'failed', 4, 1, 12.8, 20, '2024-01-20 13:00:00', 0.45, 1.4, 1.3);

-- Insert orders
INSERT INTO orders (id, order_id, merchant_id, customer_id, status, total_amount, delivery_address, delivery_lat, delivery_lng) VALUES
('aa0e8400-e29b-41d4-a716-446655440001', 'ORD001', '660e8400-e29b-41d4-a716-446655440001', 'CUST001', 'delivered', 45.99, '123 Customer St, Austin, TX 78701', 30.2672, -97.7431),
('aa0e8400-e29b-41d4-a716-446655440002', 'ORD002', '660e8400-e29b-41d4-a716-446655440002', 'CUST002', 'assigned', 1250.99, '456 Customer Ave, Austin, TX 78702', 30.2672, -97.7431),
('aa0e8400-e29b-41d4-a716-446655440003', 'ORD003', '660e8400-e29b-41d4-a716-446655440003', 'CUST003', 'confirmed', 25.99, '789 Customer Blvd, Austin, TX 78703', 30.2672, -97.7431),
('aa0e8400-e29b-41d4-a716-446655440004', 'ORD004', '660e8400-e29b-41d4-a716-446655440004', 'CUST004', 'pending', 89.99, '321 Customer Rd, Austin, TX 78704', 30.2672, -97.7431),
('aa0e8400-e29b-41d4-a716-446655440005', 'ORD005', '660e8400-e29b-41d4-a716-446655440005', 'CUST005', 'cancelled', 44.99, '654 Customer Ln, Austin, TX 78705', 30.2672, -97.7431);

-- Insert deliveries
INSERT INTO deliveries (id, delivery_id, order_id, vehicle_id, route_id, pickup_location_id, delivery_location_id, status, weight_kg, volume_m3, distance_km, duration_minutes, customer_rating) VALUES
('bb0e8400-e29b-41d4-a716-446655440001', 'DEL001', 1, '880e8400-e29b-41d4-a716-446655440001', '990e8400-e29b-41d4-a716-446655440001', 1, 2, 'delivered', 5.5, 0.02, 15.5, 25, 5),
('bb0e8400-e29b-41d4-a716-446655440002', 'DEL002', 2, '880e8400-e29b-41d4-a716-446655440002', '990e8400-e29b-41d4-a716-446655440002', 1, 3, 'in_transit', 0.5, 0.001, 22.3, 35, NULL),
('bb0e8400-e29b-41d4-a716-446655440003', 'DEL003', 3, '880e8400-e29b-41d4-a716-446655440003', '990e8400-e29b-41d4-a716-446655440003', 2, 4, 'assigned', 0.1, 0.0001, 18.7, 30, NULL),
('bb0e8400-e29b-41d4-a716-446655440004', 'DEL004', 4, '880e8400-e29b-41d4-a716-446655440001', '990e8400-e29b-41d4-a716-446655440004', 3, 5, 'pending', 2.0, 0.005, 25.1, 40, NULL),
('bb0e8400-e29b-41d4-a716-446655440005', 'DEL005', 5, '880e8400-e29b-41d4-a716-446655440002', '990e8400-e29b-41d4-a716-446655440005', 4, 1, 'failed', 3.5, 0.01, 12.8, 20, 1);

-- Insert agents
INSERT INTO agents (id, agent_id, agent_type, name, status, config, performance_metrics) VALUES
('cc0e8400-e29b-41d4-a716-446655440001', 'AGENT001', 'dispatch', 'Dispatch Agent Alpha', 'active', '{"max_orders_per_vehicle": 5, "optimization_algorithm": "genetic"}', '{"orders_dispatched": 150, "avg_delivery_time": 25.5, "success_rate": 0.95}'),
('cc0e8400-e29b-41d4-a716-446655440002', 'AGENT002', 'forecasting', 'Forecasting Agent Beta', 'active', '{"forecast_horizon_days": 30, "confidence_interval": 0.95}', '{"forecasts_generated": 45, "avg_accuracy": 0.87, "prediction_horizon": 30}'),
('cc0e8400-e29b-41d4-a716-446655440003', 'AGENT003', 'pricing', 'Pricing Agent Charlie', 'active', '{"dynamic_pricing": true, "competitor_tracking": true}', '{"price_updates": 120, "revenue_impact": 0.12, "market_share": 0.23}'),
('cc0e8400-e29b-41d4-a716-446655440004', 'AGENT004', 'route', 'Routing Agent Delta', 'active', '{"algorithm": "ant_colony", "traffic_integration": true}', '{"routes_optimized": 89, "avg_optimization": 0.78, "fuel_savings": 0.15}'),
('cc0e8400-e29b-41d4-a716-446655440005', 'AGENT005', 'restock', 'Inventory Agent Echo', 'active', '{"reorder_point_calculation": true, "demand_forecasting": true}', '{"stockouts_prevented": 23, "inventory_turnover": 4.5, "carrying_cost_reduction": 0.08}');

-- Insert simulation states
INSERT INTO simulation_states (id, simulation_id, simulation_time, state_data, is_active) VALUES
('dd0e8400-e29b-41d4-a716-446655440001', 'SIM001', '2024-01-20 10:30:00', '{"active_vehicles": 3, "pending_orders": 12, "completed_deliveries": 45, "system_load": 0.75}', true),
('dd0e8400-e29b-41d4-a716-446655440002', 'SIM002', '2024-01-20 11:00:00', '{"active_vehicles": 4, "pending_orders": 8, "completed_deliveries": 52, "system_load": 0.68}', true);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_locations_updated_at BEFORE UPDATE ON locations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_merchants_updated_at BEFORE UPDATE ON merchants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sku_updated_at BEFORE UPDATE ON sku FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_inventory_items_updated_at BEFORE UPDATE ON inventory_items FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_vehicles_updated_at BEFORE UPDATE ON vehicles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_routes_updated_at BEFORE UPDATE ON routes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_deliveries_updated_at BEFORE UPDATE ON deliveries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_simulation_states_updated_at BEFORE UPDATE ON simulation_states FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

COMMIT; 