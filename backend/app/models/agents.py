from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import BaseModel

class AgentType(str, Enum):
    RESTOCK = "restock"
    ROUTE = "route"
    PRICING = "pricing"
    DISPATCH = "dispatch"
    FORECASTING = "forecasting"

class AgentStatus(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Agent(BaseModel):
    """Autonomous agent model"""
    __tablename__ = "agents"
    
    agent_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    agent_type = Column(String(20), nullable=False)  # AgentType
    status = Column(String(20), default=AgentStatus.IDLE)  # AgentStatus
    current_task = Column(String(100))
    last_heartbeat = Column(DateTime)
    config = Column(JSON)  # Agent-specific configuration
    is_active = Column(Boolean, default=True)
    
    # Performance metrics
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    average_response_time = Column(Float, default=0.0)
    
    # Relationships
    logs = relationship("AgentLog", back_populates="agent")
    memories = relationship("AgentMemory", back_populates="agent")
    
    def update_heartbeat(self):
        """Update agent heartbeat"""
        self.last_heartbeat = datetime.utcnow()
    
    def is_healthy(self) -> bool:
        """Check if agent is healthy (heartbeat within 5 minutes)"""
        if not self.last_heartbeat:
            return False
        return (datetime.utcnow() - self.last_heartbeat).total_seconds() < 300

class AgentLog(BaseModel):
    """Agent activity log"""
    __tablename__ = "agent_logs"
    
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    task_id = Column(String(100))
    action = Column(String(100), nullable=False)
    status = Column(String(20), default=TaskStatus.PENDING)  # TaskStatus
    input_data = Column(JSON)
    output_data = Column(JSON)
    reasoning = Column(Text)  # AI reasoning for the action
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    retry_count = Column(Integer, default=0)
    
    # Relationships
    agent = relationship("Agent", back_populates="logs")
    
    def log_reasoning(self, reasoning: str):
        """Log AI reasoning for the action"""
        self.reasoning = reasoning
    
    def log_error(self, error: str):
        """Log error message"""
        self.error_message = error
        self.status = TaskStatus.FAILED
    
    def mark_completed(self, output_data: dict = None, execution_time_ms: int = None):
        """Mark task as completed"""
        self.status = TaskStatus.COMPLETED
        if output_data:
            self.output_data = output_data
        if execution_time_ms:
            self.execution_time_ms = execution_time_ms

class AgentMemory(BaseModel):
    """Agent memory for context and learning"""
    __tablename__ = "agent_memories"
    
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    memory_type = Column(String(50), nullable=False)  # context, learning, experience
    key = Column(String(100), nullable=False)
    value = Column(JSON)
    importance = Column(Float, default=1.0)  # Memory importance score
    expires_at = Column(DateTime)
    
    # Relationships
    agent = relationship("Agent", back_populates="memories")
    
    def is_expired(self) -> bool:
        """Check if memory has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def update_importance(self, importance: float):
        """Update memory importance score"""
        self.importance = max(0.0, min(1.0, importance)) 