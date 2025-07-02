import asyncio
import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.agents.base_agent import BaseAgent
from app.models.inventory import SKU, Location
from app.models.forecasting import DemandForecast
from app.forecasting.engine import DemandForecastingEngine
from app.core.database import get_db

logger = structlog.get_logger()

class ForecastingAgent(BaseAgent):
    """Autonomous agent for demand forecasting coordination"""
    
    async def _initialize_agent(self):
        """Initialize forecasting agent specific components"""
        logger.info("Initializing Forecasting Agent components")
        
        # Initialize forecasting engine
        self.forecasting_engine = DemandForecastingEngine()
        await self.forecasting_engine.initialize()
        
        # Load forecasting configuration
        await self._load_forecasting_config()
        
        logger.info("Forecasting Agent components initialized")
    
    async def _stop_agent(self):
        """Stop forecasting agent specific components"""
        logger.info("Stopping Forecasting Agent components")
        
        # Clear forecasting cache
        self.forecasting_engine.forecast_cache.clear()
        
        logger.info("Forecasting Agent components stopped")
    
    async def _run_cycle_logic(self):
        """Run forecasting agent cycle logic"""
        logger.debug("Running Forecasting Agent cycle", agent_id=self.agent_id)
        
        try:
            # Get active SKUs and locations
            active_skus = await self._get_active_skus()
            active_locations = await self._get_active_locations()
            
            # Check for SKUs that need forecasting
            skus_needing_forecast = await self._identify_forecast_needs(active_skus, active_locations)
            
            # Generate forecasts
            forecasts_generated = []
            if skus_needing_forecast:
                forecasts_generated = await self._generate_forecasts(skus_needing_forecast)
            
            # Update forecast accuracy
            await self._update_forecast_accuracy()
            
            # Analyze forecast trends
            await self._analyze_forecast_trends()
            
            # Store cycle results in memory
            await self._store_memory("cycle", f"cycle_{self.cycle_count}", {
                "timestamp": datetime.utcnow().isoformat(),
                "active_skus": len(active_skus),
                "active_locations": len(active_locations),
                "forecasts_generated": len(forecasts_generated),
                "cycle_duration_ms": self.average_response_time
            })
            
            self.tasks_completed += 1
            
        except Exception as e:
            logger.error("Error in Forecasting Agent cycle", agent_id=self.agent_id, error=str(e))
            self.tasks_failed += 1
            raise
    
    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute forecasting agent specific actions"""
        
        if action == "generate_forecast":
            sku_id = parameters.get("sku_id")
            location_id = parameters.get("location_id")
            horizon_hours = parameters.get("horizon_hours", 24)
            return await self._generate_specific_forecast(sku_id, location_id, horizon_hours)
        
        elif action == "batch_forecast":
            sku_ids = parameters.get("sku_ids", [])
            location_ids = parameters.get("location_ids", [])
            return await self._generate_batch_forecasts(sku_ids, location_ids)
        
        elif action == "analyze_accuracy":
            days_back = parameters.get("days_back", 7)
            return await self._analyze_forecast_accuracy(days_back)
        
        elif action == "optimize_model":
            sku_id = parameters.get("sku_id")
            return await self._optimize_forecast_model(sku_id)
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _get_active_skus(self) -> List[Dict[str, Any]]:
        """Get all active SKUs"""
        db = next(get_db())
        
        try:
            skus = db.query(SKU).filter(SKU.is_active == True).all()
            
            active_skus = []
            for sku in skus:
                active_skus.append({
                    "sku_id": sku.id,
                    "sku_code": sku.sku_code,
                    "name": sku.name,
                    "category": sku.category,
                    "base_price": sku.base_price
                })
            
            return active_skus
            
        finally:
            db.close()
    
    async def _get_active_locations(self) -> List[Dict[str, Any]]:
        """Get all active locations"""
        db = next(get_db())
        
        try:
            locations = db.query(Location).filter(Location.is_active == True).all()
            
            active_locations = []
            for location in locations:
                active_locations.append({
                    "location_id": location.id,
                    "name": location.name,
                    "sector": location.sector,
                    "latitude": location.latitude,
                    "longitude": location.longitude
                })
            
            return active_locations
            
        finally:
            db.close()
    
    async def _identify_forecast_needs(self, skus: List[Dict[str, Any]], locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify SKU-location combinations that need forecasting"""
        
        forecast_needs = []
        current_time = datetime.utcnow()
        
        for sku in skus:
            for location in locations:
                # Check if forecast is needed (older than 1 hour)
                last_forecast = await self._get_last_forecast(sku["sku_id"], location["location_id"])
                
                if not last_forecast or (current_time - last_forecast["forecast_date"]).total_seconds() > 3600:
                    forecast_needs.append({
                        "sku_id": sku["sku_id"],
                        "location_id": location["location_id"],
                        "sku_code": sku["sku_code"],
                        "location_name": location["name"],
                        "reason": "forecast_expired" if last_forecast else "no_forecast"
                    })
        
        return forecast_needs
    
    async def _get_last_forecast(self, sku_id: int, location_id: int) -> Dict[str, Any]:
        """Get the most recent forecast for a SKU-location combination"""
        db = next(get_db())
        
        try:
            forecast = db.query(DemandForecast).filter(
                DemandForecast.sku_id == sku_id,
                DemandForecast.location_id == location_id
            ).order_by(DemandForecast.forecast_date.desc()).first()
            
            if forecast:
                return {
                    "forecast_id": forecast.id,
                    "forecast_date": forecast.forecast_date,
                    "predicted_demand": forecast.predicted_demand,
                    "accuracy_score": forecast.accuracy_score
                }
            
            return None
            
        finally:
            db.close()
    
    async def _generate_forecasts(self, forecast_needs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate forecasts for identified needs"""
        
        forecasts_generated = []
        
        for need in forecast_needs:
            try:
                # Generate forecast
                forecast = await self.forecasting_engine.generate_forecast(
                    sku_id=need["sku_id"],
                    location_id=need["location_id"],
                    forecast_date=datetime.utcnow(),
                    horizon_hours=24
                )
                
                forecasts_generated.append({
                    "sku_id": need["sku_id"],
                    "location_id": need["location_id"],
                    "forecast_id": forecast.id,
                    "predicted_demand": forecast.predicted_demand,
                    "confidence_interval": forecast.get_confidence_interval(),
                    "reasoning": forecast.reasoning[:200] + "..." if len(forecast.reasoning) > 200 else forecast.reasoning
                })
                
                logger.info(f"Forecast generated for {need['sku_code']} at {need['location_name']}")
                
            except Exception as e:
                logger.error(f"Failed to generate forecast for {need['sku_code']} at {need['location_name']}", error=str(e))
        
        return forecasts_generated
    
    async def _update_forecast_accuracy(self):
        """Update forecast accuracy based on actual demand"""
        
        # For MVP, simulate accuracy updates
        # In production, this would compare forecasts with actual sales data
        
        db = next(get_db())
        
        try:
            # Get recent forecasts
            recent_forecasts = db.query(DemandForecast).filter(
                DemandForecast.forecast_date >= datetime.utcnow() - timedelta(days=1)
            ).all()
            
            for forecast in recent_forecasts:
                # Simulate actual demand (in production, this would be real data)
                import random
                actual_demand = forecast.predicted_demand * random.uniform(0.8, 1.2)
                
                # Update accuracy
                forecast.update_accuracy(actual_demand)
            
            db.commit()
            
            logger.info(f"Updated accuracy for {len(recent_forecasts)} forecasts")
            
        except Exception as e:
            logger.error("Failed to update forecast accuracy", error=str(e))
            db.rollback()
        finally:
            db.close()
    
    async def _analyze_forecast_trends(self):
        """Analyze forecast trends and patterns"""
        
        # For MVP, provide basic trend analysis
        # In production, this would use sophisticated trend analysis
        
        trend_analysis = {
            "overall_accuracy": 0.85,  # 85% accuracy
            "trending_products": ["SKU001", "SKU005", "SKU010"],
            "declining_products": ["SKU003", "SKU007"],
            "seasonal_patterns": {
                "weekend_boost": 1.3,  # 30% increase on weekends
                "lunch_peak": 1.5,     # 50% increase during lunch hours
                "dinner_peak": 1.4     # 40% increase during dinner hours
            },
            "weather_impact": {
                "rainy_days": 0.8,     # 20% decrease on rainy days
                "sunny_days": 1.1      # 10% increase on sunny days
            }
        }
        
        # Store trend analysis in memory
        await self._store_memory("trend_analysis", "current_trends", {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": trend_analysis
        })
    
    async def _load_forecasting_config(self):
        """Load forecasting configuration"""
        self.forecasting_config = {
            "default_horizon_hours": 24,
            "forecast_update_interval": 3600,  # 1 hour
            "accuracy_threshold": 0.8,  # 80% accuracy threshold
            "confidence_level": 0.95,
            "max_forecast_age_hours": 1
        }
    
    async def _generate_specific_forecast(self, sku_id: int, location_id: int, horizon_hours: int = 24) -> Dict[str, Any]:
        """Generate a specific forecast"""
        
        try:
            # Generate forecast
            forecast = await self.forecasting_engine.generate_forecast(
                sku_id=sku_id,
                location_id=location_id,
                forecast_date=datetime.utcnow(),
                horizon_hours=horizon_hours
            )
            
            return {
                "success": True,
                "forecast_id": forecast.id,
                "sku_id": sku_id,
                "location_id": location_id,
                "predicted_demand": forecast.predicted_demand,
                "confidence_interval": forecast.get_confidence_interval(),
                "reasoning": forecast.reasoning,
                "model_version": forecast.model_version,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate specific forecast", error=str(e))
            raise
    
    async def _generate_batch_forecasts(self, sku_ids: List[int], location_ids: List[int]) -> Dict[str, Any]:
        """Generate forecasts for multiple SKU-location combinations"""
        
        try:
            # Generate batch forecasts
            forecasts = await self.forecasting_engine.batch_forecast(
                sku_ids=sku_ids,
                location_ids=location_ids,
                forecast_date=datetime.utcnow(),
                horizon_hours=24
            )
            
            forecast_summary = []
            for forecast in forecasts:
                forecast_summary.append({
                    "forecast_id": forecast.id,
                    "sku_id": forecast.sku_id,
                    "location_id": forecast.location_id,
                    "predicted_demand": forecast.predicted_demand,
                    "confidence_interval": forecast.get_confidence_interval()
                })
            
            return {
                "success": True,
                "forecasts_generated": len(forecasts),
                "forecast_summary": forecast_summary,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate batch forecasts", error=str(e))
            raise
    
    async def _analyze_forecast_accuracy(self, days_back: int = 7) -> Dict[str, Any]:
        """Analyze forecast accuracy over a period"""
        
        db = next(get_db())
        
        try:
            # Get forecasts from the specified period
            start_date = datetime.utcnow() - timedelta(days=days_back)
            forecasts = db.query(DemandForecast).filter(
                DemandForecast.forecast_date >= start_date
            ).all()
            
            if not forecasts:
                return {
                    "success": True,
                    "message": "No forecasts found for the specified period",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Calculate accuracy metrics
            accuracy_scores = [f.accuracy_score for f in forecasts if f.accuracy_score is not None]
            
            if accuracy_scores:
                avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
                min_accuracy = min(accuracy_scores)
                max_accuracy = max(accuracy_scores)
            else:
                avg_accuracy = min_accuracy = max_accuracy = 0.0
            
            # Analyze by SKU category
            category_accuracy = {}
            for forecast in forecasts:
                if forecast.sku and forecast.sku.category:
                    category = forecast.sku.category
                    if category not in category_accuracy:
                        category_accuracy[category] = []
                    
                    if forecast.accuracy_score is not None:
                        category_accuracy[category].append(forecast.accuracy_score)
            
            # Calculate category averages
            category_averages = {}
            for category, scores in category_accuracy.items():
                category_averages[category] = sum(scores) / len(scores)
            
            return {
                "success": True,
                "analysis_period": f"{days_back} days",
                "total_forecasts": len(forecasts),
                "accuracy_metrics": {
                    "average_accuracy": avg_accuracy,
                    "min_accuracy": min_accuracy,
                    "max_accuracy": max_accuracy
                },
                "category_accuracy": category_averages,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        finally:
            db.close()
    
    async def _optimize_forecast_model(self, sku_id: int) -> Dict[str, Any]:
        """Optimize forecast model for a specific SKU"""
        
        try:
            db = next(get_db())
            sku = db.query(SKU).filter(SKU.id == sku_id).first()
            
            if not sku:
                raise ValueError(f"SKU {sku_id} not found")
            
            # For MVP, provide basic optimization recommendations
            # In production, this would use sophisticated model optimization
            
            optimization_result = {
                "sku_id": sku_id,
                "sku_code": sku.sku_code,
                "current_model": "ai-enhanced-v1",
                "recommended_improvements": [
                    "Increase training data for seasonal patterns",
                    "Add weather correlation factors",
                    "Optimize confidence intervals"
                ],
                "expected_accuracy_improvement": 0.05,  # 5% improvement
                "implementation_steps": [
                    "Collect additional historical data",
                    "Retrain model with new features",
                    "Validate on test dataset",
                    "Deploy improved model"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            db.close()
            return optimization_result
            
        except Exception as e:
            logger.error(f"Failed to optimize forecast model for SKU {sku_id}", error=str(e))
            raise 