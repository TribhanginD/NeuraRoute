"""
Logging models for system monitoring
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Integer, DateTime, JSON, Numeric, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from .base import BaseModel


class SimulationLog(BaseModel):
    """Simulation log model for tracking simulation ticks"""
    
    __tablename__ = "simulation_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tick_number = Column(Integer, nullable=False, index=True)
    events_processed = Column(Integer, default=0)
    agents_active = Column(Integer, default=0)
    duration_ms = Column(Integer)
    status = Column(String(50), default='success')
    
    def __init__(self, tick_number: int, events_processed: int = 0, agents_active: int = 0,
                 duration_ms: int = None, status: str = 'success', **kwargs):
        super().__init__(**kwargs)
        self.tick_number = tick_number
        self.events_processed = events_processed
        self.agents_active = agents_active
        self.duration_ms = duration_ms
        self.status = status
    
    def get_duration_seconds(self) -> float:
        """Get duration in seconds"""
        return self.duration_ms / 1000.0 if self.duration_ms else 0.0
    
    def is_successful(self) -> bool:
        """Check if tick was successful"""
        return self.status == 'success'
    
    def get_efficiency_score(self) -> float:
        """Get efficiency score based on events processed and duration"""
        if self.duration_ms and self.duration_ms > 0:
            return self.events_processed / (self.duration_ms / 1000.0)
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        base_dict['duration_seconds'] = self.get_duration_seconds()
        base_dict['is_successful'] = self.is_successful()
        base_dict['efficiency_score'] = self.get_efficiency_score()
        return base_dict
    
    def __repr__(self) -> str:
        return f"<SimulationLog(id={self.id}, tick={self.tick_number}, events={self.events_processed}, status='{self.status}')>"


class PerformanceMetric(BaseModel):
    """Performance metric model for system monitoring"""
    
    __tablename__ = "performance_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Numeric(15, 4), nullable=False)
    metric_unit = Column(String(20))
    tags = Column(JSON, default={})
    recorded_at = Column(DateTime(timezone=True), server_default='now()')
    
    def __init__(self, metric_name: str, metric_value: float, metric_unit: str = None,
                 tags: Dict[str, Any] = None, **kwargs):
        super().__init__(**kwargs)
        self.metric_name = metric_name
        self.metric_value = metric_value
        self.metric_unit = metric_unit
        self.tags = tags or {}
    
    def get_tag_value(self, key: str, default: Any = None) -> Any:
        """Get tag value"""
        return self.tags.get(key, default)
    
    def set_tag_value(self, key: str, value: Any):
        """Set tag value"""
        if not self.tags:
            self.tags = {}
        self.tags[key] = value
    
    def is_above_threshold(self, threshold: float) -> bool:
        """Check if metric is above threshold"""
        return float(self.metric_value) > threshold
    
    def is_below_threshold(self, threshold: float) -> bool:
        """Check if metric is below threshold"""
        return float(self.metric_value) < threshold
    
    def get_formatted_value(self) -> str:
        """Get formatted metric value with unit"""
        if self.metric_unit:
            return f"{self.metric_value} {self.metric_unit}"
        return str(self.metric_value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        base_dict['formatted_value'] = self.get_formatted_value()
        return base_dict
    
    def __repr__(self) -> str:
        return f"<PerformanceMetric(id={self.id}, name='{self.metric_name}', value={self.metric_value}, unit='{self.metric_unit}')>" 