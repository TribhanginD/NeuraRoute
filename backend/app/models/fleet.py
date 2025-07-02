from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import BaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid
from typing import Dict, Any, Optional, List

class VehicleStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class RouteStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"

class Vehicle(BaseModel):
    """Vehicle model for fleet management"""
    __tablename__ = "vehicles"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    vehicle_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    vehicle_type = Column(String(50), nullable=False)  # truck, van, bike, etc.
    capacity_kg = Column(Float, nullable=False)
    capacity_m3 = Column(Float, nullable=False)
    current_lat = Column(Float)
    current_lng = Column(Float)
    status = Column(String(20), default=VehicleStatus.AVAILABLE)  # VehicleStatus
    
    # Performance metrics
    total_distance_km = Column(Float, default=0.0)
    total_deliveries = Column(Integer, default=0)
    average_speed_kmh = Column(Float, default=30.0)
    fuel_efficiency = Column(Float)  # km/liter
    
    # Current load
    current_load_kg = Column(Float, default=0.0)
    current_route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"))
    current_location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"))
    
    # Relationships
    current_location = relationship("Location", back_populates="vehicles", foreign_keys=[current_location_id])
    current_route = relationship("Route", foreign_keys=[current_route_id])
    deliveries = relationship("Delivery", back_populates="vehicle")
    
    def is_available(self) -> bool:
        """Check if vehicle is available for new assignments"""
        return self.status == VehicleStatus.AVAILABLE and self.current_load_kg < self.capacity_kg
    
    def add_load(self, weight_kg: float) -> bool:
        """Add load to vehicle"""
        if self.current_load_kg + weight_kg <= self.capacity_kg:
            self.current_load_kg += weight_kg
            return True
        return False
    
    def remove_load(self, weight_kg: float):
        """Remove load from vehicle"""
        self.current_load_kg = max(0.0, self.current_load_kg - weight_kg)

class Route(BaseModel):
    """Route model for delivery optimization"""
    __tablename__ = "routes"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    route_id = Column(String(50), unique=True, nullable=False, index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"))
    status = Column(String(20), default=RouteStatus.PLANNED)  # RouteStatus
    
    # Route details
    start_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    end_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    waypoints = Column(JSON)  # List of intermediate locations
    estimated_distance_km = Column(Float)
    estimated_duration_minutes = Column(Integer)
    
    # Timing
    planned_start_time = Column(DateTime)
    actual_start_time = Column(DateTime)
    planned_end_time = Column(DateTime)
    actual_end_time = Column(DateTime)
    
    # Optimization data
    optimization_score = Column(Float)  # Route efficiency score
    traffic_factor = Column(Float, default=1.0)
    weather_factor = Column(Float, default=1.0)
    
    # Relationships
    # vehicle = relationship("Vehicle", back_populates="current_route", foreign_keys=[vehicle_id])
    start_location = relationship("Location", foreign_keys=[start_location_id])
    end_location = relationship("Location", foreign_keys=[end_location_id])
    deliveries = relationship("Delivery", back_populates="route")
    
    def calculate_actual_duration(self) -> int:
        """Calculate actual route duration in minutes"""
        if self.actual_start_time and self.actual_end_time:
            duration = self.actual_end_time - self.actual_start_time
            return int(duration.total_seconds() / 60)
        return 0
    
    def update_status(self, status: RouteStatus):
        """Update route status"""
        self.status = status
        if status == RouteStatus.IN_PROGRESS and not self.actual_start_time:
            self.actual_start_time = datetime.utcnow()
        elif status == RouteStatus.COMPLETED and not self.actual_end_time:
            self.actual_end_time = datetime.utcnow()

class Delivery(BaseModel):
    """Delivery model for order fulfillment"""
    __tablename__ = "deliveries"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    delivery_id = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"))
    route_id = Column(UUID(as_uuid=True), ForeignKey("routes.id"))
    
    # Delivery details
    pickup_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    delivery_location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    status = Column(String(20), default=DeliveryStatus.PENDING)  # DeliveryStatus
    
    # Timing
    requested_pickup_time = Column(DateTime)
    actual_pickup_time = Column(DateTime)
    requested_delivery_time = Column(DateTime)
    actual_delivery_time = Column(DateTime)
    
    # Package details
    weight_kg = Column(Float, nullable=False)
    volume_m3 = Column(Float)
    special_instructions = Column(Text)
    
    # Performance metrics
    distance_km = Column(Float)
    duration_minutes = Column(Integer)
    customer_rating = Column(Integer)  # 1-5 stars
    
    # Relationships
    order = relationship("Order")
    vehicle = relationship("Vehicle", back_populates="deliveries")
    route = relationship("Route", back_populates="deliveries")
    pickup_location = relationship("Location", foreign_keys=[pickup_location_id])
    delivery_location = relationship("Location", foreign_keys=[delivery_location_id])
    
    def calculate_duration(self) -> int:
        """Calculate actual delivery duration in minutes"""
        if self.actual_pickup_time and self.actual_delivery_time:
            duration = self.actual_delivery_time - self.actual_pickup_time
            return int(duration.total_seconds() / 60)
        return 0
    
    def update_status(self, status: DeliveryStatus):
        """Update delivery status"""
        self.status = status
        if status == DeliveryStatus.PICKED_UP and not self.actual_pickup_time:
            self.actual_pickup_time = datetime.utcnow()
        elif status == DeliveryStatus.DELIVERED and not self.actual_delivery_time:
            self.actual_delivery_time = datetime.utcnow()
            self.duration_minutes = self.calculate_duration()

class Fleet(BaseModel):
    """Fleet model for vehicle management"""
    
    __tablename__ = "fleet"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(String(100), unique=True, nullable=False, index=True)
    vehicle_type = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    current_location_lat = Column(Numeric(10, 8))
    current_location_lng = Column(Numeric(11, 8))
    status = Column(String(50), default='available', nullable=False)
    fuel_level = Column(Numeric(5, 2), default=100.0)
    last_maintenance = Column(DateTime(timezone=True))
    
    def __init__(self, vehicle_id: str, vehicle_type: str, capacity: int,
                 current_location_lat: float = None, current_location_lng: float = None, **kwargs):
        super().__init__(**kwargs)
        self.vehicle_id = vehicle_id
        self.vehicle_type = vehicle_type
        self.capacity = capacity
        self.current_location_lat = current_location_lat
        self.current_location_lng = current_location_lng
        self.status = 'available'
        self.fuel_level = 100.0
    
    def update_location(self, lat: float, lng: float):
        """Update vehicle location"""
        self.current_location_lat = lat
        self.current_location_lng = lng
    
    def update_status(self, status: str):
        """Update vehicle status"""
        self.status = status
    
    def update_fuel_level(self, level: float):
        """Update fuel level"""
        if 0 <= level <= 100:
            self.fuel_level = level
    
    def needs_maintenance(self) -> bool:
        """Check if vehicle needs maintenance"""
        if not self.last_maintenance:
            return True
        
        # Check if maintenance is due (every 7 days)
        days_since_maintenance = (datetime.utcnow() - self.last_maintenance).days
        return days_since_maintenance >= 7
    
    def is_available(self) -> bool:
        """Check if vehicle is available for use"""
        return self.status == 'available' and self.fuel_level > 10.0
    
    def get_utilization_ratio(self) -> float:
        """Get vehicle utilization ratio"""
        # This would be calculated based on actual usage data
        return 0.0  # Placeholder
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        base_dict['is_available'] = self.is_available()
        base_dict['needs_maintenance'] = self.needs_maintenance()
        base_dict['utilization_ratio'] = self.get_utilization_ratio()
        return base_dict
    
    def __repr__(self) -> str:
        return f"<Fleet(id={self.id}, vehicle_id='{self.vehicle_id}', type='{self.vehicle_type}', status='{self.status}')>" 