"""
Agentic Simulation Engine for NeuraRoute
Provides simulation capabilities for the agentic AI system
"""

import asyncio
import structlog
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from app.ai.agentic_system import get_agentic_system
from app.core.database import get_db
from app.models.agents import AgenticAction, ActionType, ApprovalStatus

logger = structlog.get_logger()

class SimulationEventType(str, Enum):
    """Types of simulation events"""
    INVENTORY_UPDATE = "inventory_update"
    DEMAND_SPIKE = "demand_spike"
    DELIVERY_DELAY = "delivery_delay"
    WEATHER_CHANGE = "weather_change"
    EVENT_ANNOUNCEMENT = "event_announcement"
    TRAFFIC_UPDATE = "traffic_update"

@dataclass
class SimulationEvent:
    """Represents a simulation event"""
    event_type: SimulationEventType
    timestamp: datetime
    data: Dict[str, Any]
    description: str

@dataclass
class MarketDayScenario:
    """Represents a market day scenario"""
    name: str
    description: str
    duration_hours: int
    events: List[SimulationEvent]
    initial_context: Dict[str, Any]

class AgenticSimulationEngine:
    """Simulation engine for agentic AI system"""
    
    def __init__(self):
        self.agentic_system = None
        self.is_running = False
        self.current_scenario = None
        self.current_time = None
        self.simulation_speed = 1.0  # 1 second real time = 1 minute simulation time
        self.events_processed = 0
        self.actions_generated = 0
        self.simulation_log = []
        
        # Predefined scenarios
        self.scenarios = self._create_scenarios()
    
    async def initialize(self):
        """Initialize the simulation engine"""
        logger.info("Initializing Agentic Simulation Engine")
        self.agentic_system = await get_agentic_system()
        logger.info("Agentic Simulation Engine initialized")
    
    def _create_scenarios(self) -> Dict[str, MarketDayScenario]:
        """Create predefined market day scenarios"""
        scenarios = {}
        
        # Normal Market Day
        normal_events = [
            SimulationEvent(
                event_type=SimulationEventType.INVENTORY_UPDATE,
                timestamp=datetime.utcnow() + timedelta(hours=2),
                data={"sku_id": "BREAD_001", "quantity": 15, "threshold": 20},
                description="Bread inventory running low"
            ),
            SimulationEvent(
                event_type=SimulationEventType.DEMAND_SPIKE,
                timestamp=datetime.utcnow() + timedelta(hours=4),
                data={"sku_id": "MILK_001", "demand_increase": 1.5},
                description="Milk demand spike due to weather"
            ),
            SimulationEvent(
                event_type=SimulationEventType.DELIVERY_DELAY,
                timestamp=datetime.utcnow() + timedelta(hours=6),
                data={"driver_id": "DRV_001", "delay_minutes": 30},
                description="Delivery truck delayed due to traffic"
            )
        ]
        
        scenarios["normal_market_day"] = MarketDayScenario(
            name="Normal Market Day",
            description="A typical market day with moderate activity",
            duration_hours=12,
            events=normal_events,
            initial_context={
                "inventory": [
                    {"sku_name": "Fresh Bread", "quantity": 25, "reorder_threshold": 20},
                    {"sku_name": "Milk", "quantity": 30, "reorder_threshold": 25},
                    {"sku_name": "Eggs", "quantity": 50, "reorder_threshold": 30},
                    {"sku_name": "Cheese", "quantity": 15, "reorder_threshold": 20}
                ],
                "demand_forecast": [
                    {"sku_name": "Fresh Bread", "predicted_demand": 30},
                    {"sku_name": "Milk", "predicted_demand": 25},
                    {"sku_name": "Eggs", "predicted_demand": 20},
                    {"sku_name": "Cheese", "predicted_demand": 18}
                ],
                "deliveries": [
                    {"driver_id": "DRV_001", "status": "in_transit", "estimated_arrival": "10:30"},
                    {"driver_id": "DRV_002", "status": "loading", "estimated_arrival": "11:45"}
                ],
                "market_conditions": {
                    "weather": "Partly Cloudy",
                    "events": "None",
                    "traffic": "Normal"
                }
            }
        )
        
        # High Demand Day
        high_demand_events = [
            SimulationEvent(
                event_type=SimulationEventType.EVENT_ANNOUNCEMENT,
                timestamp=datetime.utcnow() + timedelta(hours=1),
                data={"event": "Local Festival", "expected_attendance": 5000},
                description="Local festival announced - high demand expected"
            ),
            SimulationEvent(
                event_type=SimulationEventType.DEMAND_SPIKE,
                timestamp=datetime.utcnow() + timedelta(hours=3),
                data={"sku_id": "BREAD_001", "demand_increase": 2.0},
                description="Bread demand doubles due to festival"
            ),
            SimulationEvent(
                event_type=SimulationEventType.DEMAND_SPIKE,
                timestamp=datetime.utcnow() + timedelta(hours=4),
                data={"sku_id": "MILK_001", "demand_increase": 1.8},
                description="Milk demand increases significantly"
            ),
            SimulationEvent(
                event_type=SimulationEventType.TRAFFIC_UPDATE,
                timestamp=datetime.utcnow() + timedelta(hours=5),
                data={"traffic_level": "Heavy", "affected_routes": ["ROUTE_001", "ROUTE_002"]},
                description="Heavy traffic due to festival"
            )
        ]
        
        scenarios["high_demand_day"] = MarketDayScenario(
            name="High Demand Day",
            description="A day with unusually high demand due to local events",
            duration_hours=12,
            events=high_demand_events,
            initial_context={
                "inventory": [
                    {"sku_name": "Fresh Bread", "quantity": 30, "reorder_threshold": 20},
                    {"sku_name": "Milk", "quantity": 35, "reorder_threshold": 25},
                    {"sku_name": "Eggs", "quantity": 60, "reorder_threshold": 30},
                    {"sku_name": "Cheese", "quantity": 20, "reorder_threshold": 20}
                ],
                "demand_forecast": [
                    {"sku_name": "Fresh Bread", "predicted_demand": 60},
                    {"sku_name": "Milk", "predicted_demand": 45},
                    {"sku_name": "Eggs", "predicted_demand": 35},
                    {"sku_name": "Cheese", "predicted_demand": 30}
                ],
                "deliveries": [
                    {"driver_id": "DRV_001", "status": "in_transit", "estimated_arrival": "09:30"},
                    {"driver_id": "DRV_002", "status": "loading", "estimated_arrival": "10:15"},
                    {"driver_id": "DRV_003", "status": "available", "estimated_arrival": "11:00"}
                ],
                "market_conditions": {
                    "weather": "Sunny",
                    "events": "Local Festival",
                    "traffic": "Moderate"
                }
            }
        )
        
        # Supply Chain Crisis
        crisis_events = [
            SimulationEvent(
                event_type=SimulationEventType.INVENTORY_UPDATE,
                timestamp=datetime.utcnow() + timedelta(hours=1),
                data={"sku_id": "BREAD_001", "quantity": 5, "threshold": 20},
                description="Bread inventory critically low"
            ),
            SimulationEvent(
                event_type=SimulationEventType.DELIVERY_DELAY,
                timestamp=datetime.utcnow() + timedelta(hours=2),
                data={"driver_id": "DRV_001", "delay_minutes": 120},
                description="Major delivery delay due to supplier issues"
            ),
            SimulationEvent(
                event_type=SimulationEventType.WEATHER_CHANGE,
                timestamp=datetime.utcnow() + timedelta(hours=4),
                data={"weather": "Storm", "impact": "delivery_disruption"},
                description="Storm approaching - delivery disruption expected"
            ),
            SimulationEvent(
                event_type=SimulationEventType.INVENTORY_UPDATE,
                timestamp=datetime.utcnow() + timedelta(hours=6),
                data={"sku_id": "MILK_001", "quantity": 3, "threshold": 25},
                description="Milk inventory critically low"
            )
        ]
        
        scenarios["supply_chain_crisis"] = MarketDayScenario(
            name="Supply Chain Crisis",
            description="A day with supply chain disruptions and inventory shortages",
            duration_hours=12,
            events=crisis_events,
            initial_context={
                "inventory": [
                    {"sku_name": "Fresh Bread", "quantity": 8, "reorder_threshold": 20},
                    {"sku_name": "Milk", "quantity": 10, "reorder_threshold": 25},
                    {"sku_name": "Eggs", "quantity": 25, "reorder_threshold": 30},
                    {"sku_name": "Cheese", "quantity": 12, "reorder_threshold": 20}
                ],
                "demand_forecast": [
                    {"sku_name": "Fresh Bread", "predicted_demand": 25},
                    {"sku_name": "Milk", "predicted_demand": 30},
                    {"sku_name": "Eggs", "predicted_demand": 20},
                    {"sku_name": "Cheese", "predicted_demand": 15}
                ],
                "deliveries": [
                    {"driver_id": "DRV_001", "status": "delayed", "estimated_arrival": "14:30"},
                    {"driver_id": "DRV_002", "status": "cancelled", "estimated_arrival": "N/A"}
                ],
                "market_conditions": {
                    "weather": "Stormy",
                    "events": "None",
                    "traffic": "Heavy"
                }
            }
        )
        
        return scenarios
    
    async def start_simulation(self, scenario_name: str, speed: float = 1.0) -> Dict[str, Any]:
        """Start a simulation with the specified scenario"""
        if self.is_running:
            raise ValueError("Simulation already running")
        
        if scenario_name not in self.scenarios:
            raise ValueError(f"Scenario '{scenario_name}' not found")
        
        try:
            self.current_scenario = self.scenarios[scenario_name]
            self.current_time = datetime.utcnow()
            self.simulation_speed = speed
            self.is_running = True
            self.events_processed = 0
            self.actions_generated = 0
            self.simulation_log = []
            
            # Set simulation mode
            self.agentic_system.set_simulation_mode(True)
            
            # Process initial context
            initial_result = await self.agentic_system.process_situation(
                self.current_scenario.initial_context
            )
            
            self.simulation_log.append({
                "timestamp": self.current_time.isoformat(),
                "event": "simulation_started",
                "scenario": scenario_name,
                "agent_response": initial_result
            })
            
            logger.info(f"Started simulation: {scenario_name}")
            
            return {
                "success": True,
                "scenario": scenario_name,
                "start_time": self.current_time.isoformat(),
                "duration_hours": self.current_scenario.duration_hours,
                "events_count": len(self.current_scenario.events),
                "initial_actions": len(initial_result.get("actions", []))
            }
            
        except Exception as e:
            logger.error(f"Error starting simulation: {str(e)}")
            self.is_running = False
            raise
    
    async def run_simulation_step(self) -> Dict[str, Any]:
        """Run one step of the simulation"""
        if not self.is_running:
            raise ValueError("Simulation not running")
        
        try:
            # Advance time
            self.current_time += timedelta(minutes=15)  # 15-minute intervals
            
            # Check for events to trigger
            triggered_events = []
            for event in self.current_scenario.events:
                if event.timestamp <= self.current_time:
                    triggered_events.append(event)
            
            # Process triggered events
            context_updates = {}
            for event in triggered_events:
                context_updates.update(self._process_event(event))
                self.events_processed += 1
            
            # Update context and process with agentic system
            if context_updates:
                current_context = self._get_current_context()
                current_context.update(context_updates)
                
                result = await self.agentic_system.process_situation(current_context)
                self.actions_generated += len(result.get("actions", []))
                
                self.simulation_log.append({
                    "timestamp": self.current_time.isoformat(),
                    "events_triggered": [e.event_type.value for e in triggered_events],
                    "context_updates": context_updates,
                    "agent_response": result
                })
            else:
                self.simulation_log.append({
                    "timestamp": self.current_time.isoformat(),
                    "events_triggered": [],
                    "context_updates": {},
                    "agent_response": None
                })
            
            # Check if simulation should end
            simulation_end_time = datetime.utcnow() + timedelta(hours=self.current_scenario.duration_hours)
            if self.current_time >= simulation_end_time:
                await self.stop_simulation()
                return {
                    "step_completed": True,
                    "simulation_ended": True,
                    "final_stats": self.get_simulation_stats()
                }
            
            return {
                "step_completed": True,
                "simulation_ended": False,
                "current_time": self.current_time.isoformat(),
                "events_triggered": len(triggered_events),
                "actions_generated": len(result.get("actions", [])) if context_updates else 0
            }
            
        except Exception as e:
            logger.error(f"Error in simulation step: {str(e)}")
            raise
    
    async def stop_simulation(self) -> Dict[str, Any]:
        """Stop the current simulation"""
        if not self.is_running:
            return {"success": False, "message": "No simulation running"}
        
        try:
            self.is_running = False
            self.agentic_system.set_simulation_mode(False)
            
            stats = self.get_simulation_stats()
            
            logger.info(f"Stopped simulation: {stats}")
            
            return {
                "success": True,
                "message": "Simulation stopped",
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error stopping simulation: {str(e)}")
            raise
    
    def _process_event(self, event: SimulationEvent) -> Dict[str, Any]:
        """Process a simulation event and return context updates"""
        updates = {}
        
        if event.event_type == SimulationEventType.INVENTORY_UPDATE:
            updates["inventory_update"] = event.data
            
        elif event.event_type == SimulationEventType.DEMAND_SPIKE:
            updates["demand_spike"] = event.data
            
        elif event.event_type == SimulationEventType.DELIVERY_DELAY:
            updates["delivery_delay"] = event.data
            
        elif event.event_type == SimulationEventType.WEATHER_CHANGE:
            updates["weather_change"] = event.data
            
        elif event.event_type == SimulationEventType.EVENT_ANNOUNCEMENT:
            updates["event_announcement"] = event.data
            
        elif event.event_type == SimulationEventType.TRAFFIC_UPDATE:
            updates["traffic_update"] = event.data
        
        return updates
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Get the current simulation context"""
        # This would be updated based on the simulation state
        return self.current_scenario.initial_context.copy()
    
    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get simulation statistics"""
        return {
            "scenario": self.current_scenario.name if self.current_scenario else None,
            "is_running": self.is_running,
            "current_time": self.current_time.isoformat() if self.current_time else None,
            "events_processed": self.events_processed,
            "actions_generated": self.actions_generated,
            "simulation_log_entries": len(self.simulation_log)
        }
    
    def get_available_scenarios(self) -> List[Dict[str, Any]]:
        """Get list of available scenarios"""
        return [
            {
                "name": name,
                "scenario": {
                    "name": scenario.name,
                    "description": scenario.description,
                    "duration_hours": scenario.duration_hours,
                    "events_count": len(scenario.events)
                }
            }
            for name, scenario in self.scenarios.items()
        ]
    
    def get_simulation_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get simulation log entries"""
        return self.simulation_log[-limit:] if self.simulation_log else []

# Global instance
_simulation_engine = None

async def get_simulation_engine() -> AgenticSimulationEngine:
    """Get the global simulation engine instance"""
    global _simulation_engine
    if _simulation_engine is None:
        _simulation_engine = AgenticSimulationEngine()
        await _simulation_engine.initialize()
    return _simulation_engine
