"""
Simulation models for the logistics system
"""

import enum
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field

from .base import Base, BaseModelMixin

# Define enum values
class SimulationStatus:
    STOPPED = 'stopped'
    RUNNING = 'running'
    PAUSED = 'paused'
    ERROR = 'error'

class EventType:
    TICK_START = 'tick_start'
    TICK_END = 'tick_end'
    AGENT_ACTION = 'agent_action'
    ORDER_CREATED = 'order_created'
    ORDER_ASSIGNED = 'order_assigned'
    ORDER_DELIVERED = 'order_delivered'
    INVENTORY_UPDATE = 'inventory_update'
    PRICE_CHANGE = 'price_change'
    ROUTE_UPDATE = 'route_update'
    VEHICLE_UPDATE = 'vehicle_update'
    FORECAST_GENERATED = 'forecast_generated'
    ERROR = 'error'

# Create enum types
simulation_status_enum = Enum(
    SimulationStatus.STOPPED,
    SimulationStatus.RUNNING,
    SimulationStatus.PAUSED,
    SimulationStatus.ERROR,
    name='simulation_status'
)

event_type_enum = Enum(
    EventType.TICK_START,
    EventType.TICK_END,
    EventType.AGENT_ACTION,
    EventType.ORDER_CREATED,
    EventType.ORDER_ASSIGNED,
    EventType.ORDER_DELIVERED,
    EventType.INVENTORY_UPDATE,
    EventType.PRICE_CHANGE,
    EventType.ROUTE_UPDATE,
    EventType.VEHICLE_UPDATE,
    EventType.FORECAST_GENERATED,
    EventType.ERROR,
    name='event_type'
)

class SimulationState(Base):
    """Simulation state model"""
    
    __tablename__ = "simulation_state"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(simulation_status_enum, default='stopped', nullable=False)
    current_tick = Column(Integer, default=0, nullable=False)
    start_time = Column(DateTime(timezone=True))
    last_tick_time = Column(DateTime(timezone=True))
    speed_multiplier = Column(Float, default=1.0)
    config = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    events = relationship("SimulationEvent", back_populates="simulation_state")
    
    def __init__(self, config: Dict[str, Any] = None, **kwargs):
        super().__init__(**kwargs)
        self.status = 'stopped'
        self.current_tick = 0
        self.config = config or {}
    
    def start(self):
        """Start simulation"""
        self.status = 'running'
        self.start_time = datetime.utcnow()
        self.last_tick_time = datetime.utcnow()
    
    def stop(self):
        """Stop simulation"""
        self.status = 'stopped'
    
    def pause(self):
        """Pause simulation"""
        self.status = 'paused'
    
    def advance_tick(self):
        """Advance to next tick"""
        self.current_tick += 1
        self.last_tick_time = datetime.utcnow()
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default) if self.config else default
    
    def update_config(self, key: str, value: Any):
        """Update configuration"""
        if not self.config:
            self.config = {}
        self.config[key] = value
    
    def get_runtime(self) -> Optional[float]:
        """Get simulation runtime in seconds"""
        if self.start_time and self.last_tick_time:
            return (self.last_tick_time - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'status': self.status,
            'current_tick': self.current_tick,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_tick_time': self.last_tick_time.isoformat() if self.last_tick_time else None,
            'speed_multiplier': self.speed_multiplier,
            'config': self.config,
            'runtime_seconds': self.get_runtime(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self) -> str:
        return f"<SimulationState(id={self.id}, status='{self.status}', tick={self.current_tick})>"
    
    def is_running(self) -> bool:
        """Check if simulation is running"""
        return self.status == SimulationStatus.RUNNING
    
    def is_paused(self) -> bool:
        """Check if simulation is paused"""
        return self.status == SimulationStatus.PAUSED
    
    def can_start(self) -> bool:
        """Check if simulation can be started"""
        return self.status in [SimulationStatus.STOPPED, SimulationStatus.ERROR]
    
    def can_stop(self) -> bool:
        """Check if simulation can be stopped"""
        return self.status in [SimulationStatus.RUNNING, SimulationStatus.PAUSED]
    
    def can_pause(self) -> bool:
        """Check if simulation can be paused"""
        return self.status == SimulationStatus.RUNNING
    
    def can_resume(self) -> bool:
        """Check if simulation can be resumed"""
        return self.status == SimulationStatus.PAUSED
    
    def update_status(self, status: SimulationStatus) -> None:
        """Update simulation status"""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if status == SimulationStatus.RUNNING and not self.start_time:
            self.start_time = datetime.utcnow()
    
    def reset(self) -> None:
        """Reset simulation to initial state"""
        self.current_tick = 0
        self.start_time = None
        self.last_tick_time = None
        self.status = SimulationStatus.STOPPED
        self.updated_at = datetime.utcnow()


class SimulationEvent(Base):
    """Simulation event model for tracking all simulation activities"""
    
    __tablename__ = "simulation_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tick_number = Column(Integer, nullable=False, index=True)
    event_type = Column(event_type_enum, nullable=False, index=True)
    event_data = Column(JSON, default={})
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    simulation_state_id = Column(UUID(as_uuid=True), ForeignKey('simulation_state.id'))
    simulation_state = relationship("SimulationState", back_populates="events")
    
    def __repr__(self):
        return f"<SimulationEvent(id={self.id}, tick={self.tick_number}, type='{self.event_type}')>"
    
    def get_data_value(self, key: str, default: Any = None) -> Any:
        """Get event data value"""
        return self.event_data.get(key, default)
    
    def set_data_value(self, key: str, value: Any) -> None:
        """Set event data value"""
        if not self.event_data:
            self.event_data = {}
        self.event_data[key] = value
        self.updated_at = datetime.utcnow()


# Pydantic schemas
class SimulationStateBase(BaseModel):
    """Base simulation state schema"""
    status: str = Field(..., description="Simulation status")
    current_tick: int = Field(..., description="Current tick number")
    speed_multiplier: float = Field(..., description="Simulation speed multiplier")
    config: Dict[str, Any] = Field(default={}, description="Simulation configuration")


class SimulationStateCreate(SimulationStateBase):
    """Schema for creating simulation state"""
    pass


class SimulationStateUpdate(BaseModel):
    """Schema for updating simulation state"""
    status: Optional[str] = Field(None, description="Simulation status")
    speed_multiplier: Optional[float] = Field(None, description="Simulation speed multiplier")
    config: Optional[Dict[str, Any]] = Field(None, description="Simulation configuration")


class SimulationStateResponse(SimulationStateBase):
    """Schema for simulation state responses"""
    id: str = Field(..., description="Simulation state ID")
    start_time: Optional[datetime] = Field(None, description="Simulation start time")
    last_tick_time: Optional[datetime] = Field(None, description="Last tick time")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class SimulationEventBase(BaseModel):
    """Base simulation event schema"""
    tick_number: int = Field(..., description="Tick number")
    event_type: str = Field(..., description="Event type")
    event_data: Dict[str, Any] = Field(default={}, description="Event data")


class SimulationEventCreate(SimulationEventBase):
    """Schema for creating simulation event"""
    pass


class SimulationEventResponse(SimulationEventBase):
    """Schema for simulation event responses"""
    id: str = Field(..., description="Event ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class SimulationControl(BaseModel):
    """Schema for simulation control commands"""
    action: str = Field(..., description="Control action (start, stop, pause, resume, reset)")
    speed_multiplier: Optional[float] = Field(None, description="Speed multiplier for start action")


class SimulationStatusResponse(BaseModel):
    """Schema for simulation status response"""
    is_running: bool = Field(..., description="Whether simulation is running")
    current_tick: int = Field(..., description="Current tick number")
    total_ticks: int = Field(..., description="Total ticks since start")
    speed_multiplier: float = Field(..., description="Current speed multiplier")
    start_time: Optional[datetime] = Field(None, description="Simulation start time")
    last_tick_time: Optional[datetime] = Field(None, description="Last tick time")
    uptime_seconds: Optional[int] = Field(None, description="Uptime in seconds")
    status: str = Field(..., description="Current status")


class SimulationMetrics(BaseModel):
    """Schema for simulation metrics"""
    total_events: int = Field(..., description="Total events generated")
    events_by_type: Dict[str, int] = Field(..., description="Event count by type")
    avg_events_per_tick: float = Field(..., description="Average events per tick")
    total_runtime_seconds: int = Field(..., description="Total runtime in seconds")
    ticks_per_second: float = Field(..., description="Ticks processed per second")
    error_count: int = Field(..., description="Number of errors")
    last_error: Optional[str] = Field(None, description="Last error message")


class SimulationSummary(BaseModel):
    """Schema for simulation summary"""
    status: str = Field(..., description="Current status")
    current_tick: int = Field(..., description="Current tick")
    total_events: int = Field(..., description="Total events")
    active_agents: int = Field(..., description="Active agents")
    pending_orders: int = Field(..., description="Pending orders")
    available_vehicles: int = Field(..., description="Available vehicles")
    low_stock_items: int = Field(..., description="Low stock items") 