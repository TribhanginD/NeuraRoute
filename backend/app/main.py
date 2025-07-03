"""
NeuraRoute Main Application
FastAPI application with autonomous agents, simulation, and AI-powered logistics
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

from app.core.config import settings
from app.core.database import async_engine, Base, get_db
from app.simulation.engine import SimulationEngine
from app.agents.manager import AgentManager
from app.api.v1.api import api_router

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

# Global instances
simulation_engine: SimulationEngine = None
agent_manager: AgentManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global simulation_engine, agent_manager
    
    logger.info("Starting NeuraRoute application...")
    
    # Initialize database
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise
    
    # Initialize agent manager
    try:
        agent_manager = AgentManager()
        await agent_manager.start()
        logger.info("Agent manager initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize agent manager", error=str(e))
        raise
    
    # Initialize simulation engine
    try:
        simulation_engine = SimulationEngine()
        await simulation_engine.initialize()
        logger.info("Simulation engine initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize simulation engine", error=str(e))
        raise
    
    logger.info("NeuraRoute application started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down NeuraRoute application...")
    
    if simulation_engine:
        await simulation_engine.shutdown()
    
    if agent_manager:
        await agent_manager.shutdown()
    
    logger.info("NeuraRoute application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="NeuraRoute API",
    description="AI-Native Hyperlocal Logistics System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.API_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception", 
                exception=str(exc), 
                path=request.url.path,
                method=request.method)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        # Check Redis connection
        from app.core.database import redis_client
        await redis_client.ping()
        
        # Check agent manager
        agent_status = "healthy" if agent_manager and agent_manager.is_healthy() else "unhealthy"
        
        # Check simulation engine
        sim_status = "healthy" if simulation_engine and simulation_engine.is_healthy() else "unhealthy"
        
        return {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "services": {
                "database": "healthy",
                "redis": "healthy",
                "agent_manager": agent_status,
                "simulation_engine": sim_status
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "name": "NeuraRoute",
        "version": "1.0.0",
        "description": "AI-Native Hyperlocal Logistics System",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Dependency to get simulation engine
def get_simulation_engine() -> SimulationEngine:
    if not simulation_engine:
        raise HTTPException(status_code=503, detail="Simulation engine not available")
    return simulation_engine


# Dependency to get agent manager
def get_agent_manager() -> AgentManager:
    if not agent_manager:
        raise HTTPException(status_code=503, detail="Agent manager not available")
    return agent_manager


# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for real-time updates"""
    try:
        await websocket.accept()
        logger.info("WebSocket connection established")
        
        # Send initial system status
        await websocket.send_json({
            "type": "system_status",
            "data": {
                "simulation_status": simulation_engine.get_status() if simulation_engine else "unknown",
                "active_agents": len(agent_manager.get_active_agents()) if agent_manager else 0
            }
        })
        
        # Keep connection alive and send updates
        while True:
            # Send periodic updates
            await asyncio.sleep(5)
            
            if simulation_engine and agent_manager:
                await websocket.send_json({
                    "type": "update",
                    "data": {
                        "simulation_tick": simulation_engine.get_current_tick(),
                        "agent_status": agent_manager.get_status_summary()
                    }
                })
                
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
    finally:
        logger.info("WebSocket connection closed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 