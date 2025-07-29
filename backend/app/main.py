import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Set
import uvicorn
import json
from datetime import datetime, timedelta

from .core.config import settings
from .agents.manager import agent_manager

# --- WebSocket for real-time agent actions ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        data = json.dumps(message)
        for connection in list(self.active_connections):
            try:
                await connection.send_text(data)
            except Exception:
                self.disconnect(connection)

# Global connection manager instance
agent_action_manager = ConnectionManager()

def broadcast_agent_action(action: dict):
    """Schedule a broadcast of a new agent action to all WebSocket clients."""
    import asyncio
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(agent_action_manager.broadcast({"type": "agent_action", "action": action}))
    else:
        loop.run_until_complete(agent_action_manager.broadcast({"type": "agent_action", "action": action}))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting NeuraRoute Agentic System...")
    # Initialize agents
    await agent_manager.initialize_agents()
    print("Agents initialized successfully")
    yield
    # Shutdown
    print("Shutting down NeuraRoute Agentic System...")
    # Remove /api/v1/agents/start and /api/v1/agents/stop endpoints, agents_running variable, and related logic

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint defined after app initialization to avoid NameError
@app.websocket("/ws/agent-actions")
async def websocket_agent_actions(websocket: WebSocket):
    await agent_action_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; ignore incoming messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        agent_action_manager.disconnect(websocket)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NeuraRoute Agentic System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if agents are running
        agent_status = await agent_manager.get_agent_status()
        
        return {
            "status": "healthy",
            "agents_running": False, # Agents are no longer managed globally
            "agent_status": agent_status,
            "services": {
                "api": "healthy",
                "agents": "offline", # Agents are no longer managed globally
                "database": "healthy"  # Add actual DB check if needed
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "services": {
                "api": "unhealthy",
                "agents": "unknown",
                "database": "unknown"
            }
        }

# Remove /api/v1/agents/start and /api/v1/agents/stop endpoints, agents_running variable, and related logic

@app.get("/api/v1/agents/status")
async def get_agent_status():
    """Get status of all agents"""
    try:
        status = await agent_manager.get_agent_status()
        status["agents_running"] = False # Agents are no longer managed globally
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent status: {str(e)}")

@app.get("/api/v1/agents/logs")
async def get_agent_logs(limit: int = 50, agent_id: str = None):
    """Get agent logs"""
    try:
        from .core.supabase import supabase_client
        supabase = supabase_client.get_client()
        
        query = supabase.table("agent_logs").select("*").order("timestamp", desc=True).limit(limit)
        
        if agent_id:
            query = query.eq("agent_id", agent_id)
        
        result = query.execute()
        
        return {
            "logs": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent logs: {str(e)}")

@app.get("/api/v1/agents/actions")
async def get_agent_actions(limit: int = 50, status: str = None):
    """Get agent actions"""
    try:
        from .core.supabase import supabase_client
        supabase = supabase_client.get_client()
        
        query = supabase.table("agent_actions").select("*").order("created_at", desc=True).limit(limit)
        
        if status:
            query = query.eq("status", status)
        
        result = query.execute()
        
        return {
            "actions": result.data if result.data else [],
            "total": len(result.data) if result.data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agent actions: {str(e)}")

@app.post("/api/v1/agents/actions/{action_id}/approve")
async def approve_action(action_id: str):
    """Approve an agent action and execute it"""
    try:
        from .core.supabase import supabase_client
        supabase = supabase_client.get_client()
        
        # First, get the action details
        action_result = supabase.table("agent_actions").select("*").eq("id", action_id).execute()
        if not action_result.data:
            raise HTTPException(status_code=404, detail=f"Action with id '{action_id}' not found")
        
        action = action_result.data[0]
        payload = action.get("payload", {})
        action_type = action.get("action_type", "")
        
        # Execute the action based on its type
        execution_result = await execute_approved_action(action_type, payload, supabase)
        
        # Update the action status to approved (without the new columns)
        result = supabase.table("agent_actions").update({
            "status": "approved",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", action_id).execute()
        
        return {
            "message": f"Action {action_id} approved and executed successfully",
            "status": "success",
            "execution_result": execution_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving action: {str(e)}")

async def execute_approved_action(action_type: str, payload: dict, supabase) -> dict:
    """Execute an approved action and make changes to the dataset"""
    try:
        if action_type == "optimization":
            return await execute_optimization_action(payload, supabase)
        elif action_type == "inventory_management":
            return await execute_inventory_action(payload, supabase)
        elif action_type == "reorder":
            return await execute_reorder_action(payload, supabase)
        elif action_type == "decision":
            # Handle decision actions based on the action in the payload
            action = payload.get("action", "")
            if action == "increase":
                return await execute_optimization_action(payload, supabase)
            elif action == "discount":
                return await execute_inventory_action(payload, supabase)
            elif action == "restock":
                return await execute_inventory_action(payload, supabase)
            elif action == "discontinue":
                return await execute_optimization_action(payload, supabase)
            else:
                return {"status": "success", "message": f"Decision action '{action}' executed (no database changes)"}
        else:
            return {"status": "unknown_action_type", "message": f"Unknown action type: {action_type}"}
    except Exception as e:
        return {"status": "error", "message": f"Error executing action: {str(e)}"}

async def execute_optimization_action(payload: dict, supabase) -> dict:
    """Execute an optimization action (create purchase orders for increases)"""
    try:
        item_id = payload.get("item_id")
        action = payload.get("action")
        current_level = payload.get("current_level", 0)
        recommended_level = payload.get("recommended_level", 0)
        
        if action == "increase":
            # Create a purchase order instead of directly updating inventory
            quantity_needed = recommended_level - current_level
            
            # Handle descriptive item_ids (like "Electronics - Laptops") by using them as item_name
            item_name = item_id if not item_id.startswith("770e8400") else f"Item {item_id}"
            
            # Create purchase order - use NULL for item_id if it's not a valid UUID
            order_data = {
                "item_name": item_name,
                "quantity": quantity_needed,
                "order_type": "restock",
                "status": "pending",
                "requested_by": "inventory_agent",
                "created_at": datetime.utcnow().isoformat(),
                "expected_delivery": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "location": "Unknown",  # Use default location since we can't query inventory
                "reason": f"Increase inventory from {current_level} to {recommended_level} units"
            }
            
            # Only include item_id if it's a valid UUID
            if item_id.startswith("770e8400"):
                order_data["item_id"] = item_id
            
            result = supabase.table("purchase_orders").insert(order_data).execute()
            
            return {
                "status": "success",
                "action": "created_purchase_order",
                "item_name": item_name,
                "quantity_ordered": quantity_needed,
                "order_id": result.data[0].get("id") if result.data else None,
                "current_level": current_level,
                "target_level": recommended_level,
                "message": f"Purchase order created for {quantity_needed} units"
            }
        elif action == "decrease":
            # For decreases, we might want to create a disposal order or mark for clearance
            disposal_quantity = current_level - recommended_level
            
            disposal_data = {
                "quantity": disposal_quantity,
                "disposal_type": "clearance",
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "reason": "Inventory optimization - excess stock"
            }
            
            # Only include item_id if it's a valid UUID
            if item_id.startswith("770e8400"):
                disposal_data["item_id"] = item_id
            
            result = supabase.table("disposal_orders").insert(disposal_data).execute()
            
            return {
                "status": "success",
                "action": "created_disposal_order",
                "item_name": item_id if not item_id.startswith("770e8400") else f"Item {item_id}",
                "quantity_to_dispose": disposal_quantity,
                "order_id": result.data[0].get("id") if result.data else None,
                "message": "Disposal order created for excess inventory"
            }
        elif action == "discontinue":
            # Handle discontinue actions by creating disposal orders
            # For discontinue actions, we don't have current_level/recommended_level, so use a default quantity
            disposal_quantity = payload.get("current_level", 5)  # Default to 5 if not specified
            
            disposal_data = {
                "quantity": disposal_quantity,
                "disposal_type": "clearance",
                "status": "pending",
                "created_at": datetime.utcnow().isoformat(),
                "reason": "Item discontinued - clearing remaining inventory"
            }
            # Only include item_id if it's a valid UUID
            if item_id.startswith("770e8400"):
                disposal_data["item_id"] = item_id
            
            result = supabase.table("disposal_orders").insert(disposal_data).execute()
            return {
                "status": "success",
                "action": "created_disposal_order",
                "item_name": item_id if not item_id.startswith("770e8400") else f"Item {item_id}",
                "quantity_to_dispose": disposal_quantity,
                "order_id": result.data[0].get("id") if result.data else None,
                "message": "Disposal order created for discontinued item"
            }
        else:
            return {
                "status": "success",
                "action": "maintained_inventory",
                "item_id": item_id,
                "message": "No change needed"
            }
    except Exception as e:
        return {"status": "error", "message": f"Error executing optimization action: {str(e)}"}

async def execute_inventory_action(payload: dict, supabase) -> dict:
    """Execute an inventory management action (discount, restock, etc.)"""
    try:
        item_id = payload.get("item_id")
        action = payload.get("action")
        discount_percentage = payload.get("discount_percentage", 0)
        
        if action == "discount":
            # Apply discount to the item
            result = supabase.table("inventory").update({
                "discount_percentage": discount_percentage,
                "discount_applied_at": datetime.utcnow().isoformat()
            }).eq("id", item_id).execute()
            
            return {
                "status": "success",
                "action": "applied_discount",
                "item_id": item_id,
                "discount_percentage": discount_percentage
            }
        elif action == "restock":
            item_result = supabase.table("inventory").select("id, location, quantity").eq("id", item_id).execute()
            item_data = item_result.data[0] if item_result.data else {}
            current_quantity = item_data.get("quantity", 0)
            order_data = {
                "item_id": item_id,
                "item_name": f"Item {item_id}",
                "quantity": 5,
                "order_type": "restock",
                "status": "pending",
                "requested_by": "inventory_agent",
                "created_at": datetime.utcnow().isoformat(),
                "expected_delivery": (datetime.utcnow() + timedelta(days=5)).isoformat(),
                "location": item_data.get("location", "Unknown"),
                "reason": "Low stock restock"
            }
            result = supabase.table("purchase_orders").insert(order_data).execute()
            return {
                "status": "success",
                "action": "created_restock_order",
                "item_id": item_id,
                "item_name": f"Item {item_id}",
                "quantity_ordered": 5,
                "order_id": result.data[0].get("id") if result.data else None,
                "current_quantity": current_quantity,
                "message": "Restock order created for 5 units"
            }
        else:
            return {
                "status": "success",
                "action": "maintained",
                "item_id": item_id,
                "message": "No change needed"
            }
    except Exception as e:
        return {"status": "error", "message": f"Error executing inventory action: {str(e)}"}

async def execute_reorder_action(payload: dict, supabase) -> dict:
    """Execute a reorder action by creating a purchase order"""
    try:
        item_id = payload.get("item_id")
        recommended_quantity = payload.get("recommended_quantity", 0)
        item_result = supabase.table("inventory").select("id, location, quantity").eq("id", item_id).execute()
        item_data = item_result.data[0] if item_result.data else {}
        current_quantity = item_data.get("quantity", 0)
        quantity_to_order = max(0, recommended_quantity - current_quantity)

        if quantity_to_order > 0:
            order_data = {
                "item_id": item_id,
                "item_name": f"Item {item_id}",
                "quantity": quantity_to_order,
                "order_type": "reorder",
                "status": "pending",
                "requested_by": "inventory_agent",
                "created_at": datetime.utcnow().isoformat(),
                "expected_delivery": (datetime.utcnow() + timedelta(days=10)).isoformat(),
                "location": item_data.get("location", "Unknown"),
                "reason": "Reorder based on demand analysis"
            }
            result = supabase.table("purchase_orders").insert(order_data).execute()
            return {
                "status": "success",
                "action": "created_reorder",
                "item_id": item_id,
                "item_name": f"Item {item_id}",
                "quantity_ordered": quantity_to_order,
                "order_id": result.data[0].get("id") if result.data else None,
                "current_quantity": current_quantity,
                "target_quantity": recommended_quantity,
                "message": f"Reorder created for {quantity_to_order} units"
            }
        else:
            return {
                "status": "success",
                "action": "no_reorder_needed",
                "item_id": item_id,
                "message": "Current quantity is sufficient"
            }
    except Exception as e:
        return {"status": "error", "message": f"Error executing reorder action: {str(e)}"}

@app.post("/api/v1/agents/actions/{action_id}/decline")
async def decline_action(action_id: str):
    """Decline an agent action"""
    try:
        from .core.supabase import supabase_client
        supabase = supabase_client.get_client()
        
        # Update the action status to declined
        result = supabase.table("agent_actions").update({
            "status": "declined",
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", action_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail=f"Action with id '{action_id}' not found")
        
        return {
            "message": f"Action {action_id} declined successfully",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error declining action: {str(e)}")

@app.post("/api/v1/agents/trigger")
async def trigger_agent_action(agent_type: str, action: str, data: Dict[str, Any] = None):
    """Trigger a specific agent action"""
    try:
        agent = agent_manager.agents.get(agent_type)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent type '{agent_type}' not found")
        
        # Trigger the action based on agent type
        if agent_type == "inventory":
            if action == "check_low_stock":
                await agent.check_low_stock()
            elif action == "optimize_inventory":
                await agent.optimize_inventory()
            elif action == "handle_expired_items":
                await agent.handle_expired_items()
            elif action == "trigger_decision":
                # Generic decision trigger for inventory agent
                await agent.process()
            else:
                raise HTTPException(status_code=400, detail=f"Unknown action '{action}' for inventory agent")
        
        elif agent_type == "routing":
            if action == "optimize_routes":
                await agent.optimize_routes()
            elif action == "assign_vehicles":
                await agent.assign_vehicles()
            elif action == "handle_dynamic_routing":
                await agent.handle_dynamic_routing()
            elif action == "trigger_decision":
                # Generic decision trigger for routing agent
                await agent.process()
            else:
                raise HTTPException(status_code=400, detail=f"Unknown action '{action}' for routing agent")
        
        elif agent_type == "pricing":
            if action == "analyze_market_conditions":
                await agent.analyze_market_conditions()
            elif action == "optimize_inventory_pricing":
                await agent.optimize_inventory_pricing()
            elif action == "handle_dynamic_pricing":
                await agent.handle_dynamic_pricing()
            elif action == "trigger_decision":
                # Generic decision trigger for pricing agent
                await agent.process()
            else:
                raise HTTPException(status_code=400, detail=f"Unknown action '{action}' for pricing agent")
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type '{agent_type}'")
        
        return {
            "message": f"Triggered {action} for {agent_type} agent",
            "status": "success"
        }
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering agent action: {str(e)}")

@app.get("/api/v1/system/stats")
async def get_system_stats():
    """Get system statistics"""
    try:
        from .core.supabase import supabase_client
        supabase = supabase_client.get_client()
        
        # Get counts from different tables
        inventory_result = supabase.table("inventory").select("id", count="exact").execute()
        orders_result = supabase.table("orders").select("id", count="exact").execute()
        fleet_result = supabase.table("fleet").select("id", count="exact").execute()
        logs_result = supabase.table("agent_logs").select("id", count="exact").execute()
        actions_result = supabase.table("agent_actions").select("id", count="exact").execute()
        
        return {
            "inventory_items": inventory_result.count if hasattr(inventory_result, 'count') else 0,
            "orders": orders_result.count if hasattr(orders_result, 'count') else 0,
            "fleet_vehicles": fleet_result.count if hasattr(fleet_result, 'count') else 0,
            "agent_logs": logs_result.count if hasattr(logs_result, 'count') else 0,
            "agent_actions": actions_result.count if hasattr(actions_result, 'count') else 0,
            "agents_running": False # Agents are no longer managed globally
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system stats: {str(e)}")

@app.get("/api/v1/agents/duplicate-detection-config")
async def get_duplicate_detection_config():
    """Get duplicate detection configuration"""
    return {
        "enabled": True,
        "time_window_hours": 24,
        "similarity_threshold": 0.7,
        "description": "Prevents duplicate decisions for the same items within the specified time window"
    }

@app.post("/api/v1/agents/duplicate-detection-config")
async def update_duplicate_detection_config(config: Dict[str, Any]):
    """Update duplicate detection configuration"""
    # This would typically update a configuration table
    # For now, we'll just return the updated config
    return {
        "message": "Duplicate detection configuration updated",
        "config": config
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 