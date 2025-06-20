from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import structlog

from app.core.database import get_db
from app.models.forecasting import DemandForecast, ForecastContext
from app.forecasting.engine import DemandForecastingEngine

logger = structlog.get_logger()
router = APIRouter()

# Global forecasting engine instance
forecasting_engine = DemandForecastingEngine()

@router.get("/forecasts")
async def get_forecasts(
    sku_id: str = None,
    location_id: int = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get demand forecasts with optional filtering"""
    try:
        query = db.query(DemandForecast)
        
        if sku_id:
            query = query.filter(DemandForecast.sku_id == sku_id)
        if location_id:
            query = query.filter(DemandForecast.location_id == location_id)
        
        forecasts = query.offset(offset).limit(limit).all()
        
        return {
            "forecasts": [
                {
                    "forecast_id": forecast.forecast_id,
                    "sku_id": forecast.sku_id,
                    "location_id": forecast.location_id,
                    "forecast_horizon_hours": forecast.forecast_horizon_hours,
                    "predicted_demand": forecast.predicted_demand,
                    "confidence_interval_lower": forecast.confidence_interval_lower,
                    "confidence_interval_upper": forecast.confidence_interval_upper,
                    "forecast_accuracy": forecast.forecast_accuracy,
                    "created_at": forecast.created_at.isoformat(),
                    "forecast_time": forecast.forecast_time.isoformat()
                } for forecast in forecasts
            ],
            "total": len(forecasts)
        }
    except Exception as e:
        logger.error("Failed to get forecasts", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecasts/{forecast_id}")
async def get_forecast(forecast_id: str, db: Session = Depends(get_db)):
    """Get specific forecast details"""
    try:
        forecast = db.query(DemandForecast).filter(DemandForecast.forecast_id == forecast_id).first()
        if not forecast:
            raise HTTPException(status_code=404, detail="Forecast not found")
        
        return {
            "forecast_id": forecast.forecast_id,
            "sku_id": forecast.sku_id,
            "location_id": forecast.location_id,
            "forecast_horizon_hours": forecast.forecast_horizon_hours,
            "predicted_demand": forecast.predicted_demand,
            "confidence_interval_lower": forecast.confidence_interval_lower,
            "confidence_interval_upper": forecast.confidence_interval_upper,
            "forecast_accuracy": forecast.forecast_accuracy,
            "ai_reasoning": forecast.ai_reasoning,
            "context_data": forecast.context_data,
            "created_at": forecast.created_at.isoformat(),
            "forecast_time": forecast.forecast_time.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get forecast {forecast_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate")
async def generate_forecast(
    sku_id: str,
    location_id: int,
    horizon_hours: int = 24,
    db: Session = Depends(get_db)
):
    """Generate a new demand forecast"""
    try:
        forecast = await forecasting_engine.generate_forecast(
            sku_id=sku_id,
            location_id=location_id,
            horizon_hours=horizon_hours
        )
        
        return {
            "message": "Forecast generated successfully",
            "forecast": {
                "forecast_id": forecast.forecast_id,
                "sku_id": forecast.sku_id,
                "location_id": forecast.location_id,
                "predicted_demand": forecast.predicted_demand,
                "confidence_interval_lower": forecast.confidence_interval_lower,
                "confidence_interval_upper": forecast.confidence_interval_upper,
                "forecast_accuracy": forecast.forecast_accuracy,
                "created_at": forecast.created_at.isoformat()
            }
        }
    except Exception as e:
        logger.error("Failed to generate forecast", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/batch")
async def generate_batch_forecasts(
    sku_ids: List[str],
    location_ids: List[int],
    horizon_hours: int = 24
):
    """Generate forecasts for multiple SKUs and locations"""
    try:
        forecasts = await forecasting_engine.generate_batch_forecasts(
            sku_ids=sku_ids,
            location_ids=location_ids,
            horizon_hours=horizon_hours
        )
        
        return {
            "message": f"Generated {len(forecasts)} forecasts successfully",
            "forecasts": [
                {
                    "forecast_id": forecast.forecast_id,
                    "sku_id": forecast.sku_id,
                    "location_id": forecast.location_id,
                    "predicted_demand": forecast.predicted_demand,
                    "forecast_accuracy": forecast.forecast_accuracy
                } for forecast in forecasts
            ]
        }
    except Exception as e:
        logger.error("Failed to generate batch forecasts", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context")
async def get_forecast_context(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get forecast context data"""
    try:
        contexts = db.query(ForecastContext).offset(offset).limit(limit).all()
        
        return {
            "contexts": [
                {
                    "context_id": context.context_id,
                    "context_type": context.context_type,
                    "location_id": context.location_id,
                    "context_data": context.context_data,
                    "timestamp": context.timestamp.isoformat(),
                    "valid_until": context.valid_until.isoformat() if context.valid_until else None
                } for context in contexts
            ],
            "total": len(contexts)
        }
    except Exception as e:
        logger.error("Failed to get forecast context", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/accuracy")
async def get_forecast_accuracy(
    sku_id: str = None,
    location_id: int = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get forecast accuracy metrics"""
    try:
        # This would typically involve comparing forecasts with actual demand
        # For now, return a placeholder structure
        return {
            "overall_accuracy": 0.85,
            "sku_accuracy": {
                "sku_001": 0.92,
                "sku_002": 0.78,
                "sku_003": 0.89
            },
            "location_accuracy": {
                "1": 0.87,
                "2": 0.83,
                "3": 0.91
            },
            "time_period": f"Last {days} days"
        }
    except Exception as e:
        logger.error("Failed to get forecast accuracy", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_forecasting_summary(db: Session = Depends(get_db)):
    """Get forecasting summary statistics"""
    try:
        total_forecasts = db.query(DemandForecast).count()
        recent_forecasts = db.query(DemandForecast).filter(
            DemandForecast.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).count()
        
        # Calculate average accuracy
        forecasts_with_accuracy = db.query(DemandForecast).filter(
            DemandForecast.forecast_accuracy.isnot(None)
        ).all()
        
        avg_accuracy = sum(f.forecast_accuracy for f in forecasts_with_accuracy) / len(forecasts_with_accuracy) if forecasts_with_accuracy else 0
        
        return {
            "total_forecasts": total_forecasts,
            "forecasts_last_24h": recent_forecasts,
            "average_accuracy": round(avg_accuracy, 3),
            "forecast_engine_status": "active"
        }
    except Exception as e:
        logger.error("Failed to get forecasting summary", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 