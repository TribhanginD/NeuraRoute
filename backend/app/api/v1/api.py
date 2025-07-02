from fastapi import APIRouter
from app.api.v1.endpoints import simulation, agents, inventory, fleet, merchants, forecasting, ai, agentic

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(simulation.router, prefix="/simulation", tags=["simulation"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(fleet.router, prefix="/fleet", tags=["fleet"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["merchants"])
api_router.include_router(forecasting.router, prefix="/forecasting", tags=["forecasting"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(agentic.router, prefix="/agentic", tags=["agentic"]) 