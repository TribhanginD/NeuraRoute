"""
Forecasting models for LCM-style demand forecasting system
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, Text, JSON, DateTime, Integer, Float, Date, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid
from pydantic import Field, BaseModel as PydanticBaseModel

from app.models.base import BaseModelMixin, Base
from app.core.database import Base
from .base import BaseModel


class ForecastStatus(str, enum.Enum):
    """Forecast status enumeration"""
    PENDING = "pending"
    GENERATED = "generated"
    VALIDATED = "validated"
    EXPIRED = "expired"
    ERROR = "error"


class ForecastModel(str, enum.Enum):
    """Forecast model types"""
    AI_REASONING = "ai_reasoning"
    PROPHET = "prophet"
    STATISTICAL = "statistical"
    HEURISTIC = "heuristic"
    ENSEMBLE = "ensemble"


class DemandForecast(Base, BaseModelMixin):
    """Demand forecast model"""
    
    __tablename__ = "demand_forecasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(String(100), nullable=False, index=True)
    forecast_data = Column(JSON, nullable=False)
    confidence_score = Column(Numeric(5, 4))
    forecast_horizon_hours = Column(Integer, default=24, nullable=False)
    
    def __init__(self, product_id: str, forecast_data: Dict[str, Any], 
                 confidence_score: float = None, forecast_horizon_hours: int = 24, **kwargs):
        super().__init__(**kwargs)
        self.product_id = product_id
        self.forecast_data = forecast_data
        self.confidence_score = confidence_score
        self.forecast_horizon_hours = forecast_horizon_hours
    
    def get_forecast_values(self) -> List[Dict[str, Any]]:
        """Get forecast values"""
        return self.forecast_data.get('values', [])
    
    def get_total_forecast(self) -> float:
        """Get total forecasted demand"""
        values = self.get_forecast_values()
        return sum(value.get('demand', 0) for value in values)
    
    def get_peak_demand(self) -> float:
        """Get peak demand from forecast"""
        values = self.get_forecast_values()
        if not values:
            return 0.0
        return max(value.get('demand', 0) for value in values)
    
    def get_peak_time(self) -> Optional[datetime]:
        """Get time of peak demand"""
        values = self.get_forecast_values()
        if not values:
            return None
        
        peak_value = max(values, key=lambda x: x.get('demand', 0))
        timestamp_str = peak_value.get('timestamp')
        if timestamp_str:
            try:
                return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except ValueError:
                return None
        return None
    
    def get_confidence_level(self) -> str:
        """Get confidence level as string"""
        if not self.confidence_score:
            return 'unknown'
        
        if self.confidence_score >= 0.9:
            return 'very_high'
        elif self.confidence_score >= 0.8:
            return 'high'
        elif self.confidence_score >= 0.7:
            return 'medium'
        elif self.confidence_score >= 0.6:
            return 'low'
        else:
            return 'very_low'
    
    def get_factors(self) -> Dict[str, Any]:
        """Get factors that influenced the forecast"""
        return self.forecast_data.get('factors', {})
    
    def get_weather_factor(self) -> float:
        """Get weather impact factor"""
        factors = self.get_factors()
        return factors.get('weather', 1.0)
    
    def get_seasonal_factor(self) -> float:
        """Get seasonal impact factor"""
        factors = self.get_factors()
        return factors.get('seasonal', 1.0)
    
    def get_event_factor(self) -> float:
        """Get event impact factor"""
        factors = self.get_factors()
        return factors.get('events', 1.0)
    
    def get_historical_factor(self) -> float:
        """Get historical trend factor"""
        factors = self.get_factors()
        return factors.get('historical', 1.0)
    
    def is_reliable(self) -> bool:
        """Check if forecast is reliable"""
        return self.confidence_score and self.confidence_score >= 0.7
    
    def get_forecast_summary(self) -> Dict[str, Any]:
        """Get forecast summary"""
        return {
            'total_forecast': self.get_total_forecast(),
            'peak_demand': self.get_peak_demand(),
            'peak_time': self.get_peak_time(),
            'confidence_level': self.get_confidence_level(),
            'is_reliable': self.is_reliable(),
            'factors': {
                'weather': self.get_weather_factor(),
                'seasonal': self.get_seasonal_factor(),
                'events': self.get_event_factor(),
                'historical': self.get_historical_factor()
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        base_dict = super().to_dict()
        base_dict.update(self.get_forecast_summary())
        return base_dict
    
    def __repr__(self) -> str:
        return f"<DemandForecast(id={self.id}, product='{self.product_id}', confidence={self.confidence_score})>"


class ForecastContext(Base, BaseModelMixin):
    """Forecast context model for storing structured context data"""
    
    forecast_id = Column(UUID(as_uuid=True), ForeignKey("demand_forecasts.id"), nullable=False, index=True)
    context_type = Column(String(50), nullable=False, index=True)  # weather, events, seasonal, market
    context_data = Column(JSON, nullable=False)
    importance_score = Column(Float, default=1.0)
    source = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    forecast = relationship("DemandForecast")
    
    def __repr__(self):
        return f"<ForecastContext(id={self.id}, type='{self.context_type}', importance={self.importance_score})>"
    
    def get_data_value(self, key: str, default: Any = None) -> Any:
        """Get context data value"""
        return self.context_data.get(key, default) if self.context_data else default
    
    def set_data_value(self, key: str, value: Any) -> None:
        """Set context data value"""
        if not self.context_data:
            self.context_data = {}
        self.context_data[key] = value
        self.updated_at = datetime.utcnow()


class ForecastAccuracy(Base, BaseModelMixin):
    """Forecast accuracy tracking model"""
    
    forecast_id = Column(UUID(as_uuid=True), ForeignKey("demand_forecasts.id"), nullable=False, index=True)
    actual_demand = Column(Integer, nullable=False)
    predicted_demand = Column(Integer, nullable=False)
    absolute_error = Column(Integer, nullable=False)
    percentage_error = Column(Float, nullable=False)
    accuracy_score = Column(Float, nullable=False)
    evaluation_date = Column(Date, nullable=False, index=True)
    
    # Relationships
    forecast = relationship("DemandForecast")
    
    def __repr__(self):
        return f"<ForecastAccuracy(id={self.id}, accuracy={self.accuracy_score:.3f})>"


# Pydantic schemas
class DemandForecastBase(PydanticBaseModel):
    """Base demand forecast schema"""
    sku_id: str = Field(..., description="SKU ID")
    merchant_id: str = Field(..., description="Merchant ID")
    forecast_date: date = Field(..., description="Forecast date")
    predicted_demand: int = Field(..., description="Predicted demand")
    confidence_lower: Optional[int] = Field(None, description="Lower confidence bound")
    confidence_upper: Optional[int] = Field(None, description="Upper confidence bound")
    confidence_level: float = Field(0.95, description="Confidence level")
    context: Dict[str, Any] = Field(default={}, description="Forecast context")
    model_version: Optional[str] = Field(None, description="Model version")
    status: ForecastStatus = Field(ForecastStatus.PENDING, description="Forecast status")


class DemandForecastCreate(DemandForecastBase):
    """Schema for creating demand forecast"""
    pass


class DemandForecastUpdate(PydanticBaseModel):
    """Schema for updating demand forecast"""
    predicted_demand: Optional[int] = Field(None, description="Predicted demand")
    confidence_lower: Optional[int] = Field(None, description="Lower confidence bound")
    confidence_upper: Optional[int] = Field(None, description="Upper confidence bound")
    accuracy_score: Optional[float] = Field(None, description="Accuracy score")
    status: Optional[ForecastStatus] = Field(None, description="Forecast status")


class DemandForecastResponse(DemandForecastBase):
    """Schema for demand forecast responses"""
    id: str = Field(..., description="Forecast ID")
    accuracy_score: Optional[float] = Field(None, description="Accuracy score")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class ForecastContextBase(PydanticBaseModel):
    """Base forecast context schema"""
    context_type: str = Field(..., description="Context type")
    context_data: Dict[str, Any] = Field(..., description="Context data")
    importance_score: float = Field(1.0, description="Importance score")
    source: Optional[str] = Field(None, description="Data source")


class ForecastContextCreate(ForecastContextBase):
    """Schema for creating forecast context"""
    forecast_id: str = Field(..., description="Forecast ID")


class ForecastContextResponse(ForecastContextBase):
    """Schema for forecast context responses"""
    id: str = Field(..., description="Context ID")
    forecast_id: str = Field(..., description="Forecast ID")
    timestamp: datetime = Field(..., description="Context timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class ForecastAccuracyBase(PydanticBaseModel):
    """Base forecast accuracy schema"""
    actual_demand: int = Field(..., description="Actual demand")
    predicted_demand: int = Field(..., description="Predicted demand")
    evaluation_date: date = Field(..., description="Evaluation date")


class ForecastAccuracyCreate(ForecastAccuracyBase):
    """Schema for creating forecast accuracy"""
    forecast_id: str = Field(..., description="Forecast ID")


class ForecastAccuracyResponse(ForecastAccuracyBase):
    """Schema for forecast accuracy responses"""
    id: str = Field(..., description="Accuracy ID")
    forecast_id: str = Field(..., description="Forecast ID")
    absolute_error: int = Field(..., description="Absolute error")
    percentage_error: float = Field(..., description="Percentage error")
    accuracy_score: float = Field(..., description="Accuracy score")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class ForecastRequest(PydanticBaseModel):
    """Schema for forecast generation request"""
    sku_ids: List[str] = Field(..., description="List of SKU IDs")
    merchant_ids: List[str] = Field(..., description="List of merchant IDs")
    forecast_date: date = Field(..., description="Forecast date")
    horizon_days: int = Field(7, description="Forecast horizon in days")
    model_type: ForecastModel = Field(ForecastModel.AI_REASONING, description="Model type")
    include_context: bool = Field(True, description="Include context data")


class ForecastMetrics(PydanticBaseModel):
    """Schema for forecast metrics"""
    total_forecasts: int = Field(..., description="Total forecasts")
    valid_forecasts: int = Field(..., description="Valid forecasts")
    avg_accuracy: float = Field(..., description="Average accuracy")
    accuracy_by_model: Dict[str, float] = Field(..., description="Accuracy by model type")
    recent_accuracy: float = Field(..., description="Recent accuracy (last 7 days)")
    context_coverage: float = Field(..., description="Context coverage percentage")


class ForecastSummary(PydanticBaseModel):
    """Schema for forecast summary"""
    total_forecasts: int = Field(..., description="Total forecasts")
    forecasts_by_status: Dict[str, int] = Field(..., description="Forecast count by status")
    forecasts_by_model: Dict[str, int] = Field(..., description="Forecast count by model")
    avg_accuracy: float = Field(..., description="Average accuracy")
    pending_forecasts: int = Field(..., description="Pending forecasts")
    expired_forecasts: int = Field(..., description="Expired forecasts") 