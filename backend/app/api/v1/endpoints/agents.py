from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import structlog

from app.core.database import get_db
from app.models.agents import Agent, AgentLog, AgenticMemory
from app.agents.manager import AgentManager

logger = structlog.get_logger()
router = APIRouter()

# Global agent manager instance
agent_manager = AgentManager()

@router.get("/")
async def get_agents(db: Session = Depends(get_db)):
    """Get all agents"""
    try:
        agents = db.query(Agent).all()
        return {
            "agents": [
                {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "agent_type": agent.agent_type,
                    "status": agent.status,
                    "last_heartbeat": agent.last_heartbeat.isoformat() if agent.last_heartbeat else None,
                    "tasks_completed": agent.tasks_completed,
                    "tasks_failed": agent.tasks_failed,
                    "average_response_time": agent.average_response_time
                } for agent in agents
            ]
        }
    except Exception as e:
        logger.error("Failed to get agents", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_id}")
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get specific agent details"""
    try:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "agent_type": agent.agent_type,
            "status": agent.status,
            "config": agent.config,
            "last_heartbeat": agent.last_heartbeat.isoformat() if agent.last_heartbeat else None,
            "tasks_completed": agent.tasks_completed,
            "tasks_failed": agent.tasks_failed,
            "average_response_time": agent.average_response_time,
            "created_at": agent.created_at.isoformat(),
            "updated_at": agent.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_id}/start")
async def start_agent(agent_id: str):
    """Start a specific agent"""
    try:
        await agent_manager.start_agent(agent_id)
        return {"message": f"Agent {agent_id} started successfully"}
    except Exception as e:
        logger.error(f"Failed to start agent {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Stop a specific agent"""
    try:
        await agent_manager.stop_agent(agent_id)
        return {"message": f"Agent {agent_id} stopped successfully"}
    except Exception as e:
        logger.error(f"Failed to stop agent {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_id}/restart")
async def restart_agent(agent_id: str):
    """Restart a specific agent"""
    try:
        await agent_manager.restart_agent(agent_id)
        return {"message": f"Agent {agent_id} restarted successfully"}
    except Exception as e:
        logger.error(f"Failed to restart agent {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_id}/logs")
async def get_agent_logs(
    agent_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get agent logs"""
    try:
        logs = db.query(AgentLog).filter(
            AgentLog.agent_id == agent_id
        ).order_by(
            AgentLog.timestamp.desc()
        ).offset(offset).limit(limit).all()
        
        return {
            "logs": [
                {
                    "task_id": log.task_id,
                    "action": log.action,
                    "status": log.status,
                    "timestamp": log.timestamp.isoformat(),
                    "execution_time_ms": log.execution_time_ms,
                    "error_message": log.error_message,
                    "reasoning": log.reasoning
                } for log in logs
            ],
            "total": len(logs)
        }
    except Exception as e:
        logger.error(f"Failed to get agent logs for {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_id}/memory")
async def get_agent_memory(
    agent_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get agent memory"""
    try:
        memories = db.query(AgenticMemory).filter(
            AgenticMemory.is_expired() == False
        ).order_by(
            AgenticMemory.importance.desc()
        ).offset(offset).limit(limit).all()
        
        return {
            "memories": [
                {
                    "memory_type": memory.memory_type,
                    "key": memory.key,
                    "value": memory.value,
                    "importance": memory.importance,
                    "created_at": memory.created_at.isoformat(),
                    "expires_at": memory.expires_at.isoformat() if memory.expires_at else None
                } for memory in memories
            ],
            "total": len(memories)
        }
    except Exception as e:
        logger.error(f"Failed to get agent memory for {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/overview")
async def get_agents_status():
    """Get overview of all agents status"""
    try:
        status = agent_manager.get_status()
        return status
    except Exception as e:
        logger.error("Failed to get agents status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 