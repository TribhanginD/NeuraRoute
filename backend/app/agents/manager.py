import asyncio
import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
import uuid

from app.core.config import settings
from app.models.agents import Agent, AgentLog, AgentMemory, AgentType, AgentStatus, TaskStatus
from app.core.database import get_db
from app.agents.restock_agent import RestockAgent
from app.agents.route_agent import RouteAgent
from app.agents.pricing_agent import PricingAgent
from app.agents.dispatch_agent import DispatchAgent
from app.agents.forecasting_agent import ForecastingAgent

logger = structlog.get_logger()

class AgentManager:
    """Manager for coordinating autonomous agents"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.active_agents: Dict[str, Any] = {}
        self.agent_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        
    async def start(self):
        """Start the agent manager"""
        logger.info("Starting Agent Manager")
        self.is_running = True
        
        # Initialize agents
        await self._initialize_agents()
        
        # Start agent monitoring
        asyncio.create_task(self._monitor_agents())
        
        logger.info("Agent Manager started successfully")
    
    async def stop(self):
        """Stop the agent manager"""
        logger.info("Stopping Agent Manager")
        self.is_running = False
        
        # Stop all agents
        for agent_id, task in self.agent_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Stop agent instances
        for agent in self.active_agents.values():
            await agent.stop()
        
        logger.info("Agent Manager stopped")
    
    async def _initialize_agents(self):
        """Initialize all agent types"""
        db = next(get_db())
        
        try:
            # Create or get agent records
            agent_configs = [
                {
                    "agent_type": AgentType.RESTOCK,
                    "name": "Restock Agent",
                    "class": RestockAgent,
                    "config": {"check_interval": 300, "threshold_factor": 0.2}
                },
                {
                    "agent_type": AgentType.ROUTE,
                    "name": "Route Agent",
                    "class": RouteAgent,
                    "config": {"optimization_interval": 600, "traffic_update_interval": 300}
                },
                {
                    "agent_type": AgentType.PRICING,
                    "name": "Pricing Agent",
                    "class": PricingAgent,
                    "config": {"price_check_interval": 1800, "competitor_check_interval": 3600}
                },
                {
                    "agent_type": AgentType.DISPATCH,
                    "name": "Dispatch Agent",
                    "class": DispatchAgent,
                    "config": {"dispatch_interval": 120, "assignment_timeout": 300}
                },
                {
                    "agent_type": AgentType.FORECASTING,
                    "name": "Forecasting Agent",
                    "class": ForecastingAgent,
                    "config": {"forecast_interval": 3600, "horizon_hours": 24}
                }
            ]
            
            for config in agent_configs:
                agent_id = f"{config['agent_type']}_agent"
                
                # Get or create agent record
                agent_record = db.query(Agent).filter(
                    Agent.agent_id == agent_id
                ).first()
                
                if not agent_record:
                    agent_record = Agent(
                        agent_id=agent_id,
                        name=config["name"],
                        agent_type=config["agent_type"],
                        status=AgentStatus.IDLE,
                        config=config["config"],
                        is_active=True
                    )
                    db.add(agent_record)
                    db.commit()
                
                # Create agent instance
                agent_instance = config["class"](agent_record)
                await agent_instance.initialize()
                
                self.agents[agent_id] = agent_instance
                self.active_agents[agent_id] = agent_instance
                
                # Start agent task
                task = asyncio.create_task(self._run_agent(agent_id))
                self.agent_tasks[agent_id] = task
                
                logger.info(f"Initialized {config['name']}", agent_id=agent_id)
        
        except Exception as e:
            logger.error("Failed to initialize agents", error=str(e))
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _run_agent(self, agent_id: str):
        """Run an individual agent"""
        agent = self.active_agents[agent_id]
        
        while self.is_running:
            try:
                # Update heartbeat
                agent.update_heartbeat()
                
                # Run agent logic
                await agent.run_cycle()
                
                # Wait for next cycle
                await asyncio.sleep(agent.get_cycle_interval())
                
            except asyncio.CancelledError:
                logger.info(f"Agent {agent_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Agent {agent_id} error", error=str(e))
                await agent.handle_error(e)
                await asyncio.sleep(30)  # Wait before retry
    
    async def _monitor_agents(self):
        """Monitor agent health and performance"""
        while self.is_running:
            try:
                for agent_id, agent in self.active_agents.items():
                    # Check agent health
                    if not agent.is_healthy():
                        logger.warning(f"Agent {agent_id} is unhealthy, restarting")
                        await self._restart_agent(agent_id)
                    
                    # Check for stuck agents
                    if agent.is_stuck():
                        logger.warning(f"Agent {agent_id} appears stuck, restarting")
                        await self._restart_agent(agent_id)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error("Agent monitoring error", error=str(e))
                await asyncio.sleep(60)
    
    async def _restart_agent(self, agent_id: str):
        """Restart a specific agent"""
        try:
            # Stop current agent
            if agent_id in self.active_agents:
                await self.active_agents[agent_id].stop()
            
            # Cancel current task
            if agent_id in self.agent_tasks:
                self.agent_tasks[agent_id].cancel()
            
            # Reinitialize agent
            db = next(get_db())
            agent_record = db.query(Agent).filter(Agent.agent_id == agent_id).first()
            
            if agent_record:
                # Create new agent instance
                agent_class = self._get_agent_class(agent_record.agent_type)
                agent_instance = agent_class(agent_record)
                await agent_instance.initialize()
                
                self.active_agents[agent_id] = agent_instance
                
                # Start new task
                task = asyncio.create_task(self._run_agent(agent_id))
                self.agent_tasks[agent_id] = task
                
                logger.info(f"Restarted agent {agent_id}")
            
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to restart agent {agent_id}", error=str(e))
    
    def _get_agent_class(self, agent_type: str):
        """Get agent class by type"""
        agent_classes = {
            AgentType.RESTOCK: RestockAgent,
            AgentType.ROUTE: RouteAgent,
            AgentType.PRICING: PricingAgent,
            AgentType.DISPATCH: DispatchAgent,
            AgentType.FORECASTING: ForecastingAgent
        }
        return agent_classes.get(agent_type)
    
    def get_active_agents(self) -> List[str]:
        """Get list of active agent IDs"""
        return list(self.active_agents.keys())
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        if agent_id in self.active_agents:
            agent = self.active_agents[agent_id]
            return {
                "agent_id": agent_id,
                "name": agent.name,
                "status": agent.status,
                "is_healthy": agent.is_healthy(),
                "last_heartbeat": agent.last_heartbeat,
                "tasks_completed": agent.tasks_completed,
                "tasks_failed": agent.tasks_failed,
                "average_response_time": agent.average_response_time
            }
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall agent manager status"""
        return {
            "is_running": self.is_running,
            "total_agents": len(self.active_agents),
            "active_agents": self.get_active_agents(),
            "agent_statuses": {
                agent_id: self.get_agent_status(agent_id)
                for agent_id in self.active_agents.keys()
            }
        }
    
    async def trigger_agent_action(
        self,
        agent_id: str,
        action: str,
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Trigger a specific action on an agent"""
        if agent_id not in self.active_agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        agent = self.active_agents[agent_id]
        return await agent.execute_action(action, parameters or {})
    
    async def get_agent_logs(
        self,
        agent_id: str,
        limit: int = 100,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get recent logs for an agent"""
        if not db:
            db = next(get_db())
        
        try:
            logs = db.query(AgentLog).filter(
                AgentLog.agent_id == agent_id
            ).order_by(
                AgentLog.created_at.desc()
            ).limit(limit).all()
            
            return [log.to_dict() for log in logs]
        
        finally:
            db.close()
    
    async def get_agent_memory(
        self,
        agent_id: str,
        memory_type: str = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get agent memory entries"""
        if not db:
            db = next(get_db())
        
        try:
            query = db.query(AgentMemory).filter(AgentMemory.agent_id == agent_id)
            
            if memory_type:
                query = query.filter(AgentMemory.memory_type == memory_type)
            
            memories = query.order_by(AgentMemory.importance.desc()).all()
            
            return [memory.to_dict() for memory in memories]
        
        finally:
            db.close() 