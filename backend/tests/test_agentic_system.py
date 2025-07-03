"""
Unit tests for the agentic AI system
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from app.ai.agentic_system import (
    AgenticSystem, AgenticTool, PlaceOrderTool, RerouteDriverTool,
    UpdateInventoryTool, AdjustPricingTool, DispatchFleetTool,
    ActionType, ApprovalStatus, AgentAction
)
from app.simulation.agentic_simulation import (
    AgenticSimulationEngine, SimulationEvent, SimulationEventType,
    MarketDayScenario
)


class TestAgenticTools:
    """Test agentic tools functionality"""
    
    @pytest.fixture
    def place_order_tool(self):
        return PlaceOrderTool()
    
    @pytest.fixture
    def reroute_driver_tool(self):
        return RerouteDriverTool()
    
    @pytest.fixture
    def update_inventory_tool(self):
        return UpdateInventoryTool()
    
    @pytest.fixture
    def adjust_pricing_tool(self):
        return AdjustPricingTool()
    
    @pytest.fixture
    def dispatch_fleet_tool(self):
        return DispatchFleetTool()
    
    def test_place_order_tool_approval_logic(self, place_order_tool):
        """Test place order tool approval logic"""
        # Small order should not require approval
        small_order = {"quantity": 50, "supplier_id": "SUP_001", "sku_id": "SKU_001"}
        assert not place_order_tool._requires_approval(small_order)
        
        # Large order should require approval
        large_order = {"quantity": 150, "supplier_id": "SUP_001", "sku_id": "SKU_001"}
        assert place_order_tool._requires_approval(large_order)
    
    def test_reroute_driver_tool_approval_logic(self, reroute_driver_tool):
        """Test reroute driver tool approval logic"""
        # Normal priority should not require approval
        normal_route = {"priority": "normal", "driver_id": "DRV_001", "new_route": ["A", "B", "C"]}
        assert not reroute_driver_tool._requires_approval(normal_route)
        
        # High priority should require approval
        high_priority_route = {"priority": "high", "driver_id": "DRV_001", "new_route": ["A", "B", "C"]}
        assert reroute_driver_tool._requires_approval(high_priority_route)
        
        # Urgent priority should require approval
        urgent_route = {"priority": "urgent", "driver_id": "DRV_001", "new_route": ["A", "B", "C"]}
        assert reroute_driver_tool._requires_approval(urgent_route)
    
    def test_update_inventory_tool_approval_logic(self, update_inventory_tool):
        """Test update inventory tool approval logic"""
        # Small change should not require approval
        small_change = {"new_quantity": 100}
        assert not update_inventory_tool._requires_approval(small_change)
        
        # Large change should require approval
        large_change = {"new_quantity": 600}
        assert update_inventory_tool._requires_approval(large_change)
    
    def test_adjust_pricing_tool_approval_logic(self, adjust_pricing_tool):
        """Test adjust pricing tool approval logic"""
        # Pricing changes should always require approval
        price_change = {"new_price": 10.99, "sku_id": "SKU_001"}
        assert adjust_pricing_tool._requires_approval(price_change)
    
    def test_dispatch_fleet_tool_approval_logic(self, dispatch_fleet_tool):
        """Test dispatch fleet tool approval logic"""
        # Normal priority should not require approval
        normal_dispatch = {"priority": "normal", "vehicle_ids": ["VEH_001"], "route_id": "ROUTE_001"}
        assert not dispatch_fleet_tool._requires_approval(normal_dispatch)
        
        # Urgent priority should require approval
        urgent_dispatch = {"priority": "urgent", "vehicle_ids": ["VEH_001"], "route_id": "ROUTE_001"}
        assert dispatch_fleet_tool._requires_approval(urgent_dispatch)
    
    @pytest.mark.asyncio
    async def test_place_order_tool_execution(self, place_order_tool):
        """Test place order tool execution"""
        parameters = {
            "supplier_id": "SUP_001",
            "sku_id": "SKU_001",
            "quantity": 100,
            "priority": "normal"
        }
        
        result = await place_order_tool._perform_action(parameters)
        
        assert "order_id" in result
        assert result["supplier_id"] == "SUP_001"
        assert result["sku_id"] == "SKU_001"
        assert result["quantity"] == 100
        assert result["status"] == "confirmed"
    
    @pytest.mark.asyncio
    async def test_reroute_driver_tool_execution(self, reroute_driver_tool):
        """Test reroute driver tool execution"""
        parameters = {
            "driver_id": "DRV_001",
            "new_route": ["STOP_A", "STOP_B", "STOP_C"],
            "reason": "Traffic optimization",
            "priority": "normal"
        }
        
        result = await reroute_driver_tool._perform_action(parameters)
        
        assert result["driver_id"] == "DRV_001"
        assert result["new_route"] == ["STOP_A", "STOP_B", "STOP_C"]
        assert result["status"] == "rerouted"
        assert "estimated_time_saved" in result


@pytest.fixture
async def agentic_system():
    """Create a test agentic system"""
    system = AgenticSystem()
    # Mock the AI manager to avoid actual API calls
    system.ai_manager = Mock()
    system.ai_manager.providers = {"openai": Mock()}
    system.ai_manager.providers["openai"].client = Mock()
    # Mock the agent executor
    system.agent_executor = Mock()
    system.agent_executor.ainvoke = AsyncMock(return_value={"output": "Test reasoning"})
    # Initialize tools
    system._initialize_tools()
    await system.initialize()  # Ensure async initialization
    return system

@pytest.mark.asyncio
async def test_agentic_system_initialization():
    system = await agentic_system()
    assert len(system.tools) == 5
    assert system.simulation_mode is False
    assert len(system.action_queue) == 0
    assert len(system.approved_actions) == 0
    assert len(system.denied_actions) == 0
    # Check that all expected tools are present
    tool_names = [tool.name for tool in system.tools]
    expected_tools = ["place_order", "reroute_driver", "update_inventory", "adjust_pricing", "dispatch_fleet"]
    assert all(tool in tool_names for tool in expected_tools)

@pytest.mark.asyncio
async def test_build_context_prompt():
    system = await agentic_system()
    context = {
        "inventory": [
            {"sku_name": "Bread", "quantity": 15, "reorder_threshold": 20}
        ],
        "demand_forecast": [
            {"sku_name": "Bread", "predicted_demand": 30}
        ],
        "deliveries": [
            {"driver_id": "DRV_001", "status": "in_transit", "estimated_arrival": "10:30"}
        ],
        "market_conditions": {
            "weather": "Sunny",
            "events": "None",
            "traffic": "Normal"
        }
    }
    prompt = system._build_context_prompt(context)
    assert "INVENTORY STATUS:" in prompt
    assert "DEMAND FORECAST:" in prompt
    assert "DELIVERY STATUS:" in prompt
    assert "MARKET CONDITIONS:" in prompt
    assert "optimize logistics operations" in prompt

@pytest.mark.asyncio
async def test_process_situation():
    system = await agentic_system()
    context = {
        "inventory": [
            {"sku_name": "Bread", "quantity": 15, "reorder_threshold": 20}
        ],
        "demand_forecast": [
            {"sku_name": "Bread", "predicted_demand": 30}
        ]
    }
    result = await system.process_situation(context)
    assert "reasoning" in result
    assert "actions" in result
    assert "confidence" in result
    assert "timestamp" in result


class TestAgenticSimulationEngine:
    """Test agentic simulation engine functionality"""
    
    @pytest.fixture
    async def simulation_engine(self):
        """Create a test simulation engine"""
        engine = AgenticSimulationEngine()
        # Mock the agentic system
        engine.agentic_system = Mock()
        engine.agentic_system.process_situation = AsyncMock(return_value={
            "reasoning": "Test reasoning",
            "actions": [],
            "confidence": 0.8,
            "timestamp": datetime.utcnow().isoformat()
        })
        engine.agentic_system.set_simulation_mode = Mock()
        
        return engine
    
    def test_simulation_engine_initialization(self, simulation_engine):
        """Test simulation engine initialization"""
        assert simulation_engine.is_running is False
        assert simulation_engine.current_scenario is None
        assert simulation_engine.current_time is None
        assert simulation_engine.events_processed == 0
        assert simulation_engine.actions_generated == 0
        assert len(simulation_engine.simulation_log) == 0
        
        # Check that scenarios are created
        assert len(simulation_engine.scenarios) == 3
        assert "normal_market_day" in simulation_engine.scenarios
        assert "high_demand_day" in simulation_engine.scenarios
        assert "supply_chain_crisis" in simulation_engine.scenarios
    
    def test_get_available_scenarios(self, simulation_engine):
        """Test getting available scenarios"""
        scenarios = simulation_engine.get_available_scenarios()
        
        assert len(scenarios) == 3
        scenario_names = [s["name"] for s in scenarios]
        assert "normal_market_day" in scenario_names
        assert "high_demand_day" in scenario_names
        assert "supply_chain_crisis" in scenario_names
        
        # Check scenario details
        normal_scenario = next(s for s in scenarios if s["name"] == "normal_market_day")
        assert normal_scenario["scenario"]["name"] == "Normal Market Day"
        assert normal_scenario["scenario"]["duration_hours"] == 12
    
    @pytest.mark.asyncio
    async def test_start_simulation(self, simulation_engine):
        """Test starting a simulation"""
        result = await simulation_engine.start_simulation("normal_market_day", 1.0)
        
        assert result["success"] is True
        assert result["scenario"] == "normal_market_day"
        assert simulation_engine.is_running is True
        assert simulation_engine.current_scenario is not None
        assert simulation_engine.current_time is not None
        assert simulation_engine.simulation_speed == 1.0
        assert len(simulation_engine.simulation_log) == 1
    
    @pytest.mark.asyncio
    async def test_start_simulation_invalid_scenario(self, simulation_engine):
        """Test starting simulation with invalid scenario"""
        with pytest.raises(ValueError, match="Scenario 'invalid_scenario' not found"):
            await simulation_engine.start_simulation("invalid_scenario")
    
    @pytest.mark.asyncio
    async def test_start_simulation_already_running(self, simulation_engine):
        """Test starting simulation when already running"""
        # Start first simulation
        await simulation_engine.start_simulation("normal_market_day")
        
        # Try to start another
        with pytest.raises(ValueError, match="Simulation already running"):
            await simulation_engine.start_simulation("high_demand_day")
    
    @pytest.mark.asyncio
    async def test_run_simulation_step(self, simulation_engine):
        """Test running a simulation step"""
        # Start simulation first
        await simulation_engine.start_simulation("normal_market_day")
        initial_time = simulation_engine.current_time
        
        # Run a step
        result = await simulation_engine.run_simulation_step()
        
        assert result["step_completed"] is True
        assert result["simulation_ended"] is False
        assert simulation_engine.current_time > initial_time
        assert len(simulation_engine.simulation_log) == 2  # Start + step
    
    @pytest.mark.asyncio
    async def test_run_simulation_step_not_running(self, simulation_engine):
        """Test running simulation step when not running"""
        with pytest.raises(ValueError, match="Simulation not running"):
            await simulation_engine.run_simulation_step()
    
    @pytest.mark.asyncio
    async def test_stop_simulation(self, simulation_engine):
        """Test stopping simulation"""
        # Start simulation first
        await simulation_engine.start_simulation("normal_market_day")
        
        # Stop simulation
        result = await simulation_engine.stop_simulation()
        
        assert result["success"] is True
        assert simulation_engine.is_running is False
    
    @pytest.mark.asyncio
    async def test_stop_simulation_not_running(self, simulation_engine):
        """Test stopping simulation when not running"""
        result = await simulation_engine.stop_simulation()
        
        assert result["success"] is False
        assert "No simulation running" in result["message"]
    
    def test_get_simulation_stats(self, simulation_engine):
        """Test getting simulation statistics"""
        stats = simulation_engine.get_simulation_stats()
        
        assert "scenario" in stats
        assert "is_running" in stats
        assert "current_time" in stats
        assert "events_processed" in stats
        assert "actions_generated" in stats
        assert "simulation_log_entries" in stats
        
        assert stats["is_running"] is False
        assert stats["events_processed"] == 0
        assert stats["actions_generated"] == 0
        assert stats["simulation_log_entries"] == 0
    
    def test_get_simulation_log(self, simulation_engine):
        """Test getting simulation log"""
        # Add some test log entries
        simulation_engine.simulation_log = [
            {"timestamp": "2024-01-01T10:00:00", "event": "test1"},
            {"timestamp": "2024-01-01T10:15:00", "event": "test2"},
            {"timestamp": "2024-01-01T10:30:00", "event": "test3"}
        ]
        
        # Get all log entries
        all_entries = simulation_engine.get_simulation_log()
        assert len(all_entries) == 3
        
        # Get limited log entries
        limited_entries = simulation_engine.get_simulation_log(limit=2)
        assert len(limited_entries) == 2
        assert limited_entries[0]["event"] == "test2"
        assert limited_entries[0]["event"] == "test3"
    
    def test_process_event(self, simulation_engine):
        """Test processing simulation events"""
        # Test inventory update event
        inventory_event = SimulationEvent(
            event_type=SimulationEventType.INVENTORY_UPDATE,
            timestamp=datetime.utcnow(),
            data={"sku_id": "BREAD_001", "quantity": 10},
            description="Bread inventory low"
        )
        
        updates = simulation_engine._process_event(inventory_event)
        assert "inventory_update" in updates
        assert updates["inventory_update"]["sku_id"] == "BREAD_001"
        
        # Test demand spike event
        demand_event = SimulationEvent(
            event_type=SimulationEventType.DEMAND_SPIKE,
            timestamp=datetime.utcnow(),
            data={"sku_id": "MILK_001", "demand_increase": 1.5},
            description="Milk demand spike"
        )
        
        updates = simulation_engine._process_event(demand_event)
        assert "demand_spike" in updates
        assert updates["demand_spike"]["demand_increase"] == 1.5


class TestIntegration:
    """Integration tests for the agentic system"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a complete agentic workflow"""
        # This would test the full integration between components
        # For now, we'll test the basic flow
        
        # Create a mock agentic system
        system = AgenticSystem()
        system.ai_manager = Mock()
        system.ai_manager.providers = {"openai": Mock()}
        system.ai_manager.providers["openai"].client = Mock()
        
        system.agent_executor = Mock()
        system.agent_executor.ainvoke = AsyncMock(return_value={"output": "Test reasoning"})
        
        system._initialize_tools()
        
        # Test processing a situation
        context = {
            "inventory": [
                {"sku_name": "Bread", "quantity": 15, "reorder_threshold": 20}
            ],
            "demand_forecast": [
                {"sku_name": "Bread", "predicted_demand": 30}
            ]
        }
        
        result = await system.process_situation(context)
        
        assert "reasoning" in result
        assert "actions" in result
        assert "confidence" in result
        assert "timestamp" in result
        
        # Test getting pending actions
        pending_actions = system.get_pending_actions()
        assert isinstance(pending_actions, list)
        
        # Test getting action history
        history = system.get_action_history()
        assert "pending" in history
        assert "approved" in history
        assert "denied" in history
