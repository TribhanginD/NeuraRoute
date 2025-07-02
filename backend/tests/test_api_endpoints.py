"""
Tests for NeuraRoute API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


class TestHealthEndpoints:
    """Test health check and root endpoints."""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "NeuraRoute"
        assert data["version"] == "1.0.0"
        assert "docs" in data
        assert "health" in data


class TestSimulationEndpoints:
    """Test simulation control endpoints."""
    
    def test_get_simulation_status(self, client: TestClient):
        """Test getting simulation status."""
        response = client.get("/api/v1/simulation/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "is_running" in data
    
    def test_start_simulation(self, client: TestClient):
        """Test starting simulation."""
        response = client.post("/api/v1/simulation/start")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
    
    def test_stop_simulation(self, client: TestClient):
        """Test stopping simulation."""
        response = client.post("/api/v1/simulation/stop")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
    
    def test_get_simulation_history(self, client: TestClient):
        """Test getting simulation history."""
        response = client.get("/api/v1/simulation/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_simulation_metrics(self, client: TestClient):
        """Test getting simulation metrics."""
        response = client.get("/api/v1/simulation/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_ticks" in data
        assert "uptime" in data
        assert "performance_metrics" in data


class TestAgentEndpoints:
    """Test agent management endpoints."""
    
    def test_get_all_agents(self, client: TestClient):
        """Test getting all agents."""
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_agent_by_id(self, client: TestClient):
        """Test getting specific agent."""
        response = client.get("/api/v1/agents/restock_agent")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "status" in data
        assert "type" in data
    
    def test_start_agent(self, client: TestClient):
        """Test starting an agent."""
        response = client.post("/api/v1/agents/restock_agent/start")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
    
    def test_stop_agent(self, client: TestClient):
        """Test stopping an agent."""
        response = client.post("/api/v1/agents/restock_agent/stop")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
    
    def test_get_agent_logs(self, client: TestClient):
        """Test getting agent logs."""
        response = client.get("/api/v1/agents/restock_agent/logs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_agent_metrics(self, client: TestClient):
        """Test getting agent metrics."""
        response = client.get("/api/v1/agents/restock_agent/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "performance" in data
        assert "health" in data
        assert "last_action" in data


class TestInventoryEndpoints:
    """Test inventory management endpoints."""
    
    def test_get_all_inventory(self, client: TestClient):
        """Test getting all inventory."""
        response = client.get("/api/v1/inventory")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_merchant_inventory(self, client: TestClient):
        """Test getting merchant inventory."""
        response = client.get("/api/v1/inventory/merchant_001")
        assert response.status_code == 200
        data = response.json()
        assert "merchant_id" in data
        assert "items" in data
    
    def test_update_inventory(self, client: TestClient):
        """Test updating inventory."""
        inventory_data = {
            "items": [
                {"name": "Test Item", "quantity": 15, "price": 10.99}
            ]
        }
        response = client.put("/api/v1/inventory/merchant_001", json=inventory_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_get_inventory_alerts(self, client: TestClient):
        """Test getting inventory alerts."""
        response = client.get("/api/v1/inventory/alerts")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_inventory_history(self, client: TestClient):
        """Test getting inventory history."""
        response = client.get("/api/v1/inventory/merchant_001/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestFleetEndpoints:
    """Test fleet management endpoints."""
    
    def test_get_all_fleet(self, client: TestClient):
        """Test getting all fleet vehicles."""
        response = client.get("/api/v1/fleet")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_vehicle_by_id(self, client: TestClient):
        """Test getting specific vehicle."""
        response = client.get("/api/v1/fleet/fleet_001")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "status" in data
        assert "current_location" in data
    
    def test_update_vehicle_location(self, client: TestClient):
        """Test updating vehicle location."""
        location_data = {
            "lat": 40.7589,
            "lng": -73.9851
        }
        response = client.put("/api/v1/fleet/fleet_001/location", json=location_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_get_fleet_routes(self, client: TestClient):
        """Test getting fleet routes."""
        response = client.get("/api/v1/fleet/routes")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_fleet_metrics(self, client: TestClient):
        """Test getting fleet metrics."""
        response = client.get("/api/v1/fleet/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_vehicles" in data
        assert "available_vehicles" in data
        assert "utilization_rate" in data


class TestMerchantEndpoints:
    """Test merchant management endpoints."""
    
    def test_get_all_merchants(self, client: TestClient):
        """Test getting all merchants."""
        response = client.get("/api/v1/merchants")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_merchant_by_id(self, client: TestClient):
        """Test getting specific merchant."""
        response = client.get("/api/v1/merchants/merchant_001")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "location" in data
    
    def test_create_merchant(self, client: TestClient):
        """Test creating a new merchant."""
        merchant_data = {
            "name": "New Test Merchant",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "category": "retail",
            "status": "active"
        }
        response = client.post("/api/v1/merchants", json=merchant_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == merchant_data["name"]
    
    def test_update_merchant(self, client: TestClient):
        """Test updating merchant."""
        update_data = {
            "name": "Updated Merchant Name",
            "status": "inactive"
        }
        response = client.put("/api/v1/merchants/merchant_001", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_get_merchant_orders(self, client: TestClient):
        """Test getting merchant orders."""
        response = client.get("/api/v1/merchants/merchant_001/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestForecastingEndpoints:
    """Test forecasting endpoints."""
    
    def test_get_current_forecast(self, client: TestClient):
        """Test getting current forecast."""
        response = client.get("/api/v1/forecasting/current")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_forecast_by_merchant(self, client: TestClient):
        """Test getting forecast for specific merchant."""
        response = client.get("/api/v1/forecasting/merchant_001")
        assert response.status_code == 200
        data = response.json()
        assert "merchant_id" in data
        assert "demand_forecast" in data
        assert "confidence" in data
    
    def test_get_forecast_history(self, client: TestClient):
        """Test getting forecast history."""
        response = client.get("/api/v1/forecasting/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_update_forecast(self, client: TestClient):
        """Test updating forecast."""
        forecast_data = {
            "demand_forecast": 200,
            "confidence": 0.9,
            "factors": {
                "weather": "rainy",
                "events": ["sports_game"],
                "seasonal_factor": 1.1
            }
        }
        response = client.put("/api/v1/forecasting/merchant_001", json=forecast_data)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_get_forecast_accuracy(self, client: TestClient):
        """Test getting forecast accuracy metrics."""
        response = client.get("/api/v1/forecasting/accuracy")
        assert response.status_code == 200
        data = response.json()
        assert "overall_accuracy" in data
        assert "merchant_accuracy" in data
        assert "time_period" in data


class TestWebSocketEndpoints:
    """Test WebSocket endpoints."""
    
    def test_websocket_connection(self, client: TestClient):
        """Test WebSocket connection."""
        with client.websocket_connect("/ws") as websocket:
            # Send a test message
            websocket.send_json({"type": "ping", "data": "test"})
            
            # Receive response
            data = websocket.receive_json()
            assert "type" in data
            assert "timestamp" in data
    
    def test_websocket_simulation_updates(self, client: TestClient):
        """Test WebSocket simulation updates."""
        with client.websocket_connect("/ws") as websocket:
            # Subscribe to simulation updates
            websocket.send_json({"type": "subscribe", "channel": "simulation"})
            
            # Should receive subscription confirmation
            data = websocket.receive_json()
            assert data["type"] == "subscription_confirmed"
            assert data["channel"] == "simulation"


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_agent_id(self, client: TestClient):
        """Test invalid agent ID."""
        response = client.get("/api/v1/agents/invalid_agent")
        assert response.status_code == 404
    
    def test_invalid_merchant_id(self, client: TestClient):
        """Test invalid merchant ID."""
        response = client.get("/api/v1/merchants/invalid_merchant")
        assert response.status_code == 404
    
    def test_invalid_fleet_id(self, client: TestClient):
        """Test invalid fleet ID."""
        response = client.get("/api/v1/fleet/invalid_fleet")
        assert response.status_code == 404
    
    def test_invalid_inventory_data(self, client: TestClient):
        """Test invalid inventory data."""
        invalid_data = {"invalid": "data"}
        response = client.put("/api/v1/inventory/merchant_001", json=invalid_data)
        assert response.status_code == 422
    
    def test_invalid_forecast_data(self, client: TestClient):
        """Test invalid forecast data."""
        invalid_data = {"invalid": "forecast"}
        response = client.put("/api/v1/forecasting/merchant_001", json=invalid_data)
        assert response.status_code == 422 