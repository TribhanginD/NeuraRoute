"""
Agentic AI System for NeuraRoute
Provides autonomous decision-making and action-taking capabilities using LangChain agents
"""

import asyncio
import structlog
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.ai.model_manager import get_ai_model_manager
from app.core.database import get_db
from app.models.agents import AgentLog, AgentStatus
from app.core.config import settings

logger = structlog.get_logger()

class ActionType(str, Enum):
    """Types of actions the agent can take"""
    PLACE_ORDER = "place_order"
    REROUTE_DRIVER = "reroute_driver"
    UPDATE_INVENTORY = "update_inventory"
    ADJUST_PRICING = "adjust_pricing"
    DISPATCH_FLEET = "dispatch_fleet"
    FORECAST_DEMAND = "forecast_demand"
    ANALYZE_PERFORMANCE = "analyze_performance"

class ApprovalStatus(str, Enum):
    """Approval status for agent actions"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    AUTO_APPROVED = "auto_approved"

@dataclass
class AgentAction:
    """Represents an action taken by the agentic system"""
    action_id: str
    action_type: ActionType
    parameters: Dict[str, Any]
    reasoning: str
    confidence: float
    estimated_impact: Dict[str, Any]
    approval_required: bool
    approval_status: ApprovalStatus
    timestamp: datetime
    executed: bool = False
    execution_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class PlaceOrderInput(BaseModel):
    """Input schema for place_order tool"""
    supplier_id: str = Field(..., description="ID of the supplier to order from")
    sku_id: str = Field(..., description="ID of the SKU to order")
    quantity: int = Field(..., description="Quantity to order", gt=0)
    priority: str = Field(default="normal", description="Order priority: low, normal, high, urgent")
    expected_delivery_date: Optional[str] = Field(None, description="Expected delivery date (YYYY-MM-DD)")

class RerouteDriverInput(BaseModel):
    """Input schema for reroute_driver tool"""
    driver_id: str = Field(..., description="ID of the driver to reroute")
    new_route: List[str] = Field(..., description="List of stop IDs in new order")
    reason: str = Field(..., description="Reason for rerouting")
    priority: str = Field(default="normal", description="Reroute priority: low, normal, high, urgent")

class UpdateInventoryInput(BaseModel):
    """Input schema for update_inventory tool"""
    store_id: str = Field(..., description="ID of the store")
    sku_id: str = Field(..., description="ID of the SKU")
    new_quantity: int = Field(..., description="New quantity to set")
    reason: str = Field(..., description="Reason for inventory update")

class AdjustPricingInput(BaseModel):
    """Input schema for adjust_pricing tool"""
    sku_id: str = Field(..., description="ID of the SKU")
    new_price: float = Field(..., description="New price to set", gt=0)
    store_id: Optional[str] = Field(None, description="Specific store ID (if None, applies to all stores)")
    reason: str = Field(..., description="Reason for price adjustment")

class DispatchFleetInput(BaseModel):
    """Input schema for dispatch_fleet tool"""
    vehicle_ids: List[str] = Field(..., description="List of vehicle IDs to dispatch")
    route_id: str = Field(..., description="ID of the route to assign")
    priority: str = Field(default="normal", description="Dispatch priority: low, normal, high, urgent")

class AgenticTool:
    """Base class for agentic tools with approval workflow"""
    
    approval_threshold: float = Field(default=1000.0, description="Threshold for requiring approval")
    action_history: List[AgentAction] = Field(default_factory=list, description="History of actions taken by this tool")
    
    def __init__(self, name: str, description: str, approval_threshold: float = 1000.0):
        self.name = name
        self.approval_threshold = approval_threshold
        self.action_history: List[AgentAction] = []
    
    async def _arun(self, *args, **kwargs) -> str:
        """Async execution with approval workflow"""
        # Create action record
        action = AgentAction(
            action_id=f"{self.name}_{datetime.utcnow().isoformat()}",
            action_type=ActionType(self.name),
            parameters=kwargs,
            reasoning="",  # Will be filled by agent
            confidence=0.0,  # Will be filled by agent
            estimated_impact={},
            approval_required=self._requires_approval(kwargs),
            approval_status=ApprovalStatus.PENDING,
            timestamp=datetime.utcnow()
        )
        
        # Check if auto-approval is possible
        if not action.approval_required:
            action.approval_status = ApprovalStatus.AUTO_APPROVED
            return await self._execute_action(action)
        else:
            # Store for manual approval
            self.action_history.append(action)
            return f"Action requires approval. Action ID: {action.action_id}"
    
    def _requires_approval(self, parameters: Dict[str, Any]) -> bool:
        """Check if action requires manual approval"""
        # Override in subclasses for specific logic
        return False
    
    async def _execute_action(self, action: AgentAction) -> str:
        """Execute the actual action"""
        try:
            # This will be implemented by subclasses
            result = await self._perform_action(action.parameters)
            action.executed = True
            action.execution_result = result
            return f"Action executed successfully: {result}"
        except Exception as e:
            action.executed = True
            action.error_message = str(e)
            return f"Action failed: {str(e)}"

class PlaceOrderTool(AgenticTool):
    """Tool for placing orders with suppliers"""
    
    def __init__(self):
        super().__init__(
            name="place_order",
            description="Place an order with a supplier for inventory restocking",
            approval_threshold=1000.0
        )
    
    def _run(self, *args, **kwargs) -> str:
        """Sync execution - delegate to async version"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._arun(*args, **kwargs))
        except RuntimeError:
            # If no event loop, create one
            return asyncio.run(self._arun(*args, **kwargs))
    
    def _requires_approval(self, parameters: Dict[str, Any]) -> bool:
        """Require approval for orders over threshold"""
        # This would need to calculate total order value
        # For now, use quantity as proxy
        quantity = parameters.get('quantity', 0)
        return quantity > 100  # Approve orders over 100 units
    
    async def _perform_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Actually place the order"""
        # This would integrate with your existing order system
        # For now, return mock result
        return {
            "order_id": f"ORD_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "supplier_id": parameters['supplier_id'],
            "sku_id": parameters['sku_id'],
            "quantity": parameters['quantity'],
            "status": "confirmed",
            "estimated_delivery": parameters.get('expected_delivery_date')
        }

class RerouteDriverTool(AgenticTool):
    """Tool for rerouting drivers"""
    
    def __init__(self):
        super().__init__(
            name="reroute_driver",
            description="Reroute a driver to optimize delivery efficiency",
            approval_threshold=500.0
        )
    
    def _run(self, *args, **kwargs) -> str:
        """Sync execution - delegate to async version"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._arun(*args, **kwargs))
        except RuntimeError:
            # If no event loop, create one
            return asyncio.run(self._arun(*args, **kwargs))
    
    def _requires_approval(self, parameters: Dict[str, Any]) -> bool:
        """Require approval for high-priority reroutes"""
        priority = parameters.get('priority', 'normal')
        return priority in ['high', 'urgent']
    
    async def _perform_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Actually reroute the driver"""
        return {
            "driver_id": parameters['driver_id'],
            "new_route": parameters['new_route'],
            "status": "rerouted",
            "estimated_time_saved": "15 minutes"
        }

class UpdateInventoryTool(AgenticTool):
    """Tool for updating inventory levels"""
    
    def __init__(self):
        super().__init__(
            name="update_inventory",
            description="Update inventory levels at stores",
            approval_threshold=2000.0
        )
    
    def _run(self, *args, **kwargs) -> str:
        """Sync execution - delegate to async version"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._arun(*args, **kwargs))
        except RuntimeError:
            # If no event loop, create one
            return asyncio.run(self._arun(*args, **kwargs))
    
    def _requires_approval(self, parameters: Dict[str, Any]) -> bool:
        """Require approval for large inventory changes"""
        quantity = abs(parameters.get('new_quantity', 0))
        return quantity > 500
    
    async def _perform_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Actually update inventory"""
        return {
            "store_id": parameters['store_id'],
            "sku_id": parameters['sku_id'],
            "new_quantity": parameters['new_quantity'],
            "status": "updated"
        }

class AdjustPricingTool(AgenticTool):
    """Tool for adjusting pricing"""
    
    def __init__(self):
        super().__init__(
            name="adjust_pricing",
            description="Adjust pricing based on demand and market conditions",
            approval_threshold=500.0
        )
    
    def _run(self, *args, **kwargs) -> str:
        """Sync execution - delegate to async version"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._arun(*args, **kwargs))
        except RuntimeError:
            # If no event loop, create one
            return asyncio.run(self._arun(*args, **kwargs))
    
    def _requires_approval(self, parameters: Dict[str, Any]) -> bool:
        """Require approval for significant price changes"""
        # This would need current price to calculate percentage change
        return True  # Always require approval for pricing changes
    
    async def _perform_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Actually adjust pricing"""
        return {
            "sku_id": parameters['sku_id'],
            "new_price": parameters['new_price'],
            "store_id": parameters.get('store_id'),
            "status": "price_updated"
        }

class DispatchFleetTool(AgenticTool):
    """Tool for dispatching fleet vehicles"""
    
    def __init__(self):
        super().__init__(
            name="dispatch_fleet",
            description="Dispatch fleet vehicles for deliveries",
            approval_threshold=300.0
        )
    
    def _run(self, *args, **kwargs) -> str:
        """Sync execution - delegate to async version"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._arun(*args, **kwargs))
        except RuntimeError:
            # If no event loop, create one
            return asyncio.run(self._arun(*args, **kwargs))
    
    def _requires_approval(self, parameters: Dict[str, Any]) -> bool:
        """Require approval for urgent dispatches"""
        priority = parameters.get('priority', 'normal')
        return priority == 'urgent'
    
    async def _perform_action(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Actually dispatch fleet"""
        return {
            "vehicle_ids": parameters['vehicle_ids'],
            "route_id": parameters['route_id'],
            "status": "dispatched"
        }

class AgenticSystem:
    """Main agentic system that orchestrates autonomous decision-making"""
    
    def __init__(self):
        self.ai_manager = None
        self.agent_executor = None
        self.tools: List[AgenticTool] = []
        self.simulation_mode = False
        self.action_queue: List[AgentAction] = []
        self.approved_actions: List[AgentAction] = []
        self.denied_actions: List[AgentAction] = []
        
        # System prompt for the agent
        self.system_prompt = """You are an intelligent logistics operations agent for NeuraRoute, a hyperlocal logistics system.

Your mission is to keep merchants well-stocked and deliveries on time, by predicting demand spikes and autonomously placing orders or rerouting drivers.

Key responsibilities:
1. Monitor inventory levels and place restock orders before stockouts
2. Optimize delivery routes based on real-time conditions
3. Adjust pricing based on demand forecasts and market conditions
4. Dispatch fleet vehicles efficiently
5. Analyze performance and make proactive improvements

Decision-making guidelines:
- Always consider the impact on customer satisfaction and operational efficiency
- Prioritize actions that prevent stockouts and delivery delays
- Use demand forecasts to make proactive decisions
- Consider cost implications and seek approval for high-value actions
- Explain your reasoning clearly for each action

Available tools:
- place_order: Order inventory from suppliers
- reroute_driver: Optimize delivery routes
- update_inventory: Update inventory levels
- adjust_pricing: Modify pricing based on demand
- dispatch_fleet: Assign vehicles to routes

Always provide clear reasoning for your decisions and consider the broader impact on the logistics network."""

    async def initialize(self):
        """Initialize the agentic system"""
        logger.info("Initializing Agentic System")
        
        # Initialize AI model manager
        self.ai_manager = await get_ai_model_manager()
        
        # Initialize tools
        self._initialize_tools()
        
        # Create agent
        await self._create_agent()
        
        logger.info("Agentic System initialized successfully")
    
    def _initialize_tools(self):
        """Initialize all available tools"""
        self.tools = [
            PlaceOrderTool(),
            RerouteDriverTool(),
            UpdateInventoryTool(),
            AdjustPricingTool(),
            DispatchFleetTool()
        ]
        logger.info(f"Initialized {len(self.tools)} tools")
    
    async def _create_agent(self):
        """Create the agentic system"""
        try:
            # Get the LLM from the default provider
            default_provider = self.ai_manager.get_default_provider()
            if not default_provider or not default_provider.client:
                raise ValueError("No default AI provider available")
            llm = default_provider.client
            # Use a simple prompt and direct LLM call instead of LLMChain
            self.llm = llm
            self.prompt_template = self.system_prompt + "\n\nContext: {context}\n\nBased on this information, provide recommendations for logistics optimization."
            logger.info("Agentic system initialized with direct LLM call")
        except Exception as e:
            logger.error(f"Failed to create agentic system: {str(e)}")
            raise
    
    async def process_situation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a situation and generate autonomous actions"""
        try:
            # Build context prompt
            context_prompt = self._build_context_prompt(context)
            # Run LLM directly
            prompt = self.prompt_template.format(context=context_prompt)
            result = await self.llm.ainvoke(prompt)
            return {
                "reasoning": result.get("text", "") if isinstance(result, dict) else str(result),
                "actions": [],  # No actions for now, just recommendations
                "confidence": self._calculate_confidence(result),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error processing situation: {str(e)}")
            raise
    
    def _build_context_prompt(self, context: Dict[str, Any]) -> str:
        """Build a context prompt from the situation data"""
        prompt_parts = []
        
        # Add inventory status
        if 'inventory' in context:
            prompt_parts.append("INVENTORY STATUS:")
            for item in context['inventory']:
                prompt_parts.append(f"- {item['sku_name']}: {item['quantity']} units (threshold: {item['reorder_threshold']})")
        
        # Add demand forecasts
        if 'demand_forecast' in context:
            prompt_parts.append("\nDEMAND FORECAST:")
            for forecast in context['demand_forecast']:
                prompt_parts.append(f"- {forecast['sku_name']}: {forecast['predicted_demand']} units in next 24h")
        
        # Add delivery status
        if 'deliveries' in context:
            prompt_parts.append("\nDELIVERY STATUS:")
            for delivery in context['deliveries']:
                prompt_parts.append(f"- Driver {delivery['driver_id']}: {delivery['status']} - {delivery['estimated_arrival']}")
        
        # Add market conditions
        if 'market_conditions' in context:
            prompt_parts.append("\nMARKET CONDITIONS:")
            conditions = context['market_conditions']
            prompt_parts.append(f"- Weather: {conditions.get('weather', 'Unknown')}")
            prompt_parts.append(f"- Events: {conditions.get('events', 'None')}")
            prompt_parts.append(f"- Traffic: {conditions.get('traffic', 'Normal')}")
        
        # Add the main question
        prompt_parts.append("\nBased on this information, what actions should be taken to optimize logistics operations?")
        
        return "\n".join(prompt_parts)
    
    async def _process_actions(self, actions: List[AgentAction]) -> List[Dict[str, Any]]:
        """Process and categorize actions"""
        processed = []
        
        for action in actions:
            # Skip if already processed
            if action in self.approved_actions or action in self.denied_actions:
                continue
            
            # Add to appropriate queue
            if action.approval_status == ApprovalStatus.AUTO_APPROVED:
                self.approved_actions.append(action)
            else:
                self.action_queue.append(action)
            
            processed.append({
                "action_id": action.action_id,
                "action_type": action.action_type.value,
                "parameters": action.parameters,
                "reasoning": action.reasoning,
                "confidence": action.confidence,
                "approval_required": action.approval_required,
                "approval_status": action.approval_status.value,
                "timestamp": action.timestamp.isoformat()
            })
        
        return processed
    
    def _calculate_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score for the agent's decisions"""
        # This is a simplified confidence calculation
        # In practice, you might use model confidence scores or other metrics
        return 0.85  # Placeholder
    
    async def approve_action(self, action_id: str) -> Dict[str, Any]:
        """Approve a pending action"""
        action = next((a for a in self.action_queue if a.action_id == action_id), None)
        if not action:
            raise ValueError(f"Action {action_id} not found in queue")
        
        action.approval_status = ApprovalStatus.APPROVED
        self.action_queue.remove(action)
        self.approved_actions.append(action)
        
        # Execute the action
        result = await self._execute_approved_action(action)
        
        return {
            "action_id": action_id,
            "status": "approved",
            "execution_result": result
        }
    
    async def deny_action(self, action_id: str) -> bool:
        """Deny a pending action"""
        action = next((a for a in self.action_queue if a.action_id == action_id), None)
        if not action:
            raise ValueError(f"Action {action_id} not found in queue")
        
        action.approval_status = ApprovalStatus.DENIED
        self.action_queue.remove(action)
        self.denied_actions.append(action)
        
        return True
    
    async def _execute_approved_action(self, action: AgentAction) -> Dict[str, Any]:
        """Execute an approved action"""
        try:
            # Find the appropriate tool
            tool = next((t for t in self.tools if t.name == action.action_type.value), None)
            if not tool:
                raise ValueError(f"No tool found for action type {action.action_type}")
            
            # Execute the action
            result = await tool._execute_action(action)
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Error executing action {action.action_id}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_pending_actions(self) -> List[Dict[str, Any]]:
        """Get all pending actions requiring approval"""
        return [
            {
                "action_id": action.action_id,
                "action_type": action.action_type.value,
                "parameters": action.parameters,
                "reasoning": action.reasoning,
                "confidence": action.confidence,
                "timestamp": action.timestamp.isoformat()
            }
            for action in self.action_queue
        ]
    
    def get_action_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get action history by status"""
        return {
            "pending": self.get_pending_actions(),
            "approved": [
                {
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "parameters": action.parameters,
                    "execution_result": action.execution_result,
                    "timestamp": action.timestamp.isoformat()
                }
                for action in self.approved_actions
            ],
            "denied": [
                {
                    "action_id": action.action_id,
                    "action_type": action.action_type.value,
                    "parameters": action.parameters,
                    "timestamp": action.timestamp.isoformat()
                }
                for action in self.denied_actions
            ]
        }
    
    def set_simulation_mode(self, enabled: bool):
        """Enable or disable simulation mode"""
        self.simulation_mode = enabled
        logger.info(f"Simulation mode {'enabled' if enabled else 'disabled'}")

# Global instance
_agentic_system = None

async def get_agentic_system() -> AgenticSystem:
    """Get the global agentic system instance"""
    global _agentic_system
    if _agentic_system is None:
        _agentic_system = AgenticSystem()
        await _agentic_system.initialize()
    return _agentic_system
