"""
Inventory models for stock management
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid

from pydantic import BaseModel, Field
from .base import Base, BaseModelMixin

# Import enum types
from sqlalchemy import Enum as SQLEnum
inventory_status_enum = SQLEnum(
    'inventory_status',
    name='inventory_status'
)


class InventoryStatus:
    IN_STOCK = 'in_stock'
    LOW_STOCK = 'low_stock'
    OUT_OF_STOCK = 'out_of_stock'
    RESERVED = 'reserved'


class SKU(Base, BaseModelMixin):
    """SKU (Stock Keeping Unit) model"""
    
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100), index=True)
    unit_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)
    weight_kg = Column(Float)
    volume_m3 = Column(Float)
    shelf_life_days = Column(Integer)
    
    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="sku", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SKU(id={self.id}, name='{self.name}', category='{self.category}')>"
    
    def get_margin(self) -> float:
        """Calculate profit margin"""
        if self.cost_price > 0:
            return (self.unit_price - self.cost_price) / self.unit_price
        return 0.0
    
    def get_margin_amount(self) -> float:
        """Calculate profit margin amount"""
        return self.unit_price - self.cost_price


class InventoryItem(Base, BaseModelMixin):
    """Inventory item model for tracking stock levels"""
    
    __tablename__ = "inventory_items"
    
    sku_id = Column(String(36), ForeignKey("sku.id"), nullable=False, index=True)
    merchant_id = Column(UUID(as_uuid=True), ForeignKey("merchants.id"), nullable=False, index=True)
    location_id = Column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False, index=True)
    quantity = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)
    status = Column(inventory_status_enum, default=InventoryStatus.IN_STOCK, index=True)
    last_restock_date = Column(DateTime)
    expiry_date = Column(DateTime)
    
    # Relationships
    sku = relationship("SKU", back_populates="inventory_items")
    merchant = relationship("Merchant", back_populates="inventory_items")
    location = relationship("Location", back_populates="inventory_items")
    
    def __repr__(self):
        return f"<InventoryItem(id={self.id}, sku_id='{self.sku_id}', quantity={self.quantity}, status='{self.status}')>"
    
    @property
    def available_quantity(self) -> int:
        """Get available quantity (total - reserved)"""
        return max(0, self.quantity - self.reserved_quantity)
    
    def get_available_quantity(self) -> int:
        """Get available quantity (total - reserved)"""
        return max(0, self.quantity - self.reserved_quantity)
    
    def can_fulfill_order(self, requested_quantity: int) -> bool:
        """Check if can fulfill order quantity"""
        return self.get_available_quantity() >= requested_quantity
    
    def reserve_quantity(self, quantity: int) -> bool:
        """Reserve quantity for order"""
        if self.get_available_quantity() >= quantity:
            self.reserved_quantity += quantity
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def release_reservation(self, quantity: int) -> None:
        """Release reserved quantity"""
        self.reserved_quantity = max(0, self.reserved_quantity - quantity)
        self.updated_at = datetime.utcnow()
    
    def update_quantity(self, new_quantity: int) -> None:
        """Update total quantity"""
        self.quantity = max(0, new_quantity)
        self.updated_at = datetime.utcnow()
        self._update_status()
    
    def add_quantity(self, quantity: int) -> None:
        """Add quantity to inventory"""
        self.quantity += quantity
        self.updated_at = datetime.utcnow()
        self._update_status()
    
    def remove_quantity(self, quantity: int) -> bool:
        """Remove quantity from inventory"""
        if self.get_available_quantity() >= quantity:
            self.quantity = max(0, self.quantity - quantity)
            self.updated_at = datetime.utcnow()
            self._update_status()
            return True
        return False
    
    def _update_status(self) -> None:
        """Update inventory status based on quantity"""
        available = self.get_available_quantity()
        
        if available == 0:
            self.status = InventoryStatus.OUT_OF_STOCK
        elif available <= 10:  # Low stock threshold
            self.status = InventoryStatus.LOW_STOCK
        else:
            self.status = InventoryStatus.IN_STOCK
    
    def is_expired(self) -> bool:
        """Check if inventory is expired"""
        if not self.expiry_date:
            return False
        return datetime.utcnow() > self.expiry_date
    
    def get_days_until_expiry(self) -> Optional[int]:
        """Get days until expiry"""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - datetime.utcnow()
        return max(0, delta.days)


# Pydantic schemas
class SKUBase(BaseModel):
    """Base SKU schema"""
    name: str = Field(..., description="SKU name")
    description: Optional[str] = Field(None, description="SKU description")
    category: Optional[str] = Field(None, description="SKU category")
    unit_price: float = Field(..., description="Unit price")
    cost_price: float = Field(..., description="Cost price")
    weight_kg: Optional[float] = Field(None, description="Weight in kg")
    volume_m3: Optional[float] = Field(None, description="Volume in m³")
    shelf_life_days: Optional[int] = Field(None, description="Shelf life in days")


class SKUCreate(SKUBase):
    """Schema for creating SKU"""
    pass


class SKUUpdate(BaseModel):
    """Schema for updating SKU"""
    name: Optional[str] = Field(None, description="SKU name")
    description: Optional[str] = Field(None, description="SKU description")
    category: Optional[str] = Field(None, description="SKU category")
    unit_price: Optional[float] = Field(None, description="Unit price")
    cost_price: Optional[float] = Field(None, description="Cost price")
    weight_kg: Optional[float] = Field(None, description="Weight in kg")
    volume_m3: Optional[float] = Field(None, description="Volume in m³")
    shelf_life_days: Optional[int] = Field(None, description="Shelf life in days")


class SKUResponse(SKUBase):
    """Schema for SKU responses"""
    id: str = Field(..., description="SKU ID")
    margin: float = Field(..., description="Profit margin")
    margin_amount: float = Field(..., description="Profit margin amount")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class InventoryItemBase(BaseModel):
    """Base inventory item schema"""
    sku_id: str = Field(..., description="SKU ID")
    merchant_id: str = Field(..., description="Merchant ID")
    quantity: int = Field(..., description="Total quantity")
    reserved_quantity: int = Field(0, description="Reserved quantity")
    status: str = Field('in_stock', description="Inventory status")


class InventoryItemCreate(InventoryItemBase):
    """Schema for creating inventory item"""
    pass


class InventoryItemUpdate(BaseModel):
    """Schema for updating inventory item"""
    quantity: Optional[int] = Field(None, description="Total quantity")
    reserved_quantity: Optional[int] = Field(None, description="Reserved quantity")
    last_restock_date: Optional[datetime] = Field(None, description="Last restock date")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date")


class InventoryItemResponse(InventoryItemBase):
    """Schema for inventory item responses"""
    id: str = Field(..., description="Inventory item ID")
    available_quantity: int = Field(..., description="Available quantity")
    last_restock_date: Optional[datetime] = Field(None, description="Last restock date")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date")
    days_until_expiry: Optional[int] = Field(None, description="Days until expiry")
    is_expired: bool = Field(..., description="Whether item is expired")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class InventorySummary(BaseModel):
    """Schema for inventory summary"""
    total_skus: int = Field(..., description="Total SKUs")
    total_items: int = Field(..., description="Total inventory items")
    low_stock_items: int = Field(..., description="Low stock items")
    out_of_stock_items: int = Field(..., description="Out of stock items")
    expired_items: int = Field(..., description="Expired items")
    total_value: float = Field(..., description="Total inventory value")
    items_by_status: Dict[str, int] = Field(..., description="Item count by status")
    items_by_category: Dict[str, int] = Field(..., description="Item count by category")


class InventoryMetrics(BaseModel):
    """Schema for inventory metrics"""
    turnover_rate: float = Field(..., description="Inventory turnover rate")
    avg_stock_level: float = Field(..., description="Average stock level")
    stockout_rate: float = Field(..., description="Stockout rate")
    fill_rate: float = Field(..., description="Fill rate")
    carrying_cost: float = Field(..., description="Carrying cost")
    stockout_cost: float = Field(..., description="Stockout cost")


class Location(Base, BaseModelMixin):
    """Location model for inventory and delivery locations"""
    
    __tablename__ = "locations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(50), default="USA", nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location_type = Column(String(50), default="warehouse")  # warehouse, store, pickup_point, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="location")
    vehicles = relationship("Vehicle", back_populates="current_location")
    
    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}', type='{self.location_type}')>"
    
    def get_coordinates(self) -> Dict[str, float]:
        """Get location coordinates"""
        return {
            "latitude": self.latitude,
            "longitude": self.longitude
        }
    
    def get_full_address(self) -> str:
        """Get full address string"""
        return f"{self.address}, {self.city}, {self.state} {self.postal_code}, {self.country}" 