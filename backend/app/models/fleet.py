from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import BaseModel

class VehicleStatus(str, Enum):
    AVAILABLE = "available"
    IN_TRANSIT = "in_transit"
    LOADING = "loading"
    UNLOADING = "unloading"
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
    
    vehicle_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    vehicle_type = Column(String(50), nullable=False)  # truck, van, bike, etc.
    capacity_kg = Column(Float, nullable=False)
    current_location_id = Column(Integer, ForeignKey("locations.id"))
    status = Column(String(20), default=VehicleStatus.AVAILABLE)  # VehicleStatus
    
    # Performance metrics
    total_distance_km = Column(Float, default=0.0)
    total_deliveries = Column(Integer, default=0)
    average_speed_kmh = Column(Float, default=30.0)
    fuel_efficiency = Column(Float)  # km/liter
    
    # Current load
    current_load_kg = Column(Float, default=0.0)
    current_route_id = Column(Integer, ForeignKey("routes.id"))
    
    # Relationships
    current_location = relationship("Location", back_populates="vehicles")
    current_route = relationship("Route", back_populates="vehicle")
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
    
    route_id = Column(String(50), unique=True, nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
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
    vehicle = relationship("Vehicle", back_populates="current_route")
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
    
    delivery_id = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    route_id = Column(Integer, ForeignKey("routes.id"))
    
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
    order = relationship("Order", back_populates="deliveries")
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