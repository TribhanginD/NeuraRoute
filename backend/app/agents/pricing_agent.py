import asyncio
import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import uuid
import json

from app.agents.base_agent import BaseAgent
from app.models.inventory import SKU
from app.models.forecasting import DemandForecast
from app.core.database import get_db
from app.ai.model_manager import get_ai_model_manager

logger = structlog.get_logger()

class PricingEngine:
    """AI-powered pricing engine for dynamic pricing decisions"""
    
    def __init__(self):
        self.ai_manager = None
        self.pricing_cache = {}
    
    async def initialize(self):
        """Initialize the pricing engine"""
        logger.info("Initializing Pricing Engine")
        
        # Initialize AI model manager
        self.ai_manager = await get_ai_model_manager()
        
        logger.info("Pricing Engine initialized successfully")
    
    async def calculate_optimal_price(
        self,
        sku: SKU,
        current_demand: float,
        forecasted_demand: float,
        competitor_prices: Dict[str, float],
        market_conditions: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Calculate optimal price using AI reasoning"""
        
        # Create system message for pricing
        system_message = """You are an expert pricing analyst for a hyperlocal logistics system.
        Your task is to determine the optimal price for products based on market conditions, demand, and competition.
        
        Consider factors like:
        - Current and forecasted demand
        - Competitor pricing
        - Market conditions
        - Product costs and margins
        - Seasonal factors
        - Inventory levels
        
        Provide your response in JSON format with the following structure:
        {
            "optimal_price": <number>,
            "price_change_percentage": <number>,
            "reasoning": "<detailed explanation of your pricing decision>",
            "confidence": <number between 0 and 1>,
            "risk_level": "<low/medium/high>"
        }"""
        
        # Create prompt
        prompt = f"""
        Please calculate the optimal price for the following product:
        
        Product: {sku.name} ({sku.sku_code})
        Category: {sku.category}
        Current Price: ${sku.price}
        Cost: ${sku.cost}
        Current Demand: {current_demand}
        Forecasted Demand: {forecasted_demand}
        
        Competitor Prices:
        {json.dumps(competitor_prices, indent=2)}
        
        Market Conditions:
        {json.dumps(market_conditions, indent=2)}
        
        Additional Context:
        {json.dumps(kwargs, indent=2)}
        
        Provide your response in JSON format as specified in the system message.
        """
        
        try:
            # Generate response using AI model manager
            response = await self.ai_manager.generate_response(
                prompt=prompt,
                system_message=system_message,
                model="gpt-4o",  # Use specific pricing model
                provider="openai"
            )
            
            # Parse JSON response
            try:
                result = json.loads(response["content"])
                return {
                    "optimal_price": float(result["optimal_price"]),
                    "price_change_percentage": float(result["price_change_percentage"]),
                    "reasoning": result["reasoning"],
                    "confidence": float(result["confidence"]),
                    "risk_level": result["risk_level"],
                    "model": response["model"],
                    "provider": response["provider"]
                }
            except (json.JSONDecodeError, KeyError) as e:
                logger.error("Failed to parse AI pricing response", error=str(e))
                return await self._calculate_fallback_price(
                    sku, current_demand, forecasted_demand, competitor_prices, market_conditions
                )
                
        except Exception as e:
            logger.error("AI pricing calculation failed", error=str(e))
            return await self._calculate_fallback_price(
                sku, current_demand, forecasted_demand, competitor_prices, market_conditions
            )
    
    async def _calculate_fallback_price(
        self,
        sku: SKU,
        current_demand: float,
        forecasted_demand: float,
        competitor_prices: Dict[str, float],
        market_conditions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate fallback price using simple heuristics"""
        
        # Base price from cost and markup
        base_markup = 0.15  # 15% markup
        base_price = sku.cost * (1 + base_markup)
        
        # Adjust for demand
        demand_factor = forecasted_demand / current_demand if current_demand > 0 else 1.0
        demand_adjustment = min(max(demand_factor, 0.8), 1.2)  # Limit adjustment to ±20%
        
        # Adjust for competition
        if competitor_prices:
            avg_competitor_price = sum(competitor_prices.values()) / len(competitor_prices)
            competition_factor = avg_competitor_price / sku.price if sku.price > 0 else 1.0
            competition_adjustment = min(max(competition_factor, 0.9), 1.1)  # Limit to ±10%
        else:
            competition_adjustment = 1.0
        
        # Calculate optimal price
        optimal_price = base_price * demand_adjustment * competition_adjustment
        
        # Calculate price change
        price_change_percentage = ((optimal_price - sku.price) / sku.price) * 100 if sku.price > 0 else 0
        
        return {
            "optimal_price": optimal_price,
            "price_change_percentage": price_change_percentage,
            "reasoning": f"Fallback pricing: base_price={base_price}, demand_adjustment={demand_adjustment}, competition_adjustment={competition_adjustment}",
            "confidence": 0.6,
            "risk_level": "medium",
            "model": "fallback",
            "provider": "heuristic"
        }
    
    def clear_cache(self):
        """Clear pricing cache"""
        self.pricing_cache.clear()

class PricingAgent(BaseAgent):
    """Autonomous agent for dynamic pricing decisions"""
    
    async def _initialize_agent(self):
        """Initialize pricing agent specific components"""
        logger.info("Initializing Pricing Agent components")
        
        # Initialize pricing engine
        self.pricing_engine = PricingEngine()
        await self.pricing_engine.initialize()
        
        # Load pricing strategies and market data
        await self._load_pricing_config()
        
        logger.info("Pricing Agent components initialized")
    
    async def _stop_agent(self):
        """Stop pricing agent specific components"""
        logger.info("Stopping Pricing Agent components")
        
        # Clear pricing cache
        self.pricing_engine.clear_cache()
        
        logger.info("Pricing Agent components stopped")
    
    async def _load_pricing_config(self):
        """Load pricing configuration"""
        self.pricing_config = {
            "price_check_interval": self.config.get("price_check_interval", 1800),  # 30 minutes
            "competitor_check_interval": self.config.get("competitor_check_interval", 3600),  # 1 hour
            "max_price_change": self.config.get("max_price_change", 0.2),  # 20%
            "min_price_change": self.config.get("min_price_change", 0.05),  # 5%
            "confidence_threshold": self.config.get("confidence_threshold", 0.7)
        }
    
    async def _run_cycle_logic(self):
        """Run pricing agent cycle logic"""
        try:
            # Check if it's time for pricing analysis
            if await self._should_run_pricing_analysis():
                await self._run_pricing_analysis()
            
            # Check if it's time for competitor analysis
            if await self._should_run_competitor_analysis():
                await self._run_competitor_analysis()
            
            # Update pricing metrics
            await self._update_pricing_metrics()
            
        except Exception as e:
            logger.error("Pricing agent cycle failed", error=str(e))
            await self._log_action(
                task_id=str(uuid.uuid4()),
                action="pricing_cycle",
                input_data={},
                status="failed",
                error_message=str(e)
            )
    
    async def _should_run_pricing_analysis(self) -> bool:
        """Check if pricing analysis should run"""
        last_pricing = self.memory.get("last_pricing_analysis")
        if not last_pricing:
            return True
        
        last_time = datetime.fromisoformat(last_pricing)
        interval = timedelta(seconds=self.pricing_config["price_check_interval"])
        return datetime.utcnow() - last_time >= interval
    
    async def _should_run_competitor_analysis(self) -> bool:
        """Check if competitor analysis should run"""
        last_competitor = self.memory.get("last_competitor_analysis")
        if not last_competitor:
            return True
        
        last_time = datetime.fromisoformat(last_competitor)
        interval = timedelta(seconds=self.pricing_config["competitor_check_interval"])
        return datetime.utcnow() - last_time >= interval
    
    async def _run_pricing_analysis(self):
        """Run comprehensive pricing analysis"""
        logger.info("Running pricing analysis")
        
        db = next(get_db())
        try:
            # Get all active SKUs
            skus = db.query(SKU).filter(SKU.is_active == True).all()
            
            for sku in skus:
                await self._analyze_sku_pricing(sku, db)
            
            # Update last pricing analysis time
            await self._store_memory("last_pricing_analysis", datetime.utcnow().isoformat())
            
            logger.info(f"Completed pricing analysis for {len(skus)} SKUs")
            
        except Exception as e:
            logger.error("Pricing analysis failed", error=str(e))
            raise
        finally:
            db.close()
    
    async def _analyze_sku_pricing(self, sku: SKU, db: Session):
        """Analyze pricing for a specific SKU"""
        try:
            # Get current demand data
            current_demand = await self._get_current_demand(sku.id, db)
            
            # Get forecasted demand
            forecasted_demand = await self._get_forecasted_demand(sku.id, db)
            
            # Get competitor prices
            competitor_prices = await self._get_competitor_prices(sku, db)
            
            # Get market conditions
            market_conditions = await self._get_market_conditions(db)
            
            # Calculate optimal price
            pricing_result = await self.pricing_engine.calculate_optimal_price(
                sku=sku,
                current_demand=current_demand,
                forecasted_demand=forecasted_demand,
                competitor_prices=competitor_prices,
                market_conditions=market_conditions
            )
            
            # Apply price change if within thresholds
            if self._should_apply_price_change(pricing_result):
                await self._apply_price_change(sku, pricing_result, db)
            
            # Log pricing decision
            await self._log_action(
                task_id=str(uuid.uuid4()),
                action="pricing_analysis",
                input_data={
                    "sku_id": sku.id,
                    "current_price": sku.price,
                    "current_demand": current_demand,
                    "forecasted_demand": forecasted_demand
                },
                status="completed",
                output_data=pricing_result,
                reasoning=pricing_result.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze pricing for SKU {sku.id}", error=str(e))
    
    async def _get_current_demand(self, sku_id: int, db: Session) -> float:
        """Get current demand for SKU"""
        # In a real system, this would query recent order data
        # For MVP, return simulated demand
        import random
        return random.uniform(10, 100)
    
    async def _get_forecasted_demand(self, sku_id: int, db: Session) -> float:
        """Get forecasted demand for SKU"""
        # Get the most recent forecast
        forecast = db.query(DemandForecast).filter(
            DemandForecast.sku_id == sku_id
        ).order_by(DemandForecast.forecast_date.desc()).first()
        
        if forecast:
            return forecast.predicted_demand
        else:
            return 50.0  # Default forecast
    
    async def _get_competitor_prices(self, sku: SKU, db: Session) -> Dict[str, float]:
        """Get competitor prices for SKU"""
        # In a real system, this would query competitor price data
        # For MVP, return simulated competitor prices
        import random
        return {
            "competitor_1": sku.price * random.uniform(0.8, 1.2),
            "competitor_2": sku.price * random.uniform(0.8, 1.2),
            "competitor_3": sku.price * random.uniform(0.8, 1.2)
        }
    
    async def _get_market_conditions(self, db: Session) -> Dict[str, Any]:
        """Get current market conditions"""
        # In a real system, this would query market data APIs
        # For MVP, return simulated market conditions
        import random
        return {
            "economic_indicator": random.choice(["growing", "stable", "declining"]),
            "consumer_confidence": random.uniform(60, 90),
            "market_volatility": random.uniform(0.1, 0.3),
            "competition_level": random.choice(["low", "medium", "high"])
        }
    
    def _should_apply_price_change(self, pricing_result: Dict[str, Any]) -> bool:
        """Check if price change should be applied"""
        price_change = abs(pricing_result.get("price_change_percentage", 0))
        confidence = pricing_result.get("confidence", 0)
        
        return (
            price_change >= self.pricing_config["min_price_change"] and
            price_change <= self.pricing_config["max_price_change"] and
            confidence >= self.pricing_config["confidence_threshold"]
        )
    
    async def _apply_price_change(self, sku: SKU, pricing_result: Dict[str, Any], db: Session):
        """Apply price change to SKU"""
        new_price = pricing_result["optimal_price"]
        
        # Update SKU price
        sku.price = new_price
        sku.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Updated price for SKU {sku.id} to ${new_price:.2f}")
    
    async def _run_competitor_analysis(self):
        """Run competitor pricing analysis"""
        logger.info("Running competitor analysis")
        
        # Update last competitor analysis time
        await self._store_memory("last_competitor_analysis", datetime.utcnow().isoformat())
        
        logger.info("Completed competitor analysis")
    
    async def _update_pricing_metrics(self):
        """Update pricing performance metrics"""
        # Update agent metrics
        self.tasks_completed += 1
        self.last_heartbeat = datetime.utcnow()
    
    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pricing agent specific action"""
        if action == "analyze_pricing":
            return await self._execute_pricing_analysis(parameters)
        elif action == "get_pricing_recommendations":
            return await self._get_pricing_recommendations(parameters)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _execute_pricing_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pricing analysis for specific parameters"""
        sku_id = parameters.get("sku_id")
        if not sku_id:
            raise ValueError("sku_id is required for pricing analysis")
        
        db = next(get_db())
        try:
            sku = db.query(SKU).filter(SKU.id == sku_id).first()
            if not sku:
                raise ValueError(f"SKU {sku_id} not found")
            
            await self._analyze_sku_pricing(sku, db)
            
            return {"status": "completed", "sku_id": sku_id}
            
        finally:
            db.close()
    
    async def _get_pricing_recommendations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get pricing recommendations for SKUs"""
        db = next(get_db())
        try:
            skus = db.query(SKU).filter(SKU.is_active == True).all()
            
            recommendations = []
            for sku in skus:
                # Get basic pricing data
                current_demand = await self._get_current_demand(sku.id, db)
                forecasted_demand = await self._get_forecasted_demand(sku.id, db)
                competitor_prices = await self._get_competitor_prices(sku, db)
                market_conditions = await self._get_market_conditions(db)
                
                # Calculate optimal price
                pricing_result = await self.pricing_engine.calculate_optimal_price(
                    sku=sku,
                    current_demand=current_demand,
                    forecasted_demand=forecasted_demand,
                    competitor_prices=competitor_prices,
                    market_conditions=market_conditions
                )
                
                recommendations.append({
                    "sku_id": sku.id,
                    "sku_name": sku.name,
                    "current_price": sku.price,
                    "recommended_price": pricing_result["optimal_price"],
                    "price_change_percentage": pricing_result["price_change_percentage"],
                    "confidence": pricing_result["confidence"],
                    "risk_level": pricing_result["risk_level"],
                    "reasoning": pricing_result["reasoning"]
                })
            
            return {
                "status": "completed",
                "recommendations": recommendations,
                "total_skus": len(skus)
            }
            
        finally:
            db.close() 