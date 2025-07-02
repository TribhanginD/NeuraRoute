"""
Weather data model
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid

from .base import BaseModel

# Import enum types
from sqlalchemy import Enum as SQLEnum
weather_condition_enum = SQLEnum('weather_condition', name='weather_condition')


class WeatherData(BaseModel):
    """Weather data model"""
    
    __tablename__ = "weather_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location_lat = Column(Numeric(10, 8), nullable=False)
    location_lng = Column(Numeric(11, 8), nullable=False)
    condition = Column(weather_condition_enum, nullable=False)
    temperature = Column(Numeric(5, 2))
    humidity = Column(Numeric(5, 2))
    wind_speed = Column(Numeric(5, 2))
    precipitation_chance = Column(Numeric(5, 4))
    recorded_at = Column(DateTime(timezone=True), server_default='now()')
    
    def __init__(self, location_lat: float, location_lng: float, condition: str,
                 temperature: float = None, humidity: float = None, 
                 wind_speed: float = None, precipitation_chance: float = None, **kwargs):
        super().__init__(**kwargs)
        self.location_lat = location_lat
        self.location_lng = location_lng
        self.condition = condition
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.precipitation_chance = precipitation_chance
    
    def is_sunny(self) -> bool:
        """Check if weather is sunny"""
        return self.condition == 'sunny'
    
    def is_rainy(self) -> bool:
        """Check if weather is rainy"""
        return self.condition in ['rainy', 'stormy']
    
    def is_snowy(self) -> bool:
        """Check if weather is snowy"""
        return self.condition == 'snowy'
    
    def is_stormy(self) -> bool:
        """Check if weather is stormy"""
        return self.condition == 'stormy'
    
    def get_weather_impact_score(self) -> float:
        """Get weather impact score for logistics"""
        base_score = 1.0
        
        # Temperature impact
        if self.temperature is not None:
            if self.temperature < 0 or self.temperature > 35:
                base_score *= 0.8  # Extreme temperatures reduce efficiency
        
        # Precipitation impact
        if self.precipitation_chance is not None:
            if self.precipitation_chance > 0.7:
                base_score *= 0.7  # High precipitation reduces efficiency
            elif self.precipitation_chance > 0.3:
                base_score *= 0.9  # Moderate precipitation slightly reduces efficiency
        
        # Wind impact
        if self.wind_speed is not None:
            if self.wind_speed > 30:
                base_score *= 0.8  # High winds reduce efficiency
        
        # Condition impact
        if self.is_stormy():
            base_score *= 0.6
        elif self.is_snowy():
            base_score *= 0.7
        elif self.is_rainy():
            base_score *= 0.8
        
        return base_score
    
    def get_demand_multiplier(self) -> float:
        """Get demand multiplier based on weather"""
        # Weather can affect demand patterns
        if self.is_sunny():
            return 1.1  # Sunny weather increases demand
        elif self.is_rainy():
            return 0.9  # Rainy weather decreases demand
        elif self.is_snowy():
            return 0.8  # Snowy weather significantly decreases demand
        elif self.is_stormy():
            return 0.7  # Stormy weather greatly decreases demand
        else:
            return 1.0  # Cloudy weather has neutral effect
    
    def get_delivery_delay_minutes(self) -> int:
        """Get estimated delivery delay in minutes due to weather"""
        base_delay = 0
        
        if self.is_stormy():
            base_delay += 30
        elif self.is_snowy():
            base_delay += 20
        elif self.is_rainy():
            base_delay += 10
        
        if self.wind_speed and self.wind_speed > 25:
            base_delay += 5
        
        return base_delay
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        base_dict['is_sunny'] = self.is_sunny()
        base_dict['is_rainy'] = self.is_rainy()
        base_dict['is_snowy'] = self.is_snowy()
        base_dict['is_stormy'] = self.is_stormy()
        base_dict['weather_impact_score'] = self.get_weather_impact_score()
        base_dict['demand_multiplier'] = self.get_demand_multiplier()
        base_dict['delivery_delay_minutes'] = self.get_delivery_delay_minutes()
        return base_dict
    
    def __repr__(self) -> str:
        return f"<WeatherData(id={self.id}, condition='{self.condition}', temp={self.temperature}, lat={self.location_lat}, lng={self.location_lng})>" 