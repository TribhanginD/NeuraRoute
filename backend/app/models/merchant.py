from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import BaseModel

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
    orders = relationship("Order", back_populates="merchant")
    inventories = relationship("Inventory", back_populates="location")
    
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

class Order(BaseModel):
    """Order model for customer orders"""
    __tablename__ = "orders"
    
    order_id = Column(String(50), unique=True, nullable=False, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    customer_id = Column(String(50), nullable=False)
    
    # Order details
    order_items = Column(JSON, nullable=False)  # List of items with quantities
    total_amount = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    tip_amount = Column(Float, default=0.0)
    
    # Status
    order_status = Column(String(20), default=OrderStatus.PENDING)  # OrderStatus
    payment_status = Column(String(20), default=PaymentStatus.PENDING)  # PaymentStatus
    
    # Timing
    order_time = Column(DateTime, nullable=False)
    requested_delivery_time = Column(DateTime)
    estimated_delivery_time = Column(DateTime)
    actual_delivery_time = Column(DateTime)
    
    # Delivery details
    delivery_address = Column(String(255), nullable=False)
    delivery_latitude = Column(Float)
    delivery_longitude = Column(Float)
    special_instructions = Column(Text)
    
    # Customer feedback
    customer_rating = Column(Integer)  # 1-5 stars
    customer_feedback = Column(Text)
    
    # Relationships
    merchant = relationship("Merchant", back_populates="orders")
    deliveries = relationship("Delivery", back_populates="order")
    
    def calculate_total(self):
        """Calculate order total"""
        self.total_amount = self.subtotal + self.tax_amount + self.delivery_fee + self.tip_amount
    
    def update_status(self, status: OrderStatus):
        """Update order status"""
        self.order_status = status
        if status == OrderStatus.DELIVERED and not self.actual_delivery_time:
            self.actual_delivery_time = datetime.utcnow()
    
    def get_delivery_duration(self) -> int:
        """Get actual delivery duration in minutes"""
        if self.order_time and self.actual_delivery_time:
            duration = self.actual_delivery_time - self.order_time
            return int(duration.total_seconds() / 60)
        return 0
    
    def get_items_summary(self) -> dict:
        """Get summary of order items"""
        summary = {}
        for item in self.order_items:
            sku_code = item.get("sku_code")
            quantity = item.get("quantity", 0)
            if sku_code in summary:
                summary[sku_code] += quantity
            else:
                summary[sku_code] = quantity
        return summary 