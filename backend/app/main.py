from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import structlog

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.api import api_router
from app.simulation.engine import SimulationEngine
from app.agents.manager import AgentManager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NeuraRoute API",
    description="AI-Native Hyperlocal Logistics System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Global instances
simulation_engine = SimulationEngine()
agent_manager = AgentManager()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting NeuraRoute API")
    
    # Initialize simulation engine
    await simulation_engine.start()
    
    # Initialize agent manager
    await agent_manager.start()
    
    logger.info("NeuraRoute API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down NeuraRoute API")
    
    # Stop simulation engine
    await simulation_engine.stop()
    
    # Stop agent manager
    await agent_manager.stop()
    
    logger.info("NeuraRoute API shutdown complete")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NeuraRoute API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "simulation": simulation_engine.is_running(),
        "agents": agent_manager.get_status()
    }

@app.get("/api/v1/simulation/status")
async def get_simulation_status():
    """Get current simulation status"""
    return {
        "is_running": simulation_engine.is_running(),
        "current_time": simulation_engine.get_current_time(),
        "tick_count": simulation_engine.get_tick_count(),
        "agents_active": len(agent_manager.get_active_agents())
    }

@app.post("/api/v1/simulation/start")
async def start_simulation():
    """Start the simulation"""
    try:
        await simulation_engine.start()
        return {"message": "Simulation started successfully"}
    except Exception as e:
        logger.error("Failed to start simulation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/simulation/stop")
async def stop_simulation():
    """Stop the simulation"""
    try:
        await simulation_engine.stop()
        return {"message": "Simulation stopped successfully"}
    except Exception as e:
        logger.error("Failed to stop simulation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/simulation/reset")
async def reset_simulation():
    """Reset the simulation to initial state"""
    try:
        await simulation_engine.reset()
        return {"message": "Simulation reset successfully"}
    except Exception as e:
        logger.error("Failed to reset simulation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 