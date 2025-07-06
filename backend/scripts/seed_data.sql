-- Seed data for NeuraRoute tables

-- Agents
INSERT INTO agents (name, agent_type, status, config) VALUES
  ('Restock Agent 2', 'restock', 'running', '{"reorder_threshold": 0.3}'),
  ('Route Agent 2', 'route', 'idle', '{"algorithm": "dijkstra"}'),
  ('Pricing Agent 2', 'pricing', 'idle', '{"base_markup": 0.10}'),
  ('Dispatch Agent 2', 'dispatch', 'running', '{"max_capacity": 800}'),
  ('Forecasting Agent 2', 'forecasting', 'idle', '{"horizon_hours": 12}');

-- Inventory
INSERT INTO inventory (product_id, product_name, quantity, min_quantity, max_quantity, location_lat, location_lng) VALUES
  ('PROD006', 'Beverages', 60, 20, 200, 40.7130, -74.0070),
  ('PROD007', 'Books', 90, 30, 300, 40.7135, -74.0080);

-- Fleet
INSERT INTO fleet (vehicle_id, vehicle_type, capacity, current_location_lat, current_location_lng, status) VALUES
  ('VEH006', 'truck', 1200, 40.7130, -74.0070, 'available'),
  ('VEH007', 'motorcycle', 60, 40.7135, -74.0080, 'in_use');

-- Routes (use valid vehicle UUIDs)
INSERT INTO routes (vehicle_id, route_data, start_time, status, optimization_score)
SELECT id, '{"stops": ["A", "B", "C"]}', NOW(), 'in_progress', 0.95 FROM fleet WHERE vehicle_id = 'VEH006';

-- Orders
INSERT INTO orders (customer_id, product_id, quantity, status, priority, pickup_location_lat, pickup_location_lng, delivery_location_lat, delivery_location_lng) VALUES
  ('CUST003', 'PROD006', 5, 'confirmed', 1, 40.7130, -74.0070, 40.7200, -74.0000),
  ('CUST004', 'PROD007', 3, 'in_transit', 2, 40.7135, -74.0080, 40.7300, -73.9950);

-- Demand Forecasts
INSERT INTO demand_forecasts (product_id, forecast_data, confidence_score) VALUES
  ('PROD006', '{"demand": 70}', 0.88),
  ('PROD007', '{"demand": 40}', 0.92);

-- Pricing
INSERT INTO pricing (product_id, base_price, current_price, demand_factor, supply_factor) VALUES
  ('PROD006', 2.50, 2.75, 1.1, 0.9),
  ('PROD007', 10.00, 9.50, 0.95, 1.05);

-- Events
INSERT INTO events (event_type, severity, description, location_lat, location_lng, start_time, end_time) VALUES
  ('weather', 'high', 'Heavy rain expected', 40.7130, -74.0070, NOW(), NOW() + INTERVAL '2 hours'),
  ('traffic', 'medium', 'Traffic congestion', 40.7135, -74.0080, NOW(), NOW() + INTERVAL '1 hour');

-- Weather Data
INSERT INTO weather_data (location_lat, location_lng, condition, temperature, humidity, wind_speed, precipitation_chance) VALUES
  (40.7130, -74.0070, 'rainy', 18.5, 85.0, 12.0, 0.8),
  (40.7135, -74.0080, 'cloudy', 20.0, 70.0, 8.0, 0.2);

-- Agent Logs (use valid agent UUIDs)
INSERT INTO agent_logs (agent_id, action, result, duration_ms, success)
SELECT id, 'restock', '{"result": "success"}', 120, true FROM agents WHERE name = 'Restock Agent 2';

-- Simulation Logs
INSERT INTO simulation_logs (tick_number, events_processed, agents_active, duration_ms, status) VALUES
  (1, 5, 3, 200, 'success'),
  (2, 6, 4, 180, 'success');

-- Performance Metrics
INSERT INTO performance_metrics (metric_name, metric_value, metric_unit, tags) VALUES
  ('order_fulfillment_time', 15.2, 'minutes', '{"priority": "high"}'),
  ('vehicle_utilization', 0.85, 'ratio', '{"vehicle_type": "truck"}'); 