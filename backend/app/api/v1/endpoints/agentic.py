"""
Agentic AI API endpoints for NeuraRoute
Handles autonomous decision-making and action approval workflows
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime
import json
import asyncio
from collections import defaultdict

from app.core.database import get_db
from app.ai.agentic_system import get_agentic_system, ActionType, ApprovalStatus
from app.simulation.agentic_simulation import get_simulation_engine
from app.models.agents import AgentLog

logger = structlog.get_logger()
router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_subscriptions: Dict[WebSocket, List[str]] = defaultdict(list)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.connection_subscriptions:
            del self.connection_subscriptions[websocket]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    def subscribe(self, websocket: WebSocket, event_type: str):
        self.connection_subscriptions[websocket].append(event_type)

    async def broadcast(self, message: Dict[str, Any], event_type: str = "general"):
        """Broadcast message to all subscribed connections"""
        if not self.active_connections:
            return
        
        message_data = {
            "type": event_type,
            "data": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        disconnected = []
        for connection in self.active_connections:
            try:
                if event_type in self.connection_subscriptions[connection] or "all" in self.connection_subscriptions[connection]:
                    await connection.send_text(json.dumps(message_data))
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

# Global connection manager
manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time agentic updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Handle incoming messages (subscriptions, etc.)
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "subscribe":
                    event_types = message.get("events", ["all"])
                    for event_type in event_types:
                        manager.subscribe(websocket, event_type)
                    await websocket.send_text(json.dumps({
                        "type": "subscription_confirmed",
                        "events": event_types,
                        "timestamp": datetime.utcnow().isoformat()
                    }))
            except json.JSONDecodeError:
                logger.warning("Invalid JSON received via WebSocket")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/process-situation")
async def process_situation(
    context: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """
    Process a situation and generate autonomous actions
    
    Context should include:
    - inventory: List of inventory items with quantities and thresholds
    - demand_forecast: List of demand predictions
    - deliveries: List of delivery statuses
    - market_conditions: Weather, events, traffic info
    """
    try:
        agentic_system = await get_agentic_system()
        
        # Process the situation asynchronously
        result = await agentic_system.process_situation(context)
        
        # Broadcast the result via WebSocket
        await manager.broadcast({
            "reasoning": result["reasoning"],
            "actions": result["actions"],
            "confidence": result["confidence"],
            "timestamp": result["timestamp"],
            "pending_approvals": len(agentic_system.get_pending_actions())
        }, "situation_processed")
        
        return {
            "success": True,
            "reasoning": result["reasoning"],
            "actions": result["actions"],
            "confidence": result["confidence"],
            "timestamp": result["timestamp"],
            "pending_approvals": len(agentic_system.get_pending_actions())
        }
        
    except Exception as e:
        logger.error(f"Error processing situation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-actions")
async def get_pending_actions():
    """Get all pending actions requiring approval"""
    try:
        agentic_system = await get_agentic_system()
        actions = agentic_system.get_pending_actions()
        
        return {
            "actions": actions,
            "count": len(actions)
        }
        
    except Exception as e:
        logger.error(f"Error getting pending actions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/actions/{action_id}/approve")
async def approve_action(action_id: str):
    """Approve a pending action"""
    try:
        agentic_system = await get_agentic_system()
        result = await agentic_system.approve_action(action_id)
        
        # Broadcast approval event
        await manager.broadcast({
            "action_id": action_id,
            "status": "approved",
            "execution_result": result.get("execution_result"),
            "pending_actions": len(agentic_system.get_pending_actions())
        }, "action_approved")
        
        return {
            "success": True,
            "action_id": action_id,
            "status": "approved",
            "execution_result": result.get("execution_result")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error approving action {action_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/actions/{action_id}/deny")
async def deny_action(action_id: str):
    """Deny a pending action"""
    try:
        agentic_system = await get_agentic_system()
        success = await agentic_system.deny_action(action_id)
        
        # Broadcast denial event
        await manager.broadcast({
            "action_id": action_id,
            "status": "denied",
            "pending_actions": len(agentic_system.get_pending_actions())
        }, "action_denied")
        
        return {
            "success": success,
            "action_id": action_id,
            "status": "denied"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error denying action {action_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/action-history")
async def get_action_history():
    """Get complete action history by status"""
    try:
        agentic_system = await get_agentic_system()
        history = agentic_system.get_action_history()
        
        return {
            "history": history,
            "summary": {
                "pending": len(history["pending"]),
                "approved": len(history["approved"]),
                "denied": len(history["denied"])
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting action history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent-plan")
async def get_agent_plan():
    """Get the current agent's plan and reasoning"""
    try:
        agentic_system = await get_agentic_system()
        
        # Get the latest reasoning from memory
        memory_messages = []
        if agentic_system.memory and agentic_system.memory.chat_memory:
            memory_messages = agentic_system.memory.chat_memory.messages
        
        # Get recent actions for context
        recent_actions = agentic_system.get_action_history()
        
        plan = {
            "current_reasoning": memory_messages[-1].content if memory_messages else "No recent reasoning available",
            "memory_size": len(memory_messages),
            "recent_actions": {
                "pending": len(recent_actions["pending"]),
                "approved": len(recent_actions["approved"]),
                "denied": len(recent_actions["denied"])
            },
            "tools_available": len(agentic_system.tools),
            "simulation_mode": agentic_system.simulation_mode
        }
        
        return plan
        
    except Exception as e:
        logger.error(f"Error getting agent plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulation-mode")
async def set_simulation_mode(enabled: bool):
    """Enable or disable simulation mode"""
    try:
        agentic_system = await get_agentic_system()
        agentic_system.set_simulation_mode(enabled)
        
        # Broadcast simulation mode change
        await manager.broadcast({
            "simulation_mode": enabled,
            "message": f"Simulation mode {'enabled' if enabled else 'disabled'}"
        }, "simulation_mode_changed")
        
        return {
            "success": True,
            "simulation_mode": enabled,
            "message": f"Simulation mode {'enabled' if enabled else 'disabled'}"
        }
        
    except Exception as e:
        logger.error(f"Error setting simulation mode: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_agentic_status():
    """Get the current status of the agentic system"""
    try:
        agentic_system = await get_agentic_system()
        
        status = {
            "status": "active",
            "simulation_mode": agentic_system.simulation_mode,
            "tools_available": len(agentic_system.tools),
            "pending_actions": len(agentic_system.get_pending_actions()),
            "approved_actions": len(agentic_system.approved_actions),
            "denied_actions": len(agentic_system.denied_actions),
            "memory_size": len(agentic_system.memory.chat_memory.messages) if agentic_system.memory.chat_memory else 0
        }
        
        # Broadcast status update
        await manager.broadcast(status, "status_update")
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting agentic status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tools/{tool_name}/execute")
async def execute_tool_directly(
    tool_name: str,
    parameters: Dict[str, Any]
):
    """Execute a tool directly (for testing/debugging)"""
    try:
        agentic_system = await get_agentic_system()
        
        # Find the tool
        tool = next((t for t in agentic_system.tools if t.name == tool_name), None)
        if not tool:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
        
        # Execute the tool
        result = await tool._arun(**parameters)
        
        return {
            "success": True,
            "tool_name": tool_name,
            "parameters": parameters,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tools")
async def get_available_tools():
    """Get list of available tools with their descriptions"""
    try:
        agentic_system = await get_agentic_system()
        
        tools = []
        for tool in agentic_system.tools:
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "approval_threshold": tool.approval_threshold
            })
        
        return {
            "tools": tools,
            "count": len(tools)
        }
        
    except Exception as e:
        logger.error(f"Error getting available tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_agentic_system():
    """Reset the agentic system (clear memory, actions, etc.)"""
    try:
        agentic_system = await get_agentic_system()
        
        # Clear action queues
        agentic_system.action_queue.clear()
        agentic_system.approved_actions.clear()
        agentic_system.denied_actions.clear()
        
        # Clear tool action histories
        for tool in agentic_system.tools:
            tool.action_history.clear()
        
        # Clear memory
        if agentic_system.memory.chat_memory:
            agentic_system.memory.chat_memory.clear()
        
        return {
            "success": True,
            "message": "Agentic system reset successfully"
        }
        
    except Exception as e:
        logger.error(f"Error resetting agentic system: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/demo/market-day")
async def simulate_market_day():
    """Simulate a full market day with sample data"""
    try:
        agentic_system = await get_agentic_system()
        
        # Sample market day context
        sample_context = {
            "inventory": [
                {
                    "sku_name": "Fresh Bread",
                    "quantity": 15,
                    "reorder_threshold": 20
                },
                {
                    "sku_name": "Milk",
                    "quantity": 8,
                    "reorder_threshold": 25
                },
                {
                    "sku_name": "Eggs",
                    "quantity": 45,
                    "reorder_threshold": 30
                }
            ],
            "demand_forecast": [
                {
                    "sku_name": "Fresh Bread",
                    "predicted_demand": 35
                },
                {
                    "sku_name": "Milk",
                    "predicted_demand": 28
                },
                {
                    "sku_name": "Eggs",
                    "predicted_demand": 22
                }
            ],
            "deliveries": [
                {
                    "driver_id": "DRV_001",
                    "status": "in_transit",
                    "estimated_arrival": "14:30"
                },
                {
                    "driver_id": "DRV_002",
                    "status": "loading",
                    "estimated_arrival": "15:45"
                }
            ],
            "market_conditions": {
                "weather": "Sunny",
                "events": "Local farmers market",
                "traffic": "Moderate"
            }
        }
        
        # Process the situation
        result = await agentic_system.process_situation(sample_context)
        
        return {
            "success": True,
            "demo_data": sample_context,
            "agent_response": result,
            "message": "Market day simulation completed"
        }
        
    except Exception as e:
        logger.error(f"Error simulating market day: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Simulation endpoints
@router.get("/simulation/scenarios")
async def get_simulation_scenarios():
    """Get available simulation scenarios"""
    try:
        simulation_engine = await get_simulation_engine()
        scenarios = simulation_engine.get_available_scenarios()
        
        return {
            "scenarios": scenarios,
            "count": len(scenarios)
        }
        
    except Exception as e:
        logger.error(f"Error getting simulation scenarios: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulation/start")
async def start_simulation(scenario_name: str, speed: float = 1.0):
    """Start a simulation with the specified scenario"""
    try:
        simulation_engine = await get_simulation_engine()
        result = await simulation_engine.start_simulation(scenario_name, speed)
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulation/step")
async def run_simulation_step():
    """Run one step of the current simulation"""
    try:
        simulation_engine = await get_simulation_engine()
        result = await simulation_engine.run_simulation_step()
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error running simulation step: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulation/stop")
async def stop_simulation():
    """Stop the current simulation"""
    try:
        simulation_engine = await get_simulation_engine()
        result = await simulation_engine.stop_simulation()
        
        return result
        
    except Exception as e:
        logger.error(f"Error stopping simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simulation/status")
async def get_simulation_status():
    """Get the current simulation status"""
    try:
        simulation_engine = await get_simulation_engine()
        stats = simulation_engine.get_simulation_stats()
        
        return {
            "simulation": stats,
            "available_scenarios": len(simulation_engine.scenarios)
        }
        
    except Exception as e:
        logger.error(f"Error getting simulation status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/simulation/log")
async def get_simulation_log(limit: int = 100):
    """Get simulation log entries"""
    try:
        simulation_engine = await get_simulation_engine()
        log_entries = simulation_engine.get_simulation_log(limit)
        
        return {
            "log_entries": log_entries,
            "count": len(log_entries)
        }
        
    except Exception as e:
        logger.error(f"Error getting simulation log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulation/auto-run")
async def auto_run_simulation(scenario_name: str, speed: float = 1.0):
    """Automatically run a complete simulation"""
    try:
        simulation_engine = await get_simulation_engine()
        
        # Start simulation
        start_result = await simulation_engine.start_simulation(scenario_name, speed)
        
        # Run steps until completion
        steps = []
        while simulation_engine.is_running:
            step_result = await simulation_engine.run_simulation_step()
            steps.append(step_result)
            
            if step_result.get("simulation_ended", False):
                break
        
        # Get final stats
        final_stats = simulation_engine.get_simulation_stats()
        
        return {
            "success": True,
            "start_result": start_result,
            "steps": steps,
            "final_stats": final_stats,
            "total_steps": len(steps)
        }
        
    except Exception as e:
        logger.error(f"Error auto-running simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 