from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class Location(BaseModel):
    """Geographic location model"""
    __tablename__ = "locations"
    
    name = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    sector = Column(String(50), nullable=False)  # City sector
    is_active = Column(Boolean, default=True)
    
    # Relationships
    inventories = relationship("Inventory", back_populates="location")
    vehicles = relationship("Vehicle", back_populates="current_location")

class SKU(BaseModel):
    """Stock Keeping Unit model"""
    __tablename__ = "skus"
    
    sku_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=False)
    unit = Column(String(20), nullable=False)  # pieces, kg, liters, etc.
    base_price = Column(Float, nullable=False)
    min_stock_level = Column(Integer, default=0)
    max_stock_level = Column(Integer)
    lead_time_days = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    inventories = relationship("Inventory", back_populates="sku")
    forecasts = relationship("Forecast", back_populates="sku")

class Inventory(BaseModel):
    """Inventory model for tracking stock levels"""
    __tablename__ = "inventories"
    
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    current_stock = Column(Integer, default=0)
    reserved_stock = Column(Integer, default=0)
    available_stock = Column(Integer, default=0)
    last_restock_date = Column(DateTime)
    next_restock_date = Column(DateTime)
    
    # Relationships
    location = relationship("Location", back_populates="inventories")
    sku = relationship("SKU", back_populates="inventories")
    
    def update_available_stock(self):
        """Update available stock based on current and reserved"""
        self.available_stock = max(0, self.current_stock - self.reserved_stock)
    
    def add_stock(self, quantity: int):
        """Add stock to inventory"""
        self.current_stock += quantity
        self.update_available_stock()
    
    def reserve_stock(self, quantity: int) -> bool:
        """Reserve stock for orders"""
        if self.available_stock >= quantity:
            self.reserved_stock += quantity
            self.update_available_stock()
            return True
        return False
    
    def release_stock(self, quantity: int):
        """Release reserved stock"""
        self.reserved_stock = max(0, self.reserved_stock - quantity)
        self.update_available_stock()
    
    def consume_stock(self, quantity: int) -> bool:
        """Consume stock (remove from current and reserved)"""
        if self.current_stock >= quantity:
            self.current_stock -= quantity
            self.reserved_stock = max(0, self.reserved_stock - quantity)
            self.update_available_stock()
            return True
        return False 