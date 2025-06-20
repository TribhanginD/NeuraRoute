from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class Forecast(BaseModel):
    """Demand forecast model"""
    __tablename__ = "forecasts"
    
    sku_id = Column(Integer, ForeignKey("skus.id"), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False)
    horizon_hours = Column(Integer, default=24)  # Forecast horizon
    
    # Forecast values
    predicted_demand = Column(Float, nullable=False)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    confidence_level = Column(Float, default=0.95)
    
    # Context and reasoning
    context_data = Column(JSON)  # Weather, events, historical data
    reasoning = Column(Text)  # AI reasoning for the forecast
    model_version = Column(String(50))
    accuracy_score = Column(Float)  # Historical accuracy
    
    # Relationships
    sku = relationship("SKU", back_populates="forecasts")
    location = relationship("Location")
    
    def get_confidence_interval(self) -> tuple:
        """Get confidence interval"""
        return (self.confidence_lower, self.confidence_upper)
    
    def update_accuracy(self, actual_demand: float):
        """Update accuracy score based on actual demand"""
        if actual_demand > 0:
            error = abs(self.predicted_demand - actual_demand) / actual_demand
            if self.accuracy_score is None:
                self.accuracy_score = 1.0 - error
            else:
                # Exponential moving average
                self.accuracy_score = 0.9 * self.accuracy_score + 0.1 * (1.0 - error)

class ForecastContext(BaseModel):
    """Context data for forecasting"""
    __tablename__ = "forecast_contexts"
    
    context_date = Column(DateTime, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    
    # Weather data
    temperature = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
    weather_condition = Column(String(50))
    
    # Event data
    events = Column(JSON)  # List of events affecting demand
    event_impact = Column(Float, default=1.0)
    
    # Historical data
    historical_demand = Column(JSON)  # Historical demand patterns
    seasonal_factors = Column(JSON)  # Seasonal adjustment factors
    
    # Market conditions
    competitor_prices = Column(JSON)
    market_trends = Column(JSON)
    
    # Relationships
    location = relationship("Location")
    
    def get_context_summary(self) -> dict:
        """Get context summary for AI reasoning"""
        return {
            "date": self.context_date.isoformat(),
            "weather": {
                "temperature": self.temperature,
                "humidity": self.humidity,
                "precipitation": self.precipitation,
                "condition": self.weather_condition
            },
            "events": self.events,
            "event_impact": self.event_impact,
            "historical_patterns": self.historical_demand,
            "seasonal_factors": self.seasonal_factors,
            "market_conditions": {
                "competitor_prices": self.competitor_prices,
                "trends": self.market_trends
            }
        } 