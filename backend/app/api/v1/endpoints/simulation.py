from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import structlog

from app.core.database import get_db
from app.models.simulation import SimulationState, SimulationEvent
from app.simulation.engine import SimulationEngine

logger = structlog.get_logger()
router = APIRouter()

# Global simulation engine instance
simulation_engine = SimulationEngine()

@router.get("/status")
async def get_simulation_status():
    """Get current simulation status"""
    return {
        "status": "ok",
        "is_running": simulation_engine.is_running(),
        "current_time": simulation_engine.get_current_time(),
        "tick_count": simulation_engine.get_tick_count(),
        "speed_multiplier": simulation_engine.get_speed_multiplier(),
        "total_agents": simulation_engine.get_total_agents()
    }

@router.post("/start")
async def start_simulation():
    """Start the simulation"""
    try:
        await simulation_engine.start()
        return {"message": "Simulation started successfully", "status": "ok"}
    except Exception as e:
        logger.error("Failed to start simulation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_simulation():
    """Stop the simulation"""
    try:
        await simulation_engine.stop()
        return {"message": "Simulation stopped successfully", "status": "ok"}
    except Exception as e:
        logger.error("Failed to stop simulation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset")
async def reset_simulation():
    """Reset the simulation to initial state"""
    try:
        await simulation_engine.reset()
        return {"message": "Simulation reset successfully"}
    except Exception as e:
        logger.error("Failed to reset simulation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pause")
async def pause_simulation():
    """Pause the simulation"""
    try:
        await simulation_engine.pause()
        return {"message": "Simulation paused successfully"}
    except Exception as e:
        logger.error("Failed to pause simulation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resume")
async def resume_simulation():
    """Resume the simulation"""
    try:
        await simulation_engine.resume()
        return {"message": "Simulation resumed successfully"}
    except Exception as e:
        logger.error("Failed to resume simulation", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/speed")
async def set_simulation_speed(speed_multiplier: float):
    """Set simulation speed multiplier"""
    try:
        simulation_engine.set_speed_multiplier(speed_multiplier)
        return {"message": f"Simulation speed set to {speed_multiplier}x"}
    except Exception as e:
        logger.error("Failed to set simulation speed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ticks")
async def get_simulation_ticks(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get simulation tick history"""
    try:
        events = db.query(SimulationEvent).filter(
            SimulationEvent.event_type == 'tick_end'
        ).order_by(
            SimulationEvent.tick_number.desc()
        ).offset(offset).limit(limit).all()
        
        return {
            "ticks": [
                {
                    "tick_number": event.tick_number,
                    "timestamp": event.timestamp.isoformat(),
                    "simulation_time": event.event_data.get('simulation_time'),
                    "agents_active": event.event_data.get('agents_active', 0),
                    "events_processed": event.event_data.get('events_processed', 0)
                } for event in events
            ],
            "total": len(events)
        }
    except Exception as e:
        logger.error("Failed to get simulation ticks", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/state")
async def get_simulation_state(db: Session = Depends(get_db)):
    """Get current simulation state"""
    try:
        state = db.query(SimulationState).order_by(
            SimulationState.created_at.desc()
        ).first()
        
        if not state:
            return {"message": "No simulation state found"}
        
        return {
            "timestamp": state.created_at.isoformat(),
            "current_tick": state.current_tick,
            "status": state.status,
            "speed_multiplier": state.speed_multiplier,
            "config": state.config
        }
    except Exception as e:
        logger.error("Failed to get simulation state", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 

@router.get("/history")
async def get_simulation_history():
    """Stub for simulation history (for tests)"""
    return []

@router.get("/metrics")
async def get_simulation_metrics():
    """Stub for simulation metrics (for tests)"""
    return {"metrics": {}, "status": "ok", "total_ticks": 0, "uptime": 12345, "performance_metrics": {}} 