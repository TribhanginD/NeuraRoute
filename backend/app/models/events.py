"""
Event model for system events
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Text, DateTime, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import BaseModel

# Import enum types
from sqlalchemy import Enum as SQLEnum
event_type_enum = SQLEnum('event_type', name='event_type')


class Event(BaseModel):
    """Event model for system events"""
    
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(event_type_enum, nullable=False)
    severity = Column(String(20), default='medium', nullable=False)
    description = Column(Text)
    location_lat = Column(Numeric(10, 8))
    location_lng = Column(Numeric(11, 8))
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    impact_data = Column(JSON, default={})
    
    def __init__(self, event_type: str, description: str = None, severity: str = 'medium',
                 location_lat: float = None, location_lng: float = None,
                 start_time: datetime = None, end_time: datetime = None,
                 impact_data: Dict[str, Any] = None, **kwargs):
        super().__init__(**kwargs)
        self.event_type = event_type
        self.description = description
        self.severity = severity
        self.location_lat = location_lat
        self.location_lng = location_lng
        self.start_time = start_time or datetime.utcnow()
        self.end_time = end_time
        self.impact_data = impact_data or {}
    
    def is_active(self) -> bool:
        """Check if event is currently active"""
        now = datetime.utcnow()
        return (self.start_time <= now and 
                (self.end_time is None or now <= self.end_time))
    
    def is_high_severity(self) -> bool:
        """Check if event is high severity"""
        return self.severity in ['high', 'critical']
    
    def is_weather_event(self) -> bool:
        """Check if event is weather-related"""
        return self.event_type == 'weather'
    
    def is_traffic_event(self) -> bool:
        """Check if event is traffic-related"""
        return self.event_type == 'traffic'
    
    def is_demand_event(self) -> bool:
        """Check if event is demand-related"""
        return self.event_type == 'demand_spike'
    
    def get_impact_score(self) -> float:
        """Get impact score from impact data"""
        return self.impact_data.get('score', 0.0)
    
    def get_affected_area(self) -> Dict[str, Any]:
        """Get affected area information"""
        return self.impact_data.get('affected_area', {})
    
    def get_duration_hours(self) -> float:
        """Get event duration in hours"""
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds() / 3600
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        base_dict['is_active'] = self.is_active()
        base_dict['is_high_severity'] = self.is_high_severity()
        base_dict['is_weather_event'] = self.is_weather_event()
        base_dict['is_traffic_event'] = self.is_traffic_event()
        base_dict['is_demand_event'] = self.is_demand_event()
        base_dict['impact_score'] = self.get_impact_score()
        base_dict['affected_area'] = self.get_affected_area()
        base_dict['duration_hours'] = self.get_duration_hours()
        return base_dict
    
    def __repr__(self) -> str:
        return f"<Event(id={self.id}, type='{self.event_type}', severity='{self.severity}', active={self.is_active()})>" 