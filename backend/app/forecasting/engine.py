import asyncio
import structlog
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json

from app.core.config import settings
from app.models.forecasting import DemandForecast
from app.models.inventory import SKU, Location
from app.models.events import Event
from app.core.database import get_db
from app.ai.model_manager import get_ai_model_manager

logger = structlog.get_logger()

class ContextBuilder:
    """Builds comprehensive context for demand forecasting"""
    
    async def build_context(
        self,
        location_id: int,
        forecast_date: datetime,
        horizon_hours: int,
        db: Session
    ) -> Dict[str, Any]:
        """Build comprehensive context for forecasting"""
        
        context = {
            "location_info": await self._get_location_info(location_id, db),
            "historical_patterns": await self._get_historical_patterns(location_id, forecast_date, db),
            "weather": await self._get_weather_data(location_id, forecast_date),
            "events": await self._get_events_data(location_id, forecast_date, horizon_hours, db),
            "seasonal_factors": await self._get_seasonal_factors(forecast_date),
            "market_conditions": await self._get_market_conditions(db)
        }
        
        return context
    
    async def _get_location_info(self, location_id: int, db: Session) -> Dict[str, Any]:
        """Get location information"""
        location = db.query(Location).filter(Location.id == location_id).first()
        if not location:
            return {}
        
        return {
            "id": location.id,
            "name": location.name,
            "sector": location.sector,
            "coordinates": location.coordinates,
            "population_density": location.population_density,
            "economic_zone": location.economic_zone
        }
    
    async def _get_historical_patterns(self, location_id: int, forecast_date: datetime, db: Session) -> Dict[str, Any]:
        """Get historical demand patterns"""
        # Get historical forecasts for the last 30 days
        thirty_days_ago = forecast_date - timedelta(days=30)
        
        historical_forecasts = db.query(DemandForecast).filter(
            DemandForecast.location_id == location_id,
            DemandForecast.forecast_date >= thirty_days_ago,
            DemandForecast.forecast_date < forecast_date
        ).all()
        
        if not historical_forecasts:
            return {"average_daily_demand": 10.0, "trend": "stable"}
        
        # Calculate patterns
        total_demand = sum(f.predicted_demand for f in historical_forecasts)
        avg_daily_demand = total_demand / len(historical_forecasts)
        
        # Simple trend calculation
        recent_avg = sum(f.predicted_demand for f in historical_forecasts[-7:]) / 7
        older_avg = sum(f.predicted_demand for f in historical_forecasts[:7]) / 7
        
        trend = "increasing" if recent_avg > older_avg * 1.1 else "decreasing" if recent_avg < older_avg * 0.9 else "stable"
        
        return {
            "average_daily_demand": avg_daily_demand,
            "trend": trend,
            "volatility": 0.2,
            "day_of_week_pattern": self._calculate_dow_pattern(historical_forecasts),
            "hour_of_day_pattern": self._calculate_hod_pattern(historical_forecasts)
        }
    
    def _calculate_dow_pattern(self, forecasts: List[DemandForecast]) -> Dict[str, float]:
        """Calculate day of week pattern"""
        dow_totals = {i: 0 for i in range(7)}
        dow_counts = {i: 0 for i in range(7)}
        
        for forecast in forecasts:
            dow = forecast.forecast_date.weekday()
            dow_totals[dow] += forecast.predicted_demand
            dow_counts[dow] += 1
        
        return {
            day: total / count if count > 0 else 1.0
            for day, (total, count) in enumerate(zip(dow_totals.values(), dow_counts.values()))
        }
    
    def _calculate_hod_pattern(self, forecasts: List[DemandForecast]) -> Dict[str, float]:
        """Calculate hour of day pattern"""
        hod_totals = {i: 0 for i in range(24)}
        hod_counts = {i: 0 for i in range(24)}
        
        for forecast in forecasts:
            hod = forecast.forecast_date.hour
            hod_totals[hod] += forecast.predicted_demand
            hod_counts[hod] += 1
        
        return {
            hour: total / count if count > 0 else 1.0
            for hour, (total, count) in enumerate(zip(hod_totals.values(), hod_counts.values()))
        }
    
    async def _get_weather_data(self, location_id: int, forecast_date: datetime) -> Dict[str, Any]:
        """Get weather data for location and date"""
        # Mock weather data - in production, integrate with weather API
        return {
            "temperature": 22.5,
            "humidity": 65,
            "precipitation": 0.0,
            "wind_speed": 12.0,
            "demand_factor": 1.0  # Weather impact on demand
        }
    
    async def _get_events_data(self, location_id: int, forecast_date: datetime, horizon_hours: int, db: Session) -> Dict[str, Any]:
        """Get events data that might affect demand"""
        # Get market events for the forecast period
        end_date = forecast_date + timedelta(hours=horizon_hours)
        
        events = db.query(Event).filter(
            Event.location_lat.isnot(None),
            Event.start_time >= forecast_date,
            Event.end_time <= end_date
        ).all()
        
        if not events:
            return {"event_impact": 1.0, "events": []}
        
        # Calculate event impact
        total_impact = sum(event.get_impact_score() for event in events)
        event_impact = 1.0 + (total_impact / 100)  # Convert percentage to multiplier
        
        return {
            "event_impact": event_impact,
            "events": [
                {
                    "name": event.description or "Unknown Event",
                    "type": event.event_type,
                    "demand_impact": event.get_impact_score(),
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat() if event.end_time else None
                }
                for event in events
            ]
        }
    
    async def _get_seasonal_factors(self, forecast_date: datetime) -> Dict[str, Any]:
        """Get seasonal factors"""
        month = forecast_date.month
        day_of_year = forecast_date.timetuple().tm_yday
        
        # Simple seasonal factors
        seasonal_factors = {
            1: 0.8,   # January - low
            2: 0.9,   # February - low
            3: 1.0,   # March - normal
            4: 1.1,   # April - slightly high
            5: 1.2,   # May - high
            6: 1.3,   # June - peak
            7: 1.3,   # July - peak
            8: 1.2,   # August - high
            9: 1.1,   # September - slightly high
            10: 1.0,  # October - normal
            11: 0.9,  # November - low
            12: 0.8   # December - low
        }
        
        return {
            "current_factor": seasonal_factors.get(month, 1.0),
            "month": month,
            "day_of_year": day_of_year
        }
    
    async def _get_market_conditions(self, db: Session) -> Dict[str, Any]:
        """Get current market conditions"""
        # Mock market conditions - in production, integrate with market data APIs
        return {
            "economic_indicator": "stable",
            "consumer_confidence": 75.5,
            "market_volatility": 0.15,
            "competition_level": "medium"
        }

class DemandForecastingEngine:
    """LCM-style demand forecasting engine with context-aware AI reasoning"""
    
    def __init__(self):
        self.ai_manager = None
        self.context_builder = ContextBuilder()
        self.forecast_cache = {}
        
    async def initialize(self):
        """Initialize the forecasting engine"""
        logger.info("Initializing Demand Forecasting Engine")
        
        # Initialize AI model manager
        self.ai_manager = await get_ai_model_manager()
        
        logger.info("Demand Forecasting Engine initialized successfully")
    
    async def generate_forecast(
        self,
        sku_id: int,
        location_id: int,
        forecast_date: datetime,
        horizon_hours: int = 24,
        db: Session = None
    ) -> DemandForecast:
        """Generate demand forecast for a specific SKU and location"""
        
        if not db:
            db = next(get_db())
        
        try:
            # Get SKU and location
            sku = db.query(SKU).filter(SKU.id == sku_id).first()
            location = db.query(Location).filter(Location.id == location_id).first()
            
            if not sku or not location:
                raise ValueError("SKU or location not found")
            
            # Build comprehensive context
            context = await self.context_builder.build_context(
                location_id=location_id,
                forecast_date=forecast_date,
                horizon_hours=horizon_hours,
                db=db
            )
            
            # Generate forecast using AI reasoning
            if self.ai_manager:
                forecast_result = await self._generate_ai_forecast(
                    sku=sku,
                    location=location,
                    context=context,
                    forecast_date=forecast_date,
                    horizon_hours=horizon_hours
                )
            else:
                forecast_result = await self._generate_fallback_forecast(
                    sku=sku,
                    location=location,
                    context=context,
                    forecast_date=forecast_date,
                    horizon_hours=horizon_hours
                )
            
            # Create forecast record
            forecast = DemandForecast(
                sku_id=sku_id,
                location_id=location_id,
                forecast_date=forecast_date,
                horizon_hours=horizon_hours,
                predicted_demand=forecast_result["predicted_demand"],
                confidence_lower=forecast_result["confidence_lower"],
                confidence_upper=forecast_result["confidence_upper"],
                model_used=forecast_result.get("model", "fallback"),
                reasoning=forecast_result.get("reasoning", ""),
                context_data=context
            )
            
            db.add(forecast)
            db.commit()
            
            logger.info(f"Generated forecast for SKU {sku_id} at location {location_id}", 
                       predicted_demand=forecast_result["predicted_demand"])
            
            return forecast
            
        except Exception as e:
            logger.error(f"Failed to generate forecast for SKU {sku_id} at location {location_id}", 
                        error=str(e))
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _generate_ai_forecast(
        self,
        sku: SKU,
        location: Location,
        context: Dict[str, Any],
        forecast_date: datetime,
        horizon_hours: int
    ) -> Dict[str, Any]:
        """Generate forecast using AI reasoning"""
        
        # Create system message for forecasting
        system_message = """You are an expert demand forecasting analyst for a hyperlocal logistics system. 
        Your task is to predict demand for specific products in specific locations based on comprehensive context data.
        
        Analyze the provided context carefully and provide:
        1. A precise demand prediction
        2. Confidence interval (lower and upper bounds)
        3. Detailed reasoning for your prediction
        
        Consider factors like:
        - Historical demand patterns
        - Weather conditions
        - Special events
        - Seasonal trends
        - Market conditions
        - Day of week and time patterns
        
        Provide your response in JSON format with the following structure:
        {
            "predicted_demand": <number>,
            "confidence_lower": <number>,
            "confidence_upper": <number>,
            "reasoning": "<detailed explanation of your prediction>"
        }"""
        
        # Create prompt
        prompt = f"""
        Please forecast demand for the following:
        
        Product: {sku.name} ({sku.sku_code})
        Category: {sku.category}
        Location: {location.name} in {location.sector}
        Forecast Date: {forecast_date.strftime('%Y-%m-%d %H:%M')}
        Horizon: {horizon_hours} hours
        
        Context Data:
        {json.dumps(context, indent=2)}
        
        Provide your response in JSON format as specified in the system message.
        """
        
        try:
            # Generate response using AI model manager
            response = await self.ai_manager.generate_response(
                prompt=prompt,
                system_message=system_message,
                model=settings.FORECASTING_MODEL,
                provider=settings.DEFAULT_AI_PROVIDER
            )
            
            # Parse JSON response
            try:
                result = json.loads(response["content"])
                return {
                    "predicted_demand": float(result["predicted_demand"]),
                    "confidence_lower": float(result["confidence_lower"]),
                    "confidence_upper": float(result["confidence_upper"]),
                    "reasoning": result["reasoning"],
                    "model": response["model"],
                    "provider": response["provider"]
                }
            except (json.JSONDecodeError, KeyError) as e:
                logger.error("Failed to parse AI response", error=str(e))
                # Fallback to simple prediction
                return await self._generate_fallback_forecast(
                    sku, location, context, forecast_date, horizon_hours
                )
                
        except Exception as e:
            logger.error("AI forecast generation failed", error=str(e))
            # Fallback to simple prediction
            return await self._generate_fallback_forecast(
                sku, location, context, forecast_date, horizon_hours
            )
    
    async def _generate_fallback_forecast(
        self,
        sku: SKU,
        location: Location,
        context: Dict[str, Any],
        forecast_date: datetime,
        horizon_hours: int
    ) -> Dict[str, Any]:
        """Generate fallback forecast using simple heuristics"""
        
        # Base demand from historical patterns
        base_demand = context.get("historical_patterns", {}).get("average_daily_demand", 10.0)
        
        # Apply weather factor
        weather_factor = context.get("weather", {}).get("demand_factor", 1.0)
        
        # Apply event factor
        event_factor = context.get("events", {}).get("event_impact", 1.0)
        
        # Apply seasonal factor
        seasonal_factor = context.get("seasonal_factors", {}).get("current_factor", 1.0)
        
        # Calculate predicted demand
        predicted_demand = base_demand * weather_factor * event_factor * seasonal_factor
        
        # Calculate confidence interval (20% range)
        confidence_range = predicted_demand * 0.2
        confidence_lower = max(0, predicted_demand - confidence_range)
        confidence_upper = predicted_demand + confidence_range
        
        return {
            "predicted_demand": predicted_demand,
            "confidence_lower": confidence_lower,
            "confidence_upper": confidence_upper,
            "reasoning": f"Fallback forecast using heuristics: base_demand={base_demand}, weather_factor={weather_factor}, event_factor={event_factor}, seasonal_factor={seasonal_factor}",
            "model": "fallback",
            "provider": "heuristic"
        } 