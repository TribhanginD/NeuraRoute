import asyncio
import structlog
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import json

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate

from app.core.config import settings
from app.models.forecasting import Forecast, ForecastContext
from app.models.inventory import SKU, Location
from app.models.simulation import MarketEvent
from app.core.database import get_db

logger = structlog.get_logger()

class DemandForecastingEngine:
    """LCM-style demand forecasting engine with context-aware AI reasoning"""
    
    def __init__(self):
        self.llm = None
        self.context_builder = ContextBuilder()
        self.forecast_cache = {}
        
    async def initialize(self):
        """Initialize the forecasting engine"""
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-4o",
                temperature=0.1,
                api_key=settings.openai_api_key
            )
        elif settings.anthropic_api_key:
            self.llm = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                temperature=0.1,
                api_key=settings.anthropic_api_key
            )
        else:
            logger.warning("No AI API key configured, using fallback forecasting")
            self.llm = None
    
    async def generate_forecast(
        self,
        sku_id: int,
        location_id: int,
        forecast_date: datetime,
        horizon_hours: int = 24,
        db: Session = None
    ) -> Forecast:
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
            if self.llm:
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
            forecast = Forecast(
                sku_id=sku_id,
                location_id=location_id,
                forecast_date=forecast_date,
                horizon_hours=horizon_hours,
                predicted_demand=forecast_result["predicted_demand"],
                confidence_lower=forecast_result["confidence_lower"],
                confidence_upper=forecast_result["confidence_upper"],
                confidence_level=0.95,
                context_data=context,
                reasoning=forecast_result["reasoning"],
                model_version="ai-enhanced-v1"
            )
            
            db.add(forecast)
            db.commit()
            
            logger.info(
                "Forecast generated",
                sku_code=sku.sku_code,
                location=location.name,
                predicted_demand=forecast_result["predicted_demand"],
                confidence_interval=f"{forecast_result['confidence_lower']}-{forecast_result['confidence_upper']}"
            )
            
            return forecast
            
        except Exception as e:
            logger.error("Forecast generation failed", error=str(e))
            db.rollback()
            raise
    
    async def _generate_ai_forecast(
        self,
        sku: SKU,
        location: Location,
        context: Dict[str, Any],
        forecast_date: datetime,
        horizon_hours: int
    ) -> Dict[str, Any]:
        """Generate forecast using AI reasoning"""
        
        # Create reasoning prompt
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert demand forecasting analyst for a hyperlocal logistics system. 
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
            - Day of week and time patterns"""),
            
            HumanMessage(content=f"""
            Please forecast demand for the following:
            
            Product: {sku.name} ({sku.sku_code})
            Category: {sku.category}
            Location: {location.name} in {location.sector}
            Forecast Date: {forecast_date.strftime('%Y-%m-%d %H:%M')}
            Horizon: {horizon_hours} hours
            
            Context Data:
            {json.dumps(context, indent=2)}
            
            Provide your response in JSON format:
            {{
                "predicted_demand": <number>,
                "confidence_lower": <number>,
                "confidence_upper": <number>,
                "reasoning": "<detailed explanation of your prediction>"
            }}
            """)
        ])
        
        # Generate forecast
        response = await self.llm.ainvoke(prompt.format_messages())
        
        try:
            # Parse JSON response
            result = json.loads(response.content)
            return {
                "predicted_demand": float(result["predicted_demand"]),
                "confidence_lower": float(result["confidence_lower"]),
                "confidence_upper": float(result["confidence_upper"]),
                "reasoning": result["reasoning"]
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("Failed to parse AI response", error=str(e))
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
        event_factor = context.get("event_impact", 1.0)
        
        # Apply seasonal factor
        seasonal_factor = context.get("seasonal_factors", {}).get("current_factor", 1.0)
        
        # Calculate predicted demand
        predicted_demand = base_demand * weather_factor * event_factor * seasonal_factor
        
        # Calculate confidence interval (20% range)
        confidence_range = predicted_demand * 0.2
        confidence_lower = max(0, predicted_demand - confidence_range)
        confidence_upper = predicted_demand + confidence_range
        
        reasoning = f"""
        Fallback forecast generated using heuristics:
        - Base demand: {base_demand}
        - Weather factor: {weather_factor}
        - Event factor: {event_factor}
        - Seasonal factor: {seasonal_factor}
        - Final prediction: {predicted_demand}
        """
        
        return {
            "predicted_demand": predicted_demand,
            "confidence_lower": confidence_lower,
            "confidence_upper": confidence_upper,
            "reasoning": reasoning
        }
    
    async def batch_forecast(
        self,
        sku_ids: List[int],
        location_ids: List[int],
        forecast_date: datetime,
        horizon_hours: int = 24,
        db: Session = None
    ) -> List[Forecast]:
        """Generate forecasts for multiple SKU-location combinations"""
        
        forecasts = []
        
        for sku_id in sku_ids:
            for location_id in location_ids:
                try:
                    forecast = await self.generate_forecast(
                        sku_id=sku_id,
                        location_id=location_id,
                        forecast_date=forecast_date,
                        horizon_hours=horizon_hours,
                        db=db
                    )
                    forecasts.append(forecast)
                except Exception as e:
                    logger.error(
                        "Batch forecast failed for SKU-Location",
                        sku_id=sku_id,
                        location_id=location_id,
                        error=str(e)
                    )
        
        return forecasts

class ContextBuilder:
    """Build comprehensive context for forecasting"""
    
    async def build_context(
        self,
        location_id: int,
        forecast_date: datetime,
        horizon_hours: int,
        db: Session
    ) -> Dict[str, Any]:
        """Build comprehensive context for forecasting"""
        
        context = {
            "forecast_date": forecast_date.isoformat(),
            "horizon_hours": horizon_hours,
            "location_id": location_id
        }
        
        # Add weather data
        context["weather"] = await self._get_weather_context(forecast_date)
        
        # Add event data
        context["events"] = await self._get_event_context(location_id, forecast_date, db)
        
        # Add historical patterns
        context["historical_patterns"] = await self._get_historical_context(location_id, db)
        
        # Add seasonal factors
        context["seasonal_factors"] = await self._get_seasonal_context(forecast_date)
        
        # Add market conditions
        context["market_conditions"] = await self._get_market_context(location_id, db)
        
        return context
    
    async def _get_weather_context(self, forecast_date: datetime) -> Dict[str, Any]:
        """Get weather context (simulated for MVP)"""
        # In a real system, this would call a weather API
        import random
        
        return {
            "temperature": random.uniform(15, 25),
            "humidity": random.uniform(40, 80),
            "precipitation": random.uniform(0, 10),
            "condition": random.choice(["sunny", "cloudy", "rainy", "partly_cloudy"]),
            "demand_factor": random.uniform(0.8, 1.2)  # How weather affects demand
        }
    
    async def _get_event_context(
        self,
        location_id: int,
        forecast_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """Get event context affecting demand"""
        
        # Get active events for the location
        events = db.query(MarketEvent).filter(
            MarketEvent.affected_sectors.contains([location_id]),
            MarketEvent.is_active == True,
            MarketEvent.start_time <= forecast_date,
            MarketEvent.end_time >= forecast_date
        ).all()
        
        event_data = []
        total_impact = 1.0
        
        for event in events:
            event_data.append({
                "title": event.title,
                "type": event.event_type,
                "severity": event.severity,
                "demand_effect": event.demand_effect,
                "description": event.description
            })
            total_impact *= event.demand_effect
        
        return {
            "events": event_data,
            "total_impact": total_impact
        }
    
    async def _get_historical_context(self, location_id: int, db: Session) -> Dict[str, Any]:
        """Get historical demand patterns"""
        
        # In a real system, this would query historical order data
        # For MVP, return simulated patterns
        import random
        
        return {
            "average_daily_demand": random.uniform(5, 50),
            "peak_hours": [12, 18, 20],  # Peak demand hours
            "weekend_factor": random.uniform(1.2, 1.8),  # Weekend demand multiplier
            "trend": random.uniform(0.9, 1.1)  # Recent trend
        }
    
    async def _get_seasonal_context(self, forecast_date: datetime) -> Dict[str, Any]:
        """Get seasonal factors"""
        
        month = forecast_date.month
        day_of_week = forecast_date.weekday()
        hour = forecast_date.hour
        
        # Seasonal factors
        seasonal_factors = {
            1: 0.8,   # January (post-holiday)
            2: 0.9,   # February
            3: 1.0,   # March
            4: 1.1,   # April
            5: 1.2,   # May
            6: 1.3,   # June (summer)
            7: 1.3,   # July
            8: 1.2,   # August
            9: 1.1,   # September
            10: 1.0,  # October
            11: 1.1,  # November
            12: 1.4   # December (holiday season)
        }
        
        # Day of week factors
        day_factors = {
            0: 0.8,   # Monday
            1: 0.9,   # Tuesday
            2: 1.0,   # Wednesday
            3: 1.0,   # Thursday
            4: 1.1,   # Friday
            5: 1.3,   # Saturday
            6: 1.2    # Sunday
        }
        
        # Hour factors
        hour_factors = {
            6: 0.3,   # Early morning
            7: 0.5,
            8: 0.7,
            9: 0.8,
            10: 0.9,
            11: 1.0,
            12: 1.5,  # Lunch peak
            13: 1.3,
            14: 1.0,
            15: 0.9,
            16: 1.0,
            17: 1.2,
            18: 1.6,  # Dinner peak
            19: 1.4,
            20: 1.2,
            21: 1.0,
            22: 0.8,
            23: 0.6,
            0: 0.4    # Late night
        }
        
        current_factor = (
            seasonal_factors.get(month, 1.0) *
            day_factors.get(day_of_week, 1.0) *
            hour_factors.get(hour, 1.0)
        )
        
        return {
            "month_factor": seasonal_factors.get(month, 1.0),
            "day_factor": day_factors.get(day_of_week, 1.0),
            "hour_factor": hour_factors.get(hour, 1.0),
            "current_factor": current_factor
        }
    
    async def _get_market_context(self, location_id: int, db: Session) -> Dict[str, Any]:
        """Get market conditions context"""
        
        # In a real system, this would query competitor and market data
        # For MVP, return simulated data
        import random
        
        return {
            "competitor_prices": {
                "competitor_1": random.uniform(0.8, 1.2),
                "competitor_2": random.uniform(0.8, 1.2),
                "competitor_3": random.uniform(0.8, 1.2)
            },
            "market_trends": {
                "demand_trend": random.uniform(0.9, 1.1),
                "price_trend": random.uniform(0.95, 1.05),
                "competition_level": random.uniform(0.5, 1.5)
            }
        } 