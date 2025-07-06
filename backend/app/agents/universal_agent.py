import asyncio
import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, List
import random
from app.agents.base_agent import BaseAgent
from app.ai.agentic_system import get_agentic_system, ActionType, ApprovalStatus

logger = structlog.get_logger()

class UniversalAgent(BaseAgent):
    """A single agent that continuously makes autonomous decisions and requires approval"""

    def __init__(self, agent_id, agent_type=None, config=None):
        super().__init__(agent_id, agent_type, config)
        self.agentic_system = None
        self.decision_interval = 30  # Make decisions every 30 seconds
        self.last_decision_time = None
        self.pending_decisions = []
        self.decision_history = []

    async def _initialize_agent(self):
        logger.info("Initializing UniversalAgent components")
        try:
            # Initialize the agentic system
            self.agentic_system = await get_agentic_system()
            logger.info("UniversalAgent initialized with agentic system")
        except Exception as e:
            logger.warning(f"Failed to initialize agentic system (AI services may not be configured): {str(e)}")
            logger.info("UniversalAgent will continue with mock decision generation")
            self.agentic_system = None

    async def _run_cycle_logic(self):
        """Continuously make autonomous decisions"""
        try:
            current_time = datetime.utcnow()
            
            # Check if it's time to make a decision
            if (self.last_decision_time is None or 
                (current_time - self.last_decision_time).total_seconds() >= self.decision_interval):
                
                await self._make_autonomous_decision()
                self.last_decision_time = current_time
                
        except Exception as e:
            logger.error(f"Error in UniversalAgent decision cycle: {str(e)}")

    async def _make_autonomous_decision(self):
        """Make an autonomous decision based on current system state"""
        try:
            # Get current system context
            context = await self._gather_system_context()
            
            # Generate decision using agentic system
            decision = await self._generate_decision(context)
            
            if decision:
                # Add to pending decisions for user approval
                self.pending_decisions.append(decision)
                self.decision_history.append(decision)
                
                logger.info(f"Generated decision: {decision['action_type']} - {decision['reasoning'][:100]}...")
                
        except Exception as e:
            logger.error(f"Error making autonomous decision: {str(e)}")

    async def _gather_system_context(self) -> Dict[str, Any]:
        """Gather current system context for decision making"""
        # This would normally fetch real data from your database
        # For demo purposes, we'll generate mock context
        return {
            "inventory": [
                {
                    "sku_name": "Widgets",
                    "quantity": random.randint(5, 50),
                    "reorder_threshold": 20
                },
                {
                    "sku_name": "Gadgets", 
                    "quantity": random.randint(10, 100),
                    "reorder_threshold": 30
                }
            ],
            "demand_forecast": [
                {
                    "sku_name": "Widgets",
                    "predicted_demand": random.randint(15, 40)
                },
                {
                    "sku_name": "Gadgets",
                    "predicted_demand": random.randint(25, 60)
                }
            ],
            "deliveries": [
                {
                    "driver_id": "driver_001",
                    "status": "in_transit",
                    "estimated_arrival": "2 hours"
                }
            ],
            "market_conditions": {
                "weather": random.choice(["sunny", "rainy", "cloudy"]),
                "events": random.choice(["none", "local_festival", "sports_event"]),
                "traffic": random.choice(["normal", "heavy", "light"])
            }
        }

    async def _generate_decision(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a decision based on context"""
        # Analyze context and determine what action to take
        action_type = await self._analyze_context_and_decide(context)
        
        if not action_type:
            return None
            
        # Generate decision parameters
        parameters = await self._generate_action_parameters(action_type, context)
        
        # Create decision object
        decision = {
            "decision_id": f"decision_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
            "action_type": action_type,
            "parameters": parameters,
            "reasoning": await self._generate_reasoning(action_type, context),
            "confidence": random.uniform(0.7, 0.95),
            "estimated_impact": await self._estimate_impact(action_type, parameters),
            "approval_required": True,
            "approval_status": "pending",
            "timestamp": datetime.utcnow().isoformat(),
            "executed": False
        }
        
        return decision

    async def _analyze_context_and_decide(self, context: Dict[str, Any]) -> str:
        """Analyze context and decide what action to take"""
        # Simple decision logic - in practice, this would use AI/ML
        inventory = context.get("inventory", [])
        
        # Check for low inventory
        for item in inventory:
            if item["quantity"] < item["reorder_threshold"]:
                return "restock"
        
        # Check for high demand forecast
        demand_forecast = context.get("demand_forecast", [])
        for forecast in demand_forecast:
            if forecast["predicted_demand"] > 50:
                return "restock"
        
        # Randomly choose other actions
        actions = ["pricing", "route", "dispatch", "forecasting"]
        return random.choice(actions)

    async def _generate_action_parameters(self, action_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate parameters for the action"""
        if action_type == "restock":
            return {
                "supplier_id": f"supplier_{random.randint(1, 5)}",
                "sku_id": f"sku_{random.randint(1, 10)}",
                "quantity": random.randint(50, 200),
                "priority": random.choice(["normal", "high"]),
                "expected_delivery_date": (datetime.utcnow() + timedelta(days=random.randint(1, 7))).strftime("%Y-%m-%d")
            }
        elif action_type == "pricing":
            return {
                "sku_id": f"sku_{random.randint(1, 10)}",
                "new_price": round(random.uniform(10.0, 100.0), 2),
                "reason": "Demand-based price adjustment"
            }
        elif action_type == "route":
            return {
                "driver_id": f"driver_{random.randint(1, 10)}",
                "new_route": [f"stop_{i}" for i in range(1, random.randint(3, 6))],
                "reason": "Traffic optimization",
                "priority": "normal"
            }
        elif action_type == "dispatch":
            return {
                "vehicle_ids": [f"vehicle_{i}" for i in range(1, random.randint(2, 4))],
                "route_id": f"route_{random.randint(1, 5)}",
                "priority": "normal"
            }
        else:
            return {
                "forecast_horizon": 24,
                "confidence_threshold": 0.8
            }

    async def _generate_reasoning(self, action_type: str, context: Dict[str, Any]) -> str:
        """Generate reasoning for the decision"""
        reasoning_templates = {
            "restock": "Low inventory detected. Current stock levels are below reorder threshold, risking stockout. Recommend immediate restock to maintain service levels.",
            "pricing": "Demand forecast indicates potential price sensitivity. Adjusting pricing to optimize revenue while maintaining competitive position.",
            "route": "Traffic conditions and delivery windows suggest route optimization opportunity. Rerouting to improve delivery efficiency.",
            "dispatch": "Available vehicles and pending orders indicate dispatch opportunity. Assigning vehicles to optimize fleet utilization.",
            "forecasting": "Market conditions changing. Updating demand forecasts to improve inventory planning accuracy."
        }
        return reasoning_templates.get(action_type, "Autonomous decision based on system analysis.")

    async def _estimate_impact(self, action_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate the impact of the action"""
        return {
            "cost": random.randint(100, 1000),
            "time_saved": f"{random.randint(5, 30)} minutes",
            "efficiency_gain": f"{random.randint(5, 20)}%",
            "risk_level": random.choice(["low", "medium", "high"])
        }

    async def _execute_action(self, action: str, parameters: dict):
        """Execute a specific action (for manual triggers)"""
        task_type = parameters.get("task_type")
        logger.info(f"UniversalAgent executing action: {action}, task_type={task_type}, params={parameters}")
        
        if task_type == "dispatch":
            return await self._handle_dispatch(parameters)
        elif task_type == "restock":
            return await self._handle_restock(parameters)
        elif task_type == "pricing":
            return await self._handle_pricing(parameters)
        elif task_type == "route":
            return await self._handle_route(parameters)
        elif task_type == "forecasting":
            return await self._handle_forecasting(parameters)
        else:
            return {"status": "unknown_task_type", "task_type": task_type, "parameters": parameters}

    async def _handle_dispatch(self, parameters):
        logger.info("Handling dispatch task", params=parameters)
        return {"status": "dispatched", "details": parameters}

    async def _handle_restock(self, parameters):
        logger.info("Handling restock task", params=parameters)
        return {"status": "restocked", "details": parameters}

    async def _handle_pricing(self, parameters):
        logger.info("Handling pricing task", params=parameters)
        return {"status": "priced", "details": parameters}

    async def _handle_route(self, parameters):
        logger.info("Handling route task", params=parameters)
        return {"status": "routed", "details": parameters}

    async def _handle_forecasting(self, parameters):
        logger.info("Handling forecasting task", params=parameters)
        return {"status": "forecasted", "details": parameters}

    def get_pending_decisions(self) -> List[Dict[str, Any]]:
        """Get all pending decisions requiring approval"""
        return [d for d in self.pending_decisions if d["approval_status"] == "pending"]

    def get_decision_history(self) -> List[Dict[str, Any]]:
        """Get all decision history"""
        return self.decision_history

    async def approve_decision(self, decision_id: str) -> Dict[str, Any]:
        """Approve a pending decision"""
        decision = next((d for d in self.pending_decisions if d["decision_id"] == decision_id), None)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        
        decision["approval_status"] = "approved"
        decision["executed"] = True
        decision["execution_timestamp"] = datetime.utcnow().isoformat()
        
        # Execute the decision
        result = await self._execute_decision(decision)
        decision["execution_result"] = result
        
        return {
            "decision_id": decision_id,
            "status": "approved",
            "execution_result": result
        }

    async def decline_decision(self, decision_id: str) -> bool:
        """Decline a pending decision"""
        decision = next((d for d in self.pending_decisions if d["decision_id"] == decision_id), None)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        
        decision["approval_status"] = "denied"
        decision["executed"] = False
        
        return True

    async def _execute_decision(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an approved decision"""
        try:
            action_type = decision["action_type"]
            parameters = decision["parameters"]
            
            # Execute based on action type
            if action_type == "restock":
                return await self._handle_restock(parameters)
            elif action_type == "pricing":
                return await self._handle_pricing(parameters)
            elif action_type == "route":
                return await self._handle_route(parameters)
            elif action_type == "dispatch":
                return await self._handle_dispatch(parameters)
            elif action_type == "forecasting":
                return await self._handle_forecasting(parameters)
            else:
                return {"status": "unknown_action_type", "action_type": action_type}
                
        except Exception as e:
            logger.error(f"Error executing decision {decision['decision_id']}: {str(e)}")
            return {"status": "error", "error": str(e)} 