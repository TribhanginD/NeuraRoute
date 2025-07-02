"""
AI Model Management API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import structlog

from app.ai.model_manager import get_ai_model_manager
from app.core.config import settings
from app.core.database import get_db

logger = structlog.get_logger()
router = APIRouter()

@router.get("/status")
async def get_ai_status():
    """Get AI model manager status"""
    try:
        ai_manager = await get_ai_model_manager()
        
        return {
            "status": "active",
            "available_providers": ai_manager.get_available_providers(),
            "provider_status": ai_manager.get_provider_status(),
            "metrics": ai_manager.get_metrics(),
            "configuration": {
                "default_provider": settings.DEFAULT_AI_PROVIDER,
                "fallback_provider": settings.AI_FALLBACK_PROVIDER,
                "cache_enabled": settings.AI_CACHE_ENABLED,
                "monitoring_enabled": settings.AI_MONITORING_ENABLED
            }
        }
    except Exception as e:
        logger.error("Failed to get AI status", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get AI status: {str(e)}")

@router.post("/test")
async def test_ai_generation(request: Dict[str, Any]):
    """Test AI model generation"""
    try:
        ai_manager = await get_ai_model_manager()
        
        prompt = request.get("prompt", "Hello, how are you?")
        system_message = request.get("system_message")
        model = request.get("model")
        provider = request.get("provider")
        
        response = await ai_manager.generate_response(
            prompt=prompt,
            system_message=system_message,
            model=model,
            provider=provider
        )
        
        return {
            "status": "success",
            "response": response,
            "test_parameters": {
                "prompt": prompt,
                "system_message": system_message,
                "model": model,
                "provider": provider
            }
        }
    except Exception as e:
        logger.error("AI test failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"AI test failed: {str(e)}")

@router.get("/metrics")
async def get_ai_metrics():
    """Get AI model metrics"""
    try:
        ai_manager = await get_ai_model_manager()
        return ai_manager.get_metrics()
    except Exception as e:
        logger.error("Failed to get AI metrics", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get AI metrics: {str(e)}")

@router.post("/forecast")
async def test_forecasting(request: Dict[str, Any]):
    """Test demand forecasting with AI"""
    try:
        from app.forecasting.engine import DemandForecastingEngine
        
        # Initialize forecasting engine
        forecasting_engine = DemandForecastingEngine()
        await forecasting_engine.initialize()
        
        # Extract parameters
        sku_id = request.get("sku_id", 1)
        location_id = request.get("location_id", 1)
        forecast_date_str = request.get("forecast_date")
        horizon_hours = request.get("horizon_hours", 24)
        
        # Parse forecast date
        from datetime import datetime
        if forecast_date_str:
            forecast_date = datetime.fromisoformat(forecast_date_str)
        else:
            forecast_date = datetime.utcnow()
        
        # Generate forecast
        forecast = await forecasting_engine.generate_forecast(
            sku_id=sku_id,
            location_id=location_id,
            forecast_date=forecast_date,
            horizon_hours=horizon_hours
        )
        
        return {
            "status": "success",
            "forecast": {
                "sku_id": forecast.sku_id,
                "location_id": forecast.location_id,
                "forecast_date": forecast.forecast_date.isoformat(),
                "predicted_demand": forecast.predicted_demand,
                "confidence_lower": forecast.confidence_lower,
                "confidence_upper": forecast.confidence_upper,
                "model_used": forecast.model_used,
                "reasoning": forecast.reasoning
            },
            "test_parameters": {
                "sku_id": sku_id,
                "location_id": location_id,
                "forecast_date": forecast_date.isoformat(),
                "horizon_hours": horizon_hours
            }
        }
    except Exception as e:
        logger.error("Forecasting test failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Forecasting test failed: {str(e)}")

@router.post("/pricing")
async def test_pricing(request: Dict[str, Any]):
    """Test dynamic pricing with AI"""
    try:
        from app.agents.pricing_agent import PricingEngine
        from app.models.inventory import SKU
        
        # Initialize pricing engine
        pricing_engine = PricingEngine()
        await pricing_engine.initialize()
        
        # Get SKU
        db: AsyncSession = Depends(get_db)
        sku = db.query(SKU).filter(SKU.id == request.get("sku_id", 1)).first()
        
        if not sku:
            raise HTTPException(status_code=404, detail="SKU not found")
        
        # Test parameters
        current_demand = request.get("current_demand", 50.0)
        forecasted_demand = request.get("forecasted_demand", 60.0)
        competitor_prices = request.get("competitor_prices", {
            "competitor_1": sku.price * 1.1,
            "competitor_2": sku.price * 0.95,
            "competitor_3": sku.price * 1.05
        })
        market_conditions = request.get("market_conditions", {
            "economic_indicator": "stable",
            "consumer_confidence": 75.5,
            "market_volatility": 0.15,
            "competition_level": "medium"
        })
        
        # Calculate optimal price
        pricing_result = await pricing_engine.calculate_optimal_price(
            sku=sku,
            current_demand=current_demand,
            forecasted_demand=forecasted_demand,
            competitor_prices=competitor_prices,
            market_conditions=market_conditions
        )
        
        db.close()
        
        return {
            "status": "success",
            "pricing_result": pricing_result,
            "test_parameters": {
                "sku_id": sku.id,
                "sku_name": sku.name,
                "current_price": sku.price,
                "current_demand": current_demand,
                "forecasted_demand": forecasted_demand,
                "competitor_prices": competitor_prices,
                "market_conditions": market_conditions
            }
        }
    except Exception as e:
        logger.error("Pricing test failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Pricing test failed: {str(e)}")

@router.get("/providers")
async def get_ai_providers():
    """Get available AI providers and their status"""
    try:
        ai_manager = await get_ai_model_manager()
        
        providers = {}
        for provider_name in ai_manager.get_available_providers():
            provider_instance = ai_manager.providers[provider_name]
            providers[provider_name] = {
                "available": provider_instance.is_available(),
                "models": getattr(provider_instance, 'available_models', []),
                "status": "active" if provider_instance.is_available() else "inactive"
            }
        
        return {
            "providers": providers,
            "active_provider": settings.DEFAULT_AI_PROVIDER,
            "fallback_provider": settings.AI_FALLBACK_PROVIDER
        }
    except Exception as e:
        logger.error("Failed to get AI providers", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get AI providers: {str(e)}")

@router.post("/cache/clear")
async def clear_ai_cache():
    """Clear AI response cache"""
    try:
        ai_manager = await get_ai_model_manager()
        ai_manager.cache.clear()
        
        return {
            "status": "success",
            "message": "AI cache cleared successfully"
        }
    except Exception as e:
        logger.error("Failed to clear AI cache", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to clear AI cache: {str(e)}") 