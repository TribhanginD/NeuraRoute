"""
Pricing model for dynamic pricing
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import BaseModel


class Pricing(BaseModel):
    """Pricing model for dynamic pricing"""
    
    __tablename__ = "pricing"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(100), nullable=False, index=True)
    base_price = Column(Numeric(10, 2), nullable=False)
    current_price = Column(Numeric(10, 2), nullable=False)
    demand_factor = Column(Numeric(5, 4), default=1.0)
    supply_factor = Column(Numeric(5, 4), default=1.0)
    last_updated = Column(DateTime(timezone=True), server_default='now()')
    
    def __init__(self, product_id: str, base_price: float, current_price: float = None,
                 demand_factor: float = 1.0, supply_factor: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.product_id = product_id
        self.base_price = base_price
        self.current_price = current_price or base_price
        self.demand_factor = demand_factor
        self.supply_factor = supply_factor
    
    def update_price(self, new_price: float):
        """Update current price"""
        if new_price > 0:
            self.current_price = new_price
            self.last_updated = datetime.utcnow()
    
    def update_demand_factor(self, factor: float):
        """Update demand factor"""
        if 0.1 <= factor <= 10.0:  # Reasonable bounds
            self.demand_factor = factor
            self._recalculate_price()
    
    def update_supply_factor(self, factor: float):
        """Update supply factor"""
        if 0.1 <= factor <= 10.0:  # Reasonable bounds
            self.supply_factor = factor
            self._recalculate_price()
    
    def _recalculate_price(self):
        """Recalculate price based on factors"""
        new_price = float(self.base_price) * float(self.demand_factor) / float(self.supply_factor)
        self.update_price(new_price)
    
    def get_price_change_percentage(self) -> float:
        """Get percentage change from base price"""
        if self.base_price == 0:
            return 0.0
        return ((self.current_price - self.base_price) / self.base_price) * 100
    
    def get_total_factor(self) -> float:
        """Get total pricing factor"""
        return float(self.demand_factor) / float(self.supply_factor)
    
    def is_above_base(self) -> bool:
        """Check if current price is above base price"""
        return self.current_price > self.base_price
    
    def is_below_base(self) -> bool:
        """Check if current price is below base price"""
        return self.current_price < self.base_price
    
    def get_price_category(self) -> str:
        """Get price category based on change"""
        change_pct = self.get_price_change_percentage()
        
        if change_pct >= 50:
            return 'very_high'
        elif change_pct >= 20:
            return 'high'
        elif change_pct >= 5:
            return 'moderate'
        elif change_pct >= -5:
            return 'normal'
        elif change_pct >= -20:
            return 'low'
        else:
            return 'very_low'
    
    def get_dynamic_pricing_score(self) -> float:
        """Get dynamic pricing effectiveness score"""
        # This would be calculated based on sales performance
        # For now, return a placeholder
        return 0.75
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        base_dict['price_change_percentage'] = self.get_price_change_percentage()
        base_dict['total_factor'] = self.get_total_factor()
        base_dict['is_above_base'] = self.is_above_base()
        base_dict['is_below_base'] = self.is_below_base()
        base_dict['price_category'] = self.get_price_category()
        base_dict['dynamic_pricing_score'] = self.get_dynamic_pricing_score()
        return base_dict
    
    def __repr__(self) -> str:
        return f"<Pricing(id={self.id}, product='{self.product_id}', current_price={self.current_price}, base_price={self.base_price})>"
 