import asyncio
import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
import uuid
import json

from app.models.agents import Agent, AgentLog, AgentMemory, AgentStatus, TaskStatus
from app.core.database import get_db
from app.core.config import settings

logger = structlog.get_logger()

class BaseAgent(ABC):
    """Base class for all autonomous agents"""
    
    def __init__(self, agent_record: Agent):
        self.agent_record = agent_record
        self.agent_id = agent_record.agent_id
        self.name = agent_record.name
        self.agent_type = agent_record.agent_type
        self.config = agent_record.config or {}
        self.status = agent_record.status
        self.last_heartbeat = agent_record.last_heartbeat
        self.tasks_completed = agent_record.tasks_completed
        self.tasks_failed = agent_record.tasks_failed
        self.average_response_time = agent_record.average_response_time
        
        # Memory management
        self.memory = {}
        self.context_window = []
        
        # Performance tracking
        self.cycle_count = 0
        self.last_cycle_time = None
        self.error_count = 0
        self.max_retries = settings.max_agent_retries
        
    async def initialize(self):
        """Initialize the agent"""
        logger.info(f"Initializing {self.name}", agent_id=self.agent_id)
        
        try:
            # Load agent memory
            await self._load_memory()
            
            # Initialize agent-specific components
            await self._initialize_agent()
            
            # Update status
            self.status = AgentStatus.IDLE
            await self._update_status()
            
            logger.info(f"{self.name} initialized successfully", agent_id=self.agent_id)
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name}", agent_id=self.agent_id, error=str(e))
            self.status = AgentStatus.ERROR
            await self._update_status()
            raise
    
    async def stop(self):
        """Stop the agent"""
        logger.info(f"Stopping {self.name}", agent_id=self.agent_id)
        
        try:
            # Stop agent-specific components
            await self._stop_agent()
            
            # Save memory
            await self._save_memory()
            
            # Update status
            self.status = AgentStatus.OFFLINE
            await self._update_status()
            
            logger.info(f"{self.name} stopped successfully", agent_id=self.agent_id)
            
        except Exception as e:
            logger.error(f"Error stopping {self.name}", agent_id=self.agent_id, error=str(e))
    
    async def run_cycle(self):
        """Run one cycle of the agent's main logic"""
        start_time = datetime.utcnow()
        
        try:
            # Update status to busy
            self.status = AgentStatus.BUSY
            await self._update_status()
            
            # Run agent-specific cycle
            await self._run_cycle_logic()
            
            # Update performance metrics
            cycle_duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._update_performance_metrics(cycle_duration)
            
            # Update status to idle
            self.status = AgentStatus.IDLE
            await self._update_status()
            
            self.cycle_count += 1
            self.last_cycle_time = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error in {self.name} cycle", agent_id=self.agent_id, error=str(e))
            await self.handle_error(e)
    
    async def execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific action"""
        task_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        try:
            # Log action start
            await self._log_action(task_id, action, parameters, TaskStatus.RUNNING)
            
            # Execute action
            result = await self._execute_action(action, parameters)
            
            # Calculate execution time
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Log successful completion
            await self._log_action(
                task_id, action, parameters, TaskStatus.COMPLETED,
                output_data=result, execution_time_ms=execution_time
            )
            
            return result
            
        except Exception as e:
            # Log error
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            await self._log_action(
                task_id, action, parameters, TaskStatus.FAILED,
                error_message=str(e), execution_time_ms=execution_time
            )
            raise
    
    async def handle_error(self, error: Exception):
        """Handle agent errors"""
        self.error_count += 1
        
        # Log error
        logger.error(f"Agent error in {self.name}", agent_id=self.agent_id, error=str(error))
        
        # Update status
        if self.error_count > self.max_retries:
            self.status = AgentStatus.ERROR
        else:
            self.status = AgentStatus.IDLE
        
        await self._update_status()
        
        # Store error in memory
        await self._store_memory("error", f"error_{self.error_count}", {
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "cycle_count": self.cycle_count
        })
    
    def update_heartbeat(self):
        """Update agent heartbeat"""
        self.last_heartbeat = datetime.utcnow()
        self.agent_record.last_heartbeat = self.last_heartbeat
    
    def is_healthy(self) -> bool:
        """Check if agent is healthy"""
        if not self.last_heartbeat:
            return False
        
        # Check if heartbeat is within 5 minutes
        return (datetime.utcnow() - self.last_heartbeat).total_seconds() < 300
    
    def is_stuck(self) -> bool:
        """Check if agent appears stuck"""
        if not self.last_cycle_time:
            return False
        
        # Check if last cycle was more than 10 minutes ago
        return (datetime.utcnow() - self.last_cycle_time).total_seconds() > 600
    
    def get_cycle_interval(self) -> int:
        """Get the interval between cycles in seconds"""
        return self.config.get("check_interval", 300)
    
    async def _load_memory(self):
        """Load agent memory from database"""
        db = next(get_db())
        
        try:
            memories = db.query(AgentMemory).filter(
                AgentMemory.agent_id == self.agent_record.id,
                AgentMemory.is_expired() == False
            ).order_by(AgentMemory.importance.desc()).all()
            
            for memory in memories:
                self.memory[memory.key] = memory.value
                
        except Exception as e:
            logger.error(f"Failed to load memory for {self.name}", error=str(e))
        finally:
            db.close()
    
    async def _save_memory(self):
        """Save agent memory to database"""
        db = next(get_db())
        
        try:
            for key, value in self.memory.items():
                # Check if memory already exists
                existing = db.query(AgentMemory).filter(
                    AgentMemory.agent_id == self.agent_record.id,
                    AgentMemory.key == key
                ).first()
                
                if existing:
                    existing.value = value
                    existing.updated_at = datetime.utcnow()
                else:
                    memory = AgentMemory(
                        agent_id=self.agent_record.id,
                        memory_type="context",
                        key=key,
                        value=value,
                        importance=1.0
                    )
                    db.add(memory)
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to save memory for {self.name}", error=str(e))
            db.rollback()
        finally:
            db.close()
    
    async def _store_memory(self, memory_type: str, key: str, value: Any, importance: float = 1.0):
        """Store a memory entry"""
        db = next(get_db())
        
        try:
            memory = AgentMemory(
                agent_id=self.agent_record.id,
                memory_type=memory_type,
                key=key,
                value=value,
                importance=importance
            )
            db.add(memory)
            db.commit()
            
            # Update local memory
            self.memory[key] = value
            
        except Exception as e:
            logger.error(f"Failed to store memory for {self.name}", error=str(e))
            db.rollback()
        finally:
            db.close()
    
    async def _log_action(
        self,
        task_id: str,
        action: str,
        input_data: Dict[str, Any],
        status: TaskStatus,
        output_data: Dict[str, Any] = None,
        error_message: str = None,
        execution_time_ms: int = None,
        reasoning: str = None
    ):
        """Log an agent action"""
        db = next(get_db())
        
        try:
            log = AgentLog(
                agent_id=self.agent_record.id,
                task_id=task_id,
                action=action,
                status=status,
                input_data=input_data,
                output_data=output_data,
                error_message=error_message,
                execution_time_ms=execution_time_ms,
                reasoning=reasoning
            )
            db.add(log)
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to log action for {self.name}", error=str(e))
            db.rollback()
        finally:
            db.close()
    
    async def _update_status(self):
        """Update agent status in database"""
        db = next(get_db())
        
        try:
            self.agent_record.status = self.status
            self.agent_record.tasks_completed = self.tasks_completed
            self.agent_record.tasks_failed = self.tasks_failed
            self.agent_record.average_response_time = self.average_response_time
            self.agent_record.last_heartbeat = self.last_heartbeat
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update status for {self.name}", error=str(e))
            db.rollback()
        finally:
            db.close()
    
    def _update_performance_metrics(self, cycle_duration_ms: float):
        """Update performance metrics"""
        if self.average_response_time == 0:
            self.average_response_time = cycle_duration_ms
        else:
            # Exponential moving average
            self.average_response_time = (
                0.9 * self.average_response_time + 0.1 * cycle_duration_ms
            )
    
    # Abstract methods that must be implemented by subclasses
    @abstractmethod
    async def _initialize_agent(self):
        """Initialize agent-specific components"""
        pass
    
    @abstractmethod
    async def _stop_agent(self):
        """Stop agent-specific components"""
        pass
    
    @abstractmethod
    async def _run_cycle_logic(self):
        """Run agent-specific cycle logic"""
        pass
    
    @abstractmethod
    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific action"""
        pass 