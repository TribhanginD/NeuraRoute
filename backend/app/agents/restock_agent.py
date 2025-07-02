import asyncio
import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import uuid

from app.agents.base_agent import BaseAgent
from app.models.inventory import InventoryItem, SKU
from app.models.merchant import Merchant
from app.models.forecasting import DemandForecast
from app.core.database import get_db

logger = structlog.get_logger()

class RestockAgent(BaseAgent):
    """Autonomous agent for inventory restocking decisions"""
    
    async def _initialize_agent(self):
        """Initialize restock agent specific components"""
        logger.info("Initializing Restock Agent components")
        
        # Load restocking thresholds and policies
        await self._load_restock_policies()
        
        # Initialize inventory monitoring
        self.inventory_alerts = []
        self.restock_orders = []
        
        logger.info("Restock Agent components initialized")
    
    async def _stop_agent(self):
        """Stop restock agent specific components"""
        logger.info("Stopping Restock Agent components")
        
        # Clear any pending alerts
        self.inventory_alerts.clear()
        self.restock_orders.clear()
        
        logger.info("Restock Agent components stopped")
    
    async def _run_cycle_logic(self):
        """Run restock agent cycle logic"""
        logger.debug("Running Restock Agent cycle", agent_id=self.agent_id)
        
        try:
            # Check inventory levels
            low_stock_items = await self._check_inventory_levels()
            
            # Generate restock recommendations
            recommendations = []
            if low_stock_items:
                recommendations = await self._generate_restock_recommendations(low_stock_items)
                
                # Execute restock actions
                for recommendation in recommendations:
                    await self._execute_restock_action(recommendation)
            
            # Update restock policies based on performance
            await self._update_restock_policies()
            
            # Store cycle results in memory
            await self._store_memory("cycle", f"cycle_{self.cycle_count}", {
                "timestamp": datetime.utcnow().isoformat(),
                "low_stock_items_count": len(low_stock_items),
                "recommendations_generated": len(recommendations),
                "cycle_duration_ms": self.average_response_time
            })
            
            self.tasks_completed += 1
            
        except Exception as e:
            logger.error("Error in Restock Agent cycle", agent_id=self.agent_id, error=str(e))
            self.tasks_failed += 1
            raise
    
    async def _execute_action(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute restock agent specific actions"""
        
        if action == "check_inventory":
            return await self._check_inventory_levels()
        
        elif action == "generate_restock_plan":
            sku_ids = parameters.get("sku_ids", [])
            location_ids = parameters.get("location_ids", [])
            return await self._generate_restock_plan(sku_ids, location_ids)
        
        elif action == "execute_restock":
            sku_id = parameters.get("sku_id")
            location_id = parameters.get("location_id")
            quantity = parameters.get("quantity")
            return await self._execute_single_restock(sku_id, location_id, quantity)
        
        elif action == "update_thresholds":
            new_thresholds = parameters.get("thresholds", {})
            return await self._update_restock_thresholds(new_thresholds)
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _check_inventory_levels(self) -> List[Dict[str, Any]]:
        """Check for low stock items across all locations"""
        db = next(get_db())
        
        try:
            # Get all inventory items
            inventories = db.query(InventoryItem).filter(
                InventoryItem.current_stock > 0  # Only check items with some stock
            ).all()
            
            low_stock_items = []
            threshold_factor = self.config.get("threshold_factor", 0.2)
            
            for inventory in inventories:
                # Get SKU details
                sku = inventory.sku
                location = inventory.location
                
                # Calculate restock threshold
                min_stock = sku.min_stock_level
                restock_threshold = max(min_stock, inventory.current_stock * threshold_factor)
                
                # Check if stock is below threshold
                if inventory.available_stock <= restock_threshold:
                    low_stock_items.append({
                        "inventory_id": inventory.id,
                        "sku_id": sku.id,
                        "sku_code": sku.sku_code,
                        "sku_name": sku.name,
                        "location_id": location.id,
                        "location_name": location.name,
                        "current_stock": inventory.current_stock,
                        "available_stock": inventory.available_stock,
                        "min_stock_level": min_stock,
                        "restock_threshold": restock_threshold,
                        "shortage": restock_threshold - inventory.available_stock
                    })
            
            logger.info(f"Found {len(low_stock_items)} low stock items", agent_id=self.agent_id)
            return low_stock_items
            
        finally:
            db.close()
    
    async def _generate_restock_recommendations(self, low_stock_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate restock recommendations with AI reasoning"""
        recommendations = []
        
        for item in low_stock_items:
            try:
                # Get demand forecast
                forecast = await self._get_demand_forecast(item["sku_id"], item["location_id"])
                
                # Calculate optimal restock quantity
                restock_quantity = await self._calculate_restock_quantity(item, forecast)
                
                # Generate reasoning
                reasoning = await self._generate_restock_reasoning(item, forecast, restock_quantity)
                
                recommendation = {
                    "inventory_id": item["inventory_id"],
                    "sku_id": item["sku_id"],
                    "location_id": item["location_id"],
                    "current_stock": item["current_stock"],
                    "recommended_quantity": restock_quantity,
                    "forecasted_demand": forecast.get("predicted_demand", 0),
                    "reasoning": reasoning,
                    "priority": self._calculate_priority(item, forecast),
                    "estimated_cost": restock_quantity * item.get("unit_cost", 0)
                }
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.error(f"Failed to generate recommendation for item {item['sku_id']}", error=str(e))
        
        return recommendations
    
    async def _get_demand_forecast(self, sku_id: int, location_id: int) -> Dict[str, Any]:
        """Get demand forecast for restocking decisions"""
        db = next(get_db())
        
        try:
            # Get most recent forecast for the product (using sku_id as product_id)
            forecast = db.query(DemandForecast).filter(
                DemandForecast.product_id == str(sku_id)
            ).order_by(DemandForecast.created_at.desc()).first()
            
            if forecast:
                # Extract data from the forecast_data JSON field
                forecast_data = forecast.forecast_data or {}
                values = forecast_data.get('values', [])
                
                # Get the first forecast value or use default
                if values:
                    first_value = values[0]
                    predicted_demand = first_value.get('demand', 0)
                else:
                    predicted_demand = 0
                
                return {
                    "predicted_demand": predicted_demand,
                    "confidence_lower": predicted_demand * 0.8,  # Estimate
                    "confidence_upper": predicted_demand * 1.2,  # Estimate
                    "reasoning": forecast_data.get('reasoning', 'AI-generated forecast'),
                    "confidence_score": float(forecast.confidence_score) if forecast.confidence_score else 0.7
                }
            else:
                # Fallback to basic demand estimation
                return {
                    "predicted_demand": 10.0,  # Default daily demand
                    "confidence_lower": 5.0,
                    "confidence_upper": 15.0,
                    "reasoning": "No forecast available, using default demand"
                }
                
        finally:
            db.close()
    
    async def _calculate_restock_quantity(self, item: Dict[str, Any], forecast: Dict[str, Any]) -> int:
        """Calculate optimal restock quantity"""
        
        # Base calculation: cover forecasted demand + safety stock
        forecasted_demand = forecast.get("predicted_demand", 10.0)
        safety_stock_factor = 1.5  # 50% safety stock
        lead_time_days = 1  # Assume 1 day lead time
        
        # Calculate required stock
        required_stock = forecasted_demand * lead_time_days * safety_stock_factor
        
        # Calculate restock quantity
        current_stock = item["current_stock"]
        restock_quantity = max(0, int(required_stock - current_stock))
        
        # Apply constraints
        max_stock = item.get("max_stock_level", 1000)
        restock_quantity = min(restock_quantity, max_stock - current_stock)
        
        return restock_quantity
    
    async def _generate_restock_reasoning(self, item: Dict[str, Any], forecast: Dict[str, Any], quantity: int) -> str:
        """Generate AI reasoning for restock decision"""
        
        reasoning = f"""
        Restock Recommendation for {item['sku_name']} at {item['location_name']}:
        
        Current Situation:
        - Current stock: {item['current_stock']} units
        - Available stock: {item['available_stock']} units
        - Minimum stock level: {item['min_stock_level']} units
        - Restock threshold: {item['restock_threshold']} units
        
        Demand Forecast:
        - Predicted demand: {forecast.get('predicted_demand', 0)} units/day
        - Confidence interval: {forecast.get('confidence_lower', 0)} - {forecast.get('confidence_upper', 0)}
        
        Recommendation:
        - Restock quantity: {quantity} units
        - Priority: {self._calculate_priority(item, forecast)}
        
        Reasoning: {forecast.get('reasoning', 'Based on current stock levels and demand patterns')}
        """
        
        return reasoning
    
    def _calculate_priority(self, item: Dict[str, Any], forecast: Dict[str, Any]) -> str:
        """Calculate restock priority"""
        
        shortage_ratio = item["shortage"] / max(1, item["restock_threshold"])
        demand_urgency = forecast.get("predicted_demand", 0) / 10.0  # Normalize to 10 units/day
        
        if shortage_ratio > 0.5 and demand_urgency > 1.0:
            return "high"
        elif shortage_ratio > 0.3 or demand_urgency > 0.8:
            return "medium"
        else:
            return "low"
    
    async def _execute_restock_action(self, recommendation: Dict[str, Any]):
        """Execute a restock action"""
        
        try:
            # Log the restock action
            await self._log_action(
                task_id=str(uuid.uuid4()),
                action="restock_inventory",
                input_data=recommendation,
                status="completed",
                reasoning=recommendation["reasoning"]
            )
            
            # Store restock order in memory
            await self._store_memory("restock_order", f"order_{datetime.utcnow().timestamp()}", {
                "recommendation": recommendation,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "pending"
            })
            
            # Update inventory (simulate restock)
            await self._simulate_restock_delivery(recommendation)
            
            logger.info(
                f"Restock action executed for {recommendation['sku_id']}",
                quantity=recommendation["recommended_quantity"],
                location=recommendation["location_id"]
            )
            
        except Exception as e:
            logger.error(f"Failed to execute restock action", error=str(e))
            raise
    
    async def _simulate_restock_delivery(self, recommendation: Dict[str, Any]):
        """Simulate restock delivery (in real system, this would create purchase orders)"""
        db = next(get_db())
        
        try:
            # Update inventory with restocked quantity
            inventory = db.query(InventoryItem).filter(
                InventoryItem.id == recommendation["inventory_id"]
            ).first()
            
            if inventory:
                inventory.add_stock(recommendation["recommended_quantity"])
                inventory.last_restock_date = datetime.utcnow()
                inventory.next_restock_date = datetime.utcnow() + timedelta(days=1)
                
                db.commit()
                
                logger.info(f"Inventory updated for restock", 
                           inventory_id=inventory.id,
                           added_quantity=recommendation["recommended_quantity"])
            
        except Exception as e:
            logger.error("Failed to simulate restock delivery", error=str(e))
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _load_restock_policies(self):
        """Load restock policies from memory"""
        # In a real system, this would load from configuration
        self.restock_policies = {
            "safety_stock_factor": 1.5,
            "lead_time_days": 1,
            "max_stock_factor": 2.0,
            "priority_thresholds": {
                "high": 0.5,
                "medium": 0.3,
                "low": 0.1
            }
        }
    
    async def _update_restock_policies(self):
        """Update restock policies based on performance"""
        # In a real system, this would analyze performance and adjust policies
        pass
    
    async def _generate_restock_plan(self, sku_ids: List[int], location_ids: List[int]) -> Dict[str, Any]:
        """Generate comprehensive restock plan for specific SKUs and locations"""
        
        plan = {
            "timestamp": datetime.utcnow().isoformat(),
            "sku_ids": sku_ids,
            "location_ids": location_ids,
            "recommendations": [],
            "total_cost": 0,
            "priority_breakdown": {"high": 0, "medium": 0, "low": 0}
        }
        
        for sku_id in sku_ids:
            for location_id in location_ids:
                try:
                    # Check inventory for this SKU-location combination
                    db = next(get_db())
                    inventory = db.query(InventoryItem).filter(
                        InventoryItem.sku_id == sku_id,
                        InventoryItem.location_id == location_id
                    ).first()
                    
                    if inventory:
                        item = {
                            "inventory_id": inventory.id,
                            "sku_id": sku_id,
                            "location_id": location_id,
                            "current_stock": inventory.current_stock,
                            "available_stock": inventory.available_stock
                        }
                        
                        # Generate recommendation
                        forecast = await self._get_demand_forecast(sku_id, location_id)
                        restock_quantity = await self._calculate_restock_quantity(item, forecast)
                        
                        if restock_quantity > 0:
                            recommendation = {
                                "sku_id": sku_id,
                                "location_id": location_id,
                                "recommended_quantity": restock_quantity,
                                "priority": self._calculate_priority(item, forecast)
                            }
                            
                            plan["recommendations"].append(recommendation)
                            plan["priority_breakdown"][recommendation["priority"]] += 1
                    
                    db.close()
                    
                except Exception as e:
                    logger.error(f"Failed to generate plan for SKU {sku_id}, Location {location_id}", error=str(e))
        
        return plan
    
    async def _execute_single_restock(self, sku_id: int, location_id: int, quantity: int) -> Dict[str, Any]:
        """Execute a single restock action"""
        
        try:
            db = next(get_db())
            inventory = db.query(InventoryItem).filter(
                InventoryItem.sku_id == sku_id,
                InventoryItem.location_id == location_id
            ).first()
            
            if not inventory:
                raise ValueError(f"Inventory not found for SKU {sku_id} at location {location_id}")
            
            # Execute restock
            inventory.add_stock(quantity)
            inventory.last_restock_date = datetime.utcnow()
            
            db.commit()
            
            result = {
                "success": True,
                "sku_id": sku_id,
                "location_id": location_id,
                "quantity_added": quantity,
                "new_stock_level": inventory.current_stock,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute single restock", error=str(e))
            db.rollback()
            raise
        finally:
            db.close()
    
    async def _update_restock_thresholds(self, new_thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """Update restock thresholds"""
        
        # Update configuration
        self.config.update(new_thresholds)
        
        # Store updated config in memory
        await self._store_memory("config", "restock_thresholds", new_thresholds)
        
        return {
            "success": True,
            "updated_thresholds": new_thresholds,
            "timestamp": datetime.utcnow().isoformat()
        } 