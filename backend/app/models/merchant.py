from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import BaseModel
import uuid
from sqlalchemy.dialects.postgresql import UUID

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class Merchant(BaseModel):
    """Merchant model for business entities"""
    __tablename__ = "merchants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    merchant_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    business_type = Column(String(50), nullable=False)  # restaurant, retail, etc.
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # Contact information
    email = Column(String(100))
    phone = Column(String(20))
    website = Column(String(200))
    
    # Business details
    operating_hours = Column(JSON)  # Operating hours by day
    delivery_radius_km = Column(Float, default=5.0)
    minimum_order_amount = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    
    # Performance metrics
    total_orders = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    location = relationship("Location")
    inventory_items = relationship("InventoryItem", back_populates="merchant", cascade="all, delete-orphan")
    
    def get_operating_status(self, current_time: datetime) -> bool:
        """Check if merchant is currently operating"""
        if not self.is_active:
            return False
        
        day_of_week = current_time.strftime("%A").lower()
        hour = current_time.hour
        
        if day_of_week in self.operating_hours:
            hours = self.operating_hours[day_of_week]
            return hours["open"] <= hour <= hours["close"]
        
        return False

# Remove everything from 'class Order(BaseModel):' to the end of the class definition. 