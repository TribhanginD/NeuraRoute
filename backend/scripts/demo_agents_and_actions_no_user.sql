-- 1. Insert demo agents (if not already present)
INSERT INTO agents (
  id, name, agent_type, status, merchant_id, last_heartbeat,
  tasks_completed, tasks_failed, average_response_time, created_at, updated_at
)
SELECT
  gen_random_uuid(), name, agent_type, status, NULL, NOW(),
  0, 0, 1.0, NOW(), NOW()
FROM (VALUES
  ('Dispatch Agent', 'dispatch', 'online'),
  ('Restock Agent', 'restock', 'online'),
  ('Pricing Agent', 'pricing', 'offline')
) AS t(name, agent_type, status)
WHERE NOT EXISTS (
  SELECT 1 FROM agents WHERE name = t.name
);

-- 2. Fetch a merchant id (will use the first one found)
WITH merchant AS (
  SELECT id AS merchant_id FROM merchants LIMIT 1
),
agents AS (
  SELECT id, agent_type FROM agents WHERE name IN ('Dispatch Agent', 'Restock Agent', 'Pricing Agent')
)
-- 3. Insert demo actions for each agent, using the merchant id and requested_by as NULL
INSERT INTO agent_actions (
  id, agent_id, action, status, requested_by, requested_at, completed_at, error_message
)
SELECT
  gen_random_uuid(),
  a.id,
  CASE a.agent_type
    WHEN 'dispatch' THEN 'dispatch_order'
    WHEN 'restock' THEN 'restock_inventory'
    WHEN 'pricing' THEN 'update_pricing'
    ELSE 'custom_action'
  END,
  'pending',
  NULL,         -- requested_by is NULL, no user dependency
  NOW(),
  NULL,
  NULL
FROM agents a, merchant m; 