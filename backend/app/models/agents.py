"""
Agent models for autonomous agent system
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Text, JSON, DateTime, Enum, Float, Boolean, UUID, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
import enum

from app.models.base import BaseModelMixin, Base
from app.core.database import Base


class AgentStatus(str, enum.Enum):
    """Agent status enumeration"""
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


class AgentType(str, enum.Enum):
    """Agent type enumeration"""
    RESTOCK = "restock"
    ROUTE = "route"
    PRICING = "pricing"
    DISPATCH = "dispatch"
    FORECASTING = "forecasting"


class ActionType(str, enum.Enum):
    """Agentic action type enumeration"""
    PLACE_ORDER = "place_order"
    REROUTE_DRIVER = "reroute_driver"
    UPDATE_INVENTORY = "update_inventory"
    ADJUST_PRICING = "adjust_pricing"
    DISPATCH_FLEET = "dispatch_fleet"
    FORECAST_DEMAND = "forecast_demand"
    ANALYZE_PERFORMANCE = "analyze_performance"


class ApprovalStatus(str, enum.Enum):
    """Action approval status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    AUTO_APPROVED = "auto_approved"


class Agent(Base, BaseModelMixin):
    """Agent model for autonomous agents"""
    
    name = Column(String(100), nullable=False, index=True)
    agent_type = Column(Enum(AgentType), nullable=False, index=True)
    status = Column(Enum(AgentStatus), default=AgentStatus.STOPPED, index=True)
    config = Column(JSON, default={})
    memory = Column(JSON, default={})
    last_cycle = Column(DateTime)
    
    # Relationships
    logs = relationship("AgentLog", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name='{self.name}', type='{self.agent_type}', status='{self.status}')>"
    
    def is_active(self) -> bool:
        """Check if agent is active"""
        return self.status in [AgentStatus.RUNNING, AgentStatus.STARTING]
    
    def can_start(self) -> bool:
        """Check if agent can be started"""
        return self.status in [AgentStatus.STOPPED, AgentStatus.ERROR]
    
    def can_stop(self) -> bool:
        """Check if agent can be stopped"""
        return self.status in [AgentStatus.RUNNING, AgentStatus.STARTING]
    
    def update_status(self, status: AgentStatus) -> None:
        """Update agent status"""
        self.status = status
        self.updated_at = datetime.utcnow()
    
    def update_memory(self, memory_data: Dict[str, Any]) -> None:
        """Update agent memory"""
        if not self.memory:
            self.memory = {}
        self.memory.update(memory_data)
        self.updated_at = datetime.utcnow()
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set_config_value(self, key: str, value: Any) -> None:
        """Set configuration value"""
        if not self.config:
            self.config = {}
        self.config[key] = value
        self.updated_at = datetime.utcnow()


class AgentLog(Base, BaseModelMixin):
    """Agent log model for tracking agent activities"""
    
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agent.id"), nullable=False, index=True)
    level = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    context = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="logs")
    
    def __repr__(self):
        return f"<AgentLog(id={self.id}, agent_id='{self.agent_id}', level='{self.level}', message='{self.message[:50]}...')>"


class AgenticAction(Base, BaseModelMixin):
    """Agentic action model for tracking autonomous decisions"""
    
    action_id = Column(String(100), nullable=False, unique=True, index=True)
    action_type = Column(Enum(ActionType), nullable=False, index=True)
    parameters = Column(JSON, nullable=False)
    reasoning = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    estimated_impact = Column(JSON, default={})
    approval_required = Column(Boolean, default=True, index=True)
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, index=True)
    executed = Column(Boolean, default=False, index=True)
    execution_result = Column(JSON, default={})
    error_message = Column(Text, nullable=True)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<AgenticAction(id={self.id}, action_id='{self.action_id}', type='{self.action_type}', status='{self.approval_status}')>"
    
    def approve(self, approved_by: str) -> None:
        """Approve the action"""
        self.approval_status = ApprovalStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def deny(self, denied_by: str) -> None:
        """Deny the action"""
        self.approval_status = ApprovalStatus.DENIED
        self.approved_by = denied_by
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def auto_approve(self) -> None:
        """Auto-approve the action"""
        self.approval_status = ApprovalStatus.AUTO_APPROVED
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def execute(self, result: Dict[str, Any]) -> None:
        """Mark action as executed"""
        self.executed = True
        self.execution_result = result
        self.updated_at = datetime.utcnow()
    
    def fail(self, error_message: str) -> None:
        """Mark action as failed"""
        self.executed = True
        self.error_message = error_message
        self.updated_at = datetime.utcnow()


class AgenticMemory(Base, BaseModelMixin):
    """Agentic memory model for storing conversation and context"""
    
    memory_type = Column(String(50), nullable=False, index=True)
    key = Column(String(100), nullable=False, index=True)
    value = Column(JSON, nullable=False)
    importance = Column(Float, default=1.0)
    expires_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<AgenticMemory(id={self.id}, type='{self.memory_type}', key='{self.key}')>"
    
    def is_expired(self) -> bool:
        """Check if memory is expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


# Pydantic schemas
class AgentBase(BaseModel):
    """Base agent schema"""
    name: str = Field(..., description="Agent name")
    agent_type: AgentType = Field(..., description="Agent type")
    config: Dict[str, Any] = Field(default={}, description="Agent configuration")


class AgentCreate(AgentBase):
    """Schema for creating an agent"""
    pass


class AgentUpdate(BaseModel):
    """Schema for updating an agent"""
    name: Optional[str] = Field(None, description="Agent name")
    config: Optional[Dict[str, Any]] = Field(None, description="Agent configuration")
    status: Optional[AgentStatus] = Field(None, description="Agent status")


class AgentResponse(AgentBase):
    """Schema for agent responses"""
    id: str = Field(..., description="Agent ID")
    status: AgentStatus = Field(..., description="Agent status")
    memory: Dict[str, Any] = Field(default={}, description="Agent memory")
    last_cycle: Optional[datetime] = Field(None, description="Last cycle timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class AgentLogBase(BaseModel):
    """Base agent log schema"""
    level: str = Field(..., description="Log level")
    message: str = Field(..., description="Log message")
    context: Dict[str, Any] = Field(default={}, description="Log context")


class AgentLogCreate(AgentLogBase):
    """Schema for creating an agent log"""
    agent_id: str = Field(..., description="Agent ID")


class AgentLogResponse(AgentLogBase):
    """Schema for agent log responses"""
    id: str = Field(..., description="Log ID")
    agent_id: str = Field(..., description="Agent ID")
    timestamp: datetime = Field(..., description="Log timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class AgenticActionBase(BaseModel):
    """Base agentic action schema"""
    action_type: ActionType = Field(..., description="Action type")
    parameters: Dict[str, Any] = Field(..., description="Action parameters")
    reasoning: Optional[str] = Field(None, description="Reasoning for the action")
    confidence: float = Field(default=0.0, description="Confidence score")
    estimated_impact: Dict[str, Any] = Field(default={}, description="Estimated impact")


class AgenticActionCreate(AgenticActionBase):
    """Schema for creating an agentic action"""
    action_id: str = Field(..., description="Unique action ID")
    approval_required: bool = Field(default=True, description="Whether approval is required")


class AgenticActionResponse(AgenticActionBase):
    """Schema for agentic action responses"""
    id: str = Field(..., description="Action ID")
    action_id: str = Field(..., description="Unique action ID")
    approval_status: ApprovalStatus = Field(..., description="Approval status")
    executed: bool = Field(..., description="Whether action was executed")
    execution_result: Dict[str, Any] = Field(default={}, description="Execution result")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    approved_by: Optional[str] = Field(None, description="Who approved/denied the action")
    approved_at: Optional[datetime] = Field(None, description="When action was approved/denied")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class AgenticActionApproval(BaseModel):
    """Schema for action approval"""
    approved_by: str = Field(..., description="Who is approving the action")
    notes: Optional[str] = Field(None, description="Approval notes")


class AgenticActionDenial(BaseModel):
    """Schema for action denial"""
    denied_by: str = Field(..., description="Who is denying the action")
    reason: str = Field(..., description="Reason for denial")


class AgenticMemoryBase(BaseModel):
    """Base agentic memory schema"""
    memory_type: str = Field(..., description="Memory type")
    key: str = Field(..., description="Memory key")
    value: Dict[str, Any] = Field(..., description="Memory value")
    importance: float = Field(default=1.0, description="Memory importance")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")


class AgenticMemoryCreate(AgenticMemoryBase):
    """Schema for creating agentic memory"""
    pass


class AgenticMemoryResponse(AgenticMemoryBase):
    """Schema for agentic memory responses"""
    id: str = Field(..., description="Memory ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class AgentStatusUpdate(BaseModel):
    """Schema for agent status updates"""
    status: AgentStatus = Field(..., description="New agent status")


class AgentConfigUpdate(BaseModel):
    """Schema for agent configuration updates"""
    config: Dict[str, Any] = Field(..., description="New agent configuration")


class AgentMemoryUpdate(BaseModel):
    """Schema for agent memory updates"""
    memory: Dict[str, Any] = Field(..., description="New agent memory")


class AgentPerformance(BaseModel):
    """Schema for agent performance metrics"""
    agent_id: str = Field(..., description="Agent ID")
    total_cycles: int = Field(..., description="Total cycles executed")
    success_rate: float = Field(..., description="Success rate (0-1)")
    avg_cycle_time: float = Field(..., description="Average cycle time in seconds")
    error_count: int = Field(..., description="Number of errors")
    last_error: Optional[str] = Field(None, description="Last error message")
    uptime_seconds: int = Field(..., description="Total uptime in seconds")


class AgentSummary(BaseModel):
    """Schema for agent summary"""
    total_agents: int = Field(..., description="Total number of agents")
    active_agents: int = Field(..., description="Number of active agents")
    agents_by_type: Dict[str, int] = Field(..., description="Agent count by type")
    agents_by_status: Dict[str, int] = Field(..., description="Agent count by status")


class AgenticSystemStatus(BaseModel):
    """Schema for agentic system status"""
    status: str = Field(..., description="System status")
    simulation_mode: bool = Field(..., description="Whether simulation mode is enabled")
    tools_available: int = Field(..., description="Number of available tools")
    pending_actions: int = Field(..., description="Number of pending actions")
    approved_actions: int = Field(..., description="Number of approved actions")
    denied_actions: int = Field(..., description="Number of denied actions")
    memory_size: int = Field(..., description="Size of conversation memory")


class AgenticActionSummary(BaseModel):
    """Schema for agentic action summary"""
    total_actions: int = Field(..., description="Total number of actions")
    pending_actions: int = Field(..., description="Number of pending actions")
    approved_actions: int = Field(..., description="Number of approved actions")
    denied_actions: int = Field(..., description="Number of denied actions")
    auto_approved_actions: int = Field(..., description="Number of auto-approved actions")
    actions_by_type: Dict[str, int] = Field(..., description="Action count by type") 