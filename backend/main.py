"""
NeuraRoute - AI-Native Hyperlocal Logistics System
Main FastAPI Application
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import settings
from app.core.database import init_connections, close_connections
from app.core.logging import setup_logging
from app.agents.manager import AgentManager
from app.simulation.engine import SimulationEngine
from app.api.v1.api import api_router
# from app.api.v1.websocket import websocket_router  # Commented out - module doesn't exist

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global instances
agent_manager: AgentManager = None
simulation_engine: SimulationEngine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global agent_manager, simulation_engine
    
    logger.info("Starting NeuraRoute application...")
    
    # Initialize Redis only (skip local database since we're using Supabase)
    try:
        from app.core.database import init_redis
        await init_redis()
        logger.info("Redis initialized")
    except Exception as e:
        logger.warning(f"Redis initialization failed: {e}")
    
    # Initialize agent manager
    agent_manager = AgentManager()
    await agent_manager.start()
    logger.info("Agent manager started")
    
    # Initialize simulation engine
    simulation_engine = SimulationEngine()
    await simulation_engine.start()
    logger.info("Simulation engine started")
    
    yield
    
    # Cleanup
    logger.info("Shutting down NeuraRoute application...")
    
    if simulation_engine:
        await simulation_engine.stop()
        logger.info("Simulation engine stopped")
    
    if agent_manager:
        await agent_manager.stop()
        logger.info("Agent manager stopped")
    
    # Close Redis connection
    try:
        from app.core.database import close_redis
        await close_redis()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.warning(f"Error closing Redis: {e}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="NeuraRoute API",
        description="AI-Native Hyperlocal Logistics System API",
        version="1.0.0",
        docs_url="/docs" if settings.ENABLE_SWAGGER_UI else None,
        redoc_url="/redoc" if settings.ENABLE_REDOC else None,
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
    
    # Include routers
    app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")
    # app.include_router(websocket_router, prefix="/ws")  # Commented out - module doesn't exist
    
    # Health check endpoint
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """Health check endpoint"""
        try:
            # Check Redis connection (skip local database since we're using Supabase)
            from app.core.database import redis_client
            if redis_client:
                await redis_client.ping()
                redis_status = "healthy"
            else:
                redis_status = "not_initialized"
            
            return {
                "status": "healthy",
                "timestamp": asyncio.get_event_loop().time(),
                "version": "1.0.0",
                "services": {
                    "database": "supabase",  # Using Supabase instead of local DB
                    "redis": redis_status,
                    "agents": "healthy" if agent_manager else "starting",
                    "simulation": "healthy" if simulation_engine else "starting"
                }
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise HTTPException(status_code=503, detail="Service unhealthy")
    
    # Root endpoint
    @app.get("/")
    async def root() -> Dict[str, str]:
        """Root endpoint"""
        return {
            "message": "Welcome to NeuraRoute API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }
    
    # Exception handlers
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler"""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        """HTTP exception handler"""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    return app


# Create application instance
app = create_app()


def get_agent_manager() -> AgentManager:
    """Dependency to get agent manager instance"""
    if agent_manager is None:
        raise HTTPException(status_code=503, detail="Agent manager not available")
    return agent_manager


def get_simulation_engine() -> SimulationEngine:
    """Dependency to get simulation engine instance"""
    if simulation_engine is None:
        raise HTTPException(status_code=503, detail="Simulation engine not available")
    return simulation_engine


# Export dependencies for use in other modules
__all__ = ["app", "get_agent_manager", "get_simulation_engine"]


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    ) 