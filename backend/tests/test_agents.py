"""
Tests for NeuraRoute agent system
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from app.agents.manager import AgentManager
from app.agents.base_agent import BaseAgent
from app.agents.restock_agent import RestockAgent
from app.agents.route_agent import RouteAgent
from app.agents.pricing_agent import PricingAgent
from app.agents.dispatch_agent import DispatchAgent
from app.agents.forecasting_agent import ForecastingAgent


class TestBaseAgent:
    """Test base agent functionality."""
    
    @pytest.fixture
    def base_agent(self):
        """Create a base agent instance."""
        return BaseAgent(
            agent_id="test_agent",
            agent_type="test",
            config={"test": "config"}
        )
    
    def test_agent_initialization(self, base_agent):
        """Test agent initialization."""
        assert base_agent.agent_id == "test_agent"
        assert base_agent.agent_type == "test"
        assert base_agent.config == {"test": "config"}
        assert base_agent.status == "initialized"
        assert base_agent.is_running is False
    
    def test_agent_status_management(self, base_agent):
        """Test agent status management."""
        base_agent.set_status("running")
        assert base_agent.status == "running"
        
        base_agent.set_status("stopped")
        assert base_agent.status == "stopped"
    
    def test_agent_health_check(self, base_agent):
        """Test agent health check."""
        health = base_agent.get_health()
        assert "status" in health
        assert "last_heartbeat" in health
        assert "uptime" in health
    
    def test_agent_logging(self, base_agent):
        """Test agent logging functionality."""
        base_agent.log_action("test_action", {"data": "test"})
        logs = base_agent.get_logs()
        assert len(logs) > 0
        assert logs[-1]["action"] == "test_action"
        assert logs[-1]["data"]["data"] == "test"


class TestRestockAgent:
    """Test restock agent functionality."""
    
    @pytest.fixture
    def restock_agent(self):
        """Create a restock agent instance."""
        return RestockAgent(
            agent_id="restock_agent",
            config={
                "inventory_threshold": 10,
                "restock_quantity": 50,
                "check_interval": 300
            }
        )
    
    @pytest.mark.asyncio
    async def test_restock_agent_initialization(self, restock_agent):
        """Test restock agent initialization."""
        await restock_agent.initialize()
        assert restock_agent.status == "ready"
        assert restock_agent.inventory_threshold == 10
        assert restock_agent.restock_quantity == 50
    
    @pytest.mark.asyncio
    async def test_check_inventory_levels(self, restock_agent):
        """Test inventory level checking."""
        # Mock inventory data
        inventory_data = {
            "merchant_001": {
                "items": [
                    {"name": "Item 1", "quantity": 5, "threshold": 10},
                    {"name": "Item 2", "quantity": 15, "threshold": 10}
                ]
            }
        }
        
        with patch.object(restock_agent, 'get_inventory_data', return_value=inventory_data):
            alerts = await restock_agent.check_inventory_levels()
            assert len(alerts) == 1
            assert alerts[0]["merchant_id"] == "merchant_001"
            assert alerts[0]["item_name"] == "Item 1"
    
    @pytest.mark.asyncio
    async def test_generate_restock_orders(self, restock_agent):
        """Test restock order generation."""
        alerts = [
            {
                "merchant_id": "merchant_001",
                "item_name": "Item 1",
                "current_quantity": 5,
                "threshold": 10
            }
        ]
        
        orders = await restock_agent.generate_restock_orders(alerts)
        assert len(orders) == 1
        assert orders[0]["merchant_id"] == "merchant_001"
        assert orders[0]["item_name"] == "Item 1"
        assert orders[0]["quantity"] == 50
    
    @pytest.mark.asyncio
    async def test_restock_agent_cycle(self, restock_agent):
        """Test restock agent cycle execution."""
        with patch.object(restock_agent, 'check_inventory_levels', return_value=[]):
            with patch.object(restock_agent, 'generate_restock_orders', return_value=[]):
                result = await restock_agent.execute_cycle()
                assert result["status"] == "completed"
                assert "alerts_checked" in result
                assert "orders_generated" in result


class TestRouteAgent:
    """Test route agent functionality."""
    
    @pytest.fixture
    def route_agent(self):
        """Create a route agent instance."""
        return RouteAgent(
            agent_id="route_agent",
            config={
                "optimization_algorithm": "genetic",
                "update_interval": 300,
                "max_route_time": 3600
            }
        )
    
    @pytest.mark.asyncio
    async def test_route_agent_initialization(self, route_agent):
        """Test route agent initialization."""
        await route_agent.initialize()
        assert route_agent.status == "ready"
        assert route_agent.optimization_algorithm == "genetic"
    
    @pytest.mark.asyncio
    async def test_optimize_routes(self, route_agent):
        """Test route optimization."""
        fleet_data = [
            {
                "id": "fleet_001",
                "current_location": {"lat": 40.7128, "lng": -74.0060},
                "capacity": 1000,
                "status": "available"
            }
        ]
        
        orders = [
            {
                "id": "order_001",
                "pickup_location": {"lat": 40.7589, "lng": -73.9851},
                "delivery_location": {"lat": 40.7505, "lng": -73.9934},
                "priority": "high"
            }
        ]
        
        with patch.object(route_agent, 'get_fleet_data', return_value=fleet_data):
            with patch.object(route_agent, 'get_pending_orders', return_value=orders):
                routes = await route_agent.optimize_routes()
                assert len(routes) > 0
                assert "fleet_id" in routes[0]
                assert "route_points" in routes[0]
                assert "estimated_time" in routes[0]
    
    @pytest.mark.asyncio
    async def test_calculate_route_metrics(self, route_agent):
        """Test route metrics calculation."""
        route = {
            "fleet_id": "fleet_001",
            "route_points": [
                {"lat": 40.7128, "lng": -74.0060},
                {"lat": 40.7589, "lng": -73.9851},
                {"lat": 40.7505, "lng": -73.9934}
            ]
        }
        
        metrics = await route_agent.calculate_route_metrics(route)
        assert "total_distance" in metrics
        assert "estimated_time" in metrics
        assert "fuel_consumption" in metrics
        assert "efficiency_score" in metrics
    
    @pytest.mark.asyncio
    async def test_route_agent_cycle(self, route_agent):
        """Test route agent cycle execution."""
        with patch.object(route_agent, 'optimize_routes', return_value=[]):
            with patch.object(route_agent, 'update_fleet_routes', return_value=True):
                result = await route_agent.execute_cycle()
                assert result["status"] == "completed"
                assert "routes_optimized" in result
                assert "routes_updated" in result


class TestPricingAgent:
    """Test pricing agent functionality."""
    
    @pytest.fixture
    def pricing_agent(self):
        """Create a pricing agent instance."""
        return PricingAgent(
            agent_id="pricing_agent",
            config={
                "base_markup": 0.15,
                "demand_sensitivity": 0.1,
                "competition_factor": 0.05,
                "update_interval": 600
            }
        )
    
    @pytest.mark.asyncio
    async def test_pricing_agent_initialization(self, pricing_agent):
        """Test pricing agent initialization."""
        await pricing_agent.initialize()
        assert pricing_agent.status == "ready"
        assert pricing_agent.base_markup == 0.15
    
    @pytest.mark.asyncio
    async def test_calculate_dynamic_pricing(self, pricing_agent):
        """Test dynamic pricing calculation."""
        base_price = 10.0
        demand_factor = 1.2
        competition_factor = 0.95
        weather_factor = 1.1
        
        price = await pricing_agent.calculate_dynamic_pricing(
            base_price, demand_factor, competition_factor, weather_factor
        )
        
        assert price > base_price
        assert isinstance(price, float)
    
    @pytest.mark.asyncio
    async def test_analyze_market_conditions(self, pricing_agent):
        """Test market condition analysis."""
        market_data = {
            "demand_level": "high",
            "competition_prices": [9.99, 11.99, 10.50],
            "weather_condition": "rainy",
            "seasonal_factor": 1.15
        }
        
        analysis = await pricing_agent.analyze_market_conditions(market_data)
        assert "demand_factor" in analysis
        assert "competition_factor" in analysis
        assert "weather_factor" in analysis
        assert "recommended_adjustment" in analysis
    
    @pytest.mark.asyncio
    async def test_update_pricing_strategy(self, pricing_agent):
        """Test pricing strategy updates."""
        items = [
            {
                "id": "item_001",
                "name": "Test Item",
                "base_price": 10.0,
                "current_price": 11.0
            }
        ]
        
        market_analysis = {
            "demand_factor": 1.2,
            "competition_factor": 0.95,
            "weather_factor": 1.1,
            "recommended_adjustment": 0.05
        }
        
        with patch.object(pricing_agent, 'analyze_market_conditions', return_value=market_analysis):
            updates = await pricing_agent.update_pricing_strategy(items)
            assert len(updates) == 1
            assert "item_id" in updates[0]
            assert "new_price" in updates[0]
            assert "adjustment_reason" in updates[0]
    
    @pytest.mark.asyncio
    async def test_pricing_agent_cycle(self, pricing_agent):
        """Test pricing agent cycle execution."""
        with patch.object(pricing_agent, 'get_pricing_items', return_value=[]):
            with patch.object(pricing_agent, 'update_pricing_strategy', return_value=[]):
                result = await pricing_agent.execute_cycle()
                assert result["status"] == "completed"
                assert "items_analyzed" in result
                assert "prices_updated" in result


class TestDispatchAgent:
    """Test dispatch agent functionality."""
    
    @pytest.fixture
    def dispatch_agent(self):
        """Create a dispatch agent instance."""
        return DispatchAgent(
            agent_id="dispatch_agent",
            config={
                "assignment_algorithm": "greedy",
                "priority_weights": {
                    "urgent": 3.0,
                    "high": 2.0,
                    "normal": 1.0,
                    "low": 0.5
                },
                "update_interval": 60
            }
        )
    
    @pytest.mark.asyncio
    async def test_dispatch_agent_initialization(self, dispatch_agent):
        """Test dispatch agent initialization."""
        await dispatch_agent.initialize()
        assert dispatch_agent.status == "ready"
        assert dispatch_agent.assignment_algorithm == "greedy"
    
    @pytest.mark.asyncio
    async def test_assign_orders_to_fleet(self, dispatch_agent):
        """Test order assignment to fleet."""
        orders = [
            {
                "id": "order_001",
                "priority": "urgent",
                "pickup_location": {"lat": 40.7128, "lng": -74.0060},
                "delivery_location": {"lat": 40.7589, "lng": -73.9851},
                "estimated_duration": 1800
            }
        ]
        
        fleet = [
            {
                "id": "fleet_001",
                "current_location": {"lat": 40.7128, "lng": -74.0060},
                "capacity": 1000,
                "status": "available",
                "current_load": 0
            }
        ]
        
        assignments = await dispatch_agent.assign_orders_to_fleet(orders, fleet)
        assert len(assignments) == 1
        assert assignments[0]["order_id"] == "order_001"
        assert assignments[0]["fleet_id"] == "fleet_001"
    
    @pytest.mark.asyncio
    async def test_optimize_fleet_utilization(self, dispatch_agent):
        """Test fleet utilization optimization."""
        fleet_data = [
            {
                "id": "fleet_001",
                "utilization_rate": 0.7,
                "current_orders": 3,
                "max_capacity": 5
            },
            {
                "id": "fleet_002",
                "utilization_rate": 0.3,
                "current_orders": 1,
                "max_capacity": 5
            }
        ]
        
        optimization = await dispatch_agent.optimize_fleet_utilization(fleet_data)
        assert "rebalancing_suggestions" in optimization
        assert "efficiency_improvements" in optimization
    
    @pytest.mark.asyncio
    async def test_dispatch_agent_cycle(self, dispatch_agent):
        """Test dispatch agent cycle execution."""
        with patch.object(dispatch_agent, 'get_pending_orders', return_value=[]):
            with patch.object(dispatch_agent, 'get_available_fleet', return_value=[]):
                with patch.object(dispatch_agent, 'assign_orders_to_fleet', return_value=[]):
                    result = await dispatch_agent.execute_cycle()
                    assert result["status"] == "completed"
                    assert "orders_assigned" in result
                    assert "fleet_utilized" in result


class TestForecastingAgent:
    """Test forecasting agent functionality."""
    
    @pytest.fixture
    def forecasting_agent(self):
        """Create a forecasting agent instance."""
        return ForecastingAgent(
            agent_id="forecasting_agent",
            config={
                "forecast_horizon": 24,
                "update_interval": 900,
                "confidence_threshold": 0.8,
                "model_type": "prophet"
            }
        )
    
    @pytest.mark.asyncio
    async def test_forecasting_agent_initialization(self, forecasting_agent):
        """Test forecasting agent initialization."""
        await forecasting_agent.initialize()
        assert forecasting_agent.status == "ready"
        assert forecasting_agent.forecast_horizon == 24
    
    @pytest.mark.asyncio
    async def test_generate_demand_forecast(self, forecasting_agent):
        """Test demand forecast generation."""
        historical_data = [
            {"timestamp": "2024-01-01T10:00:00Z", "demand": 100},
            {"timestamp": "2024-01-01T11:00:00Z", "demand": 120},
            {"timestamp": "2024-01-01T12:00:00Z", "demand": 150}
        ]
        
        weather_data = {
            "condition": "sunny",
            "temperature": 25,
            "precipitation": 0
        }
        
        events_data = [
            {"name": "local_festival", "impact": "high", "duration": 4}
        ]
        
        with patch.object(forecasting_agent, 'get_historical_data', return_value=historical_data):
            with patch.object(forecasting_agent, 'get_weather_data', return_value=weather_data):
                with patch.object(forecasting_agent, 'get_events_data', return_value=events_data):
                    forecast = await forecasting_agent.generate_demand_forecast("merchant_001")
                    assert "merchant_id" in forecast
                    assert "demand_forecast" in forecast
                    assert "confidence" in forecast
                    assert "factors" in forecast
    
    @pytest.mark.asyncio
    async def test_analyze_forecast_accuracy(self, forecasting_agent):
        """Test forecast accuracy analysis."""
        actual_data = [
            {"timestamp": "2024-01-01T10:00:00Z", "actual_demand": 110},
            {"timestamp": "2024-01-01T11:00:00Z", "actual_demand": 125},
            {"timestamp": "2024-01-01T12:00:00Z", "actual_demand": 145}
        ]
        
        forecast_data = [
            {"timestamp": "2024-01-01T10:00:00Z", "predicted_demand": 105},
            {"timestamp": "2024-01-01T11:00:00Z", "predicted_demand": 120},
            {"timestamp": "2024-01-01T12:00:00Z", "predicted_demand": 150}
        ]
        
        accuracy = await forecasting_agent.analyze_forecast_accuracy(actual_data, forecast_data)
        assert "overall_accuracy" in accuracy
        assert "mean_absolute_error" in accuracy
        assert "root_mean_square_error" in accuracy
        assert "improvement_suggestions" in accuracy
    
    @pytest.mark.asyncio
    async def test_forecasting_agent_cycle(self, forecasting_agent):
        """Test forecasting agent cycle execution."""
        with patch.object(forecasting_agent, 'get_merchants', return_value=["merchant_001"]):
            with patch.object(forecasting_agent, 'generate_demand_forecast', return_value={}):
                result = await forecasting_agent.execute_cycle()
                assert result["status"] == "completed"
                assert "forecasts_generated" in result
                assert "accuracy_analyzed" in result


class TestAgentManager:
    """Test agent manager functionality."""
    
    @pytest.fixture
    def agent_manager(self):
        """Create an agent manager instance."""
        return AgentManager()
    
    @pytest.mark.asyncio
    async def test_agent_manager_initialization(self, agent_manager):
        """Test agent manager initialization."""
        await agent_manager.initialize()
        assert agent_manager.is_healthy()
        assert len(agent_manager.agents) > 0
    
    @pytest.mark.asyncio
    async def test_agent_lifecycle_management(self, agent_manager):
        """Test agent lifecycle management."""
        await agent_manager.initialize()
        
        # Test starting an agent
        result = await agent_manager.start_agent("restock_agent")
        assert result is True
        
        # Test stopping an agent
        result = await agent_manager.stop_agent("restock_agent")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_agent_health_monitoring(self, agent_manager):
        """Test agent health monitoring."""
        await agent_manager.initialize()
        
        health_status = await agent_manager.get_health_status()
        assert "overall_health" in health_status
        assert "agent_status" in health_status
        
        for agent_id, status in health_status["agent_status"].items():
            assert "status" in status
            assert "last_heartbeat" in status
            assert "uptime" in status
    
    @pytest.mark.asyncio
    async def test_agent_coordination(self, agent_manager):
        """Test agent coordination."""
        await agent_manager.initialize()
        
        # Test agent communication
        result = await agent_manager.coordinate_agents()
        assert "coordination_status" in result
        assert "inter_agent_communication" in result
    
    @pytest.mark.asyncio
    async def test_agent_manager_shutdown(self, agent_manager):
        """Test agent manager shutdown."""
        await agent_manager.initialize()
        await agent_manager.shutdown()
        
        # All agents should be stopped
        for agent in agent_manager.agents.values():
            assert agent.status == "stopped" 