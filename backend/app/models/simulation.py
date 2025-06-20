from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import BaseModel

class EventType(str, Enum):
    WEATHER = "weather"
    TRAFFIC = "traffic"
    DEMAND_SPIKE = "demand_spike"
    SUPPLY_SHORTAGE = "supply_shortage"
    PRICE_CHANGE = "price_change"
    COMPETITION = "competition"
    SPECIAL_EVENT = "special_event"

class SimulationState(BaseModel):
    """Global simulation state"""
    __tablename__ = "simulation_states"
    
    simulation_id = Column(String(50), unique=True, nullable=False, index=True)
    current_time = Column(DateTime, nullable=False)
    tick_count = Column(Integer, default=0)
    is_running = Column(Boolean, default=False)
    speed_multiplier = Column(Float, default=1.0)  # Simulation speed
    config = Column(JSON)  # Simulation configuration
    
    # Market conditions
    weather_condition = Column(String(50))
    traffic_level = Column(String(20))  # low, medium, high
    demand_multiplier = Column(Float, default=1.0)
    supply_multiplier = Column(Float, default=1.0)
    
    # Performance metrics
    total_orders = Column(Integer, default=0)
    completed_deliveries = Column(Integer, default=0)
    failed_deliveries = Column(Integer, default=0)
    average_delivery_time = Column(Float, default=0.0)
    
    def advance_time(self, minutes: int = 15):
        """Advance simulation time"""
        from datetime import timedelta
        self.current_time += timedelta(minutes=minutes)
        self.tick_count += 1
    
    def update_market_conditions(self, **conditions):
        """Update market conditions"""
        for key, value in conditions.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def get_market_summary(self) -> dict:
        """Get current market summary"""
        return {
            "current_time": self.current_time.isoformat(),
            "tick_count": self.tick_count,
            "weather": self.weather_condition,
            "traffic": self.traffic_level,
            "demand_multiplier": self.demand_multiplier,
            "supply_multiplier": self.supply_multiplier,
            "total_orders": self.total_orders,
            "completed_deliveries": self.completed_deliveries,
            "success_rate": (self.completed_deliveries / max(1, self.total_orders)) * 100
        }

class MarketEvent(BaseModel):
    """Market events that affect simulation"""
    __tablename__ = "market_events"
    
    event_type = Column(String(50), nullable=False)  # EventType
    title = Column(String(200), nullable=False)
    description = Column(Text)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    affected_sectors = Column(JSON)  # List of affected city sectors
    impact_data = Column(JSON)  # Event-specific impact data
    is_active = Column(Boolean, default=True)
    
    # Event effects
    demand_effect = Column(Float, default=1.0)  # Multiplier for demand
    supply_effect = Column(Float, default=1.0)  # Multiplier for supply
    traffic_effect = Column(Float, default=1.0)  # Multiplier for delivery times
    price_effect = Column(Float, default=1.0)  # Multiplier for prices
    
    def is_current(self, current_time: datetime) -> bool:
        """Check if event is currently active"""
        if not self.is_active:
            return False
        if current_time < self.start_time:
            return False
        if self.end_time and current_time > self.end_time:
            return False
        return True
    
    def get_impact_summary(self) -> dict:
        """Get event impact summary"""
        return {
            "event_type": self.event_type,
            "title": self.title,
            "severity": self.severity,
            "demand_effect": self.demand_effect,
            "supply_effect": self.supply_effect,
            "traffic_effect": self.traffic_effect,
            "price_effect": self.price_effect,
            "affected_sectors": self.affected_sectors
        } 