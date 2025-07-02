"""
Order model for order management
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Integer, Enum, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import BaseModel

# Import enum types
from sqlalchemy import Enum as SQLEnum
order_status_enum = SQLEnum('order_status', name='order_status')


class Order(BaseModel):
    """Order model for order management"""
    
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(String(100), nullable=False, index=True)
    product_id = Column(String(100), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    status = Column(order_status_enum, default='pending', nullable=False)
    priority = Column(Integer, default=1, nullable=False)
    pickup_location_lat = Column(Numeric(10, 8))
    pickup_location_lng = Column(Numeric(11, 8))
    delivery_location_lat = Column(Numeric(10, 8))
    delivery_location_lng = Column(Numeric(11, 8))
    
    def __init__(self, customer_id: str, product_id: str, quantity: int,
                 priority: int = 1, pickup_location_lat: float = None, 
                 pickup_location_lng: float = None, delivery_location_lat: float = None,
                 delivery_location_lng: float = None, **kwargs):
        super().__init__(**kwargs)
        self.customer_id = customer_id
        self.product_id = product_id
        self.quantity = quantity
        self.priority = priority
        self.pickup_location_lat = pickup_location_lat
        self.pickup_location_lng = pickup_location_lng
        self.delivery_location_lat = delivery_location_lat
        self.delivery_location_lng = delivery_location_lng
        self.status = 'pending'
    
    def confirm(self):
        """Confirm the order"""
        self.status = 'confirmed'
    
    def start_transit(self):
        """Start order in transit"""
        if self.status == 'confirmed':
            self.status = 'in_transit'
    
    def deliver(self):
        """Mark order as delivered"""
        if self.status == 'in_transit':
            self.status = 'delivered'
    
    def cancel(self):
        """Cancel the order"""
        if self.status in ['pending', 'confirmed']:
            self.status = 'cancelled'
    
    def is_pending(self) -> bool:
        """Check if order is pending"""
        return self.status == 'pending'
    
    def is_confirmed(self) -> bool:
        """Check if order is confirmed"""
        return self.status == 'confirmed'
    
    def is_in_transit(self) -> bool:
        """Check if order is in transit"""
        return self.status == 'in_transit'
    
    def is_delivered(self) -> bool:
        """Check if order is delivered"""
        return self.status == 'delivered'
    
    def is_cancelled(self) -> bool:
        """Check if order is cancelled"""
        return self.status == 'cancelled'
    
    def is_high_priority(self) -> bool:
        """Check if order is high priority"""
        return self.priority <= 2
    
    def get_age_hours(self) -> float:
        """Get order age in hours"""
        if self.created_at:
            age = datetime.utcnow() - self.created_at
            return age.total_seconds() / 3600
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        base_dict['is_pending'] = self.is_pending()
        base_dict['is_confirmed'] = self.is_confirmed()
        base_dict['is_in_transit'] = self.is_in_transit()
        base_dict['is_delivered'] = self.is_delivered()
        base_dict['is_cancelled'] = self.is_cancelled()
        base_dict['is_high_priority'] = self.is_high_priority()
        base_dict['age_hours'] = self.get_age_hours()
        return base_dict
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, customer='{self.customer_id}', product='{self.product_id}', status='{self.status}')>" 