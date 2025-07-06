import structlog
from fastapi import APIRouter, HTTPException
import httpx
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()

async def get_supabase_agents():
    """Get all agents from Supabase REST API"""
    try:
        url = f"{settings.SUPABASE_URL}/rest/v1/agents"
        headers = {
            "apikey": settings.SUPABASE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching agents from Supabase REST API: {str(e)}")
        raise

async def get_supabase_agent_by_id(agent_id: str):
    """Get a specific agent by ID from Supabase REST API"""
    try:
        url = f"{settings.SUPABASE_URL}/rest/v1/agents?id=eq.{agent_id}"
        headers = {
            "apikey": settings.SUPABASE_KEY,
            "Authorization": f"Bearer {settings.SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            agents = response.json()
            return agents[0] if agents else None
    except Exception as e:
        logger.error(f"Error fetching agent {agent_id} from Supabase REST API: {str(e)}")
        raise

@router.get("")
async def get_all_agents():
    """Get all agents from Supabase REST API"""
    try:
        agents = await get_supabase_agents()
        return agents
    except Exception as e:
        logger.error(f"Error fetching agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_id}")
async def get_agent_by_id(agent_id: str):
    """Get a specific agent by ID from Supabase REST API"""
    try:
        agent = await get_supabase_agent_by_id(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return agent
    except Exception as e:
        logger.error(f"Error fetching agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 