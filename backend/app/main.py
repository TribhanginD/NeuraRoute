import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Dict, Any, List
import uvicorn

from .core.config import settings
from .agents.manager import agent_manager

# Global variable to track if agents are running
agents_running = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting NeuraRoute Agentic System...")
    yield
    # Shutdown
    print("Shutting down NeuraRoute Agentic System...")
    if agents_running:
        await agent_manager.stop_agents()

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
            "status": "healthy" if agents_running else "offline",
            "agents_running": agents_running,
            "agent_status": agent_status,
            "services": {
                "api": "healthy",
                "agents": "healthy" if agents_running else "offline",
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

@app.post("/api/v1/agents/start")
async def start_agents(background_tasks: BackgroundTasks):
    """Start all agents"""
    global agents_running
    
    try:
        if agents_running:
            return {"message": "Agents are already running", "status": "running"}
        
        # Start agents in background
        background_tasks.add_task(start_agents_background)
        
        return {
            "message": "Starting agents...",
            "status": "starting"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting agents: {str(e)}")

async def start_agents_background():
    """Background task to start agents"""
    global agents_running
    
    try:
        await agent_manager.initialize_agents()
        await agent_manager.start_agents()
        agents_running = True
        print("Agents started successfully")
    except Exception as e:
        print(f"Error starting agents: {e}")
        agents_running = False

@app.post("/api/v1/agents/stop")
async def stop_agents():
    """Stop all agents"""
    global agents_running
    
    try:
        if not agents_running:
            return {"message": "Agents are not running", "status": "stopped"}
        
        await agent_manager.stop_agents()
        agents_running = False
        
        return {
            "message": "Agents stopped successfully",
            "status": "stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping agents: {str(e)}")

@app.get("/api/v1/agents/status")
async def get_agent_status():
    """Get status of all agents"""
    try:
        status = await agent_manager.get_agent_status()
        status["agents_running"] = agents_running
        
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

@app.post("/api/v1/agents/trigger")
async def trigger_agent_action(agent_type: str, action: str, data: Dict[str, Any] = None):
    """Trigger a specific agent action"""
    try:
        if not agents_running:
            raise HTTPException(status_code=400, detail="Agents are not running")
        
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
            else:
                raise HTTPException(status_code=400, detail=f"Unknown action '{action}' for inventory agent")
        
        elif agent_type == "routing":
            if action == "optimize_routes":
                await agent.optimize_routes()
            elif action == "assign_vehicles":
                await agent.assign_vehicles()
            elif action == "handle_dynamic_routing":
                await agent.handle_dynamic_routing()
            else:
                raise HTTPException(status_code=400, detail=f"Unknown action '{action}' for routing agent")
        
        elif agent_type == "pricing":
            if action == "analyze_market_conditions":
                await agent.analyze_market_conditions()
            elif action == "optimize_inventory_pricing":
                await agent.optimize_inventory_pricing()
            elif action == "handle_dynamic_pricing":
                await agent.handle_dynamic_pricing()
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
            "agents_running": agents_running
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system stats: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 