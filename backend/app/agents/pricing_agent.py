import asyncio
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
# Avoid circular import by importing broadcast_agent_action lazily inside methods

class PricingAgent(BaseAgent):
    def __init__(self, agent_id: str = "cc0e8400-e29b-41d4-a716-446655440001"):
        super().__init__(agent_id, "pricing_optimization")
    
    async def process(self) -> bool:
        """Process pricing optimization decisions"""
        try:
            # Analyze market conditions and adjust pricing
            await self.analyze_market_conditions()
            
            # Optimize pricing for inventory items
            await self.optimize_inventory_pricing()
            
            # Handle dynamic pricing for high-demand items
            await self.handle_dynamic_pricing()
            
            return True
        except Exception as e:
            print(f"Error in pricing agent process: {e}")
            return False
    
    async def analyze_market_conditions(self):
        """Analyze market conditions and adjust pricing strategy"""
        try:
            # Get recent sales data
            orders_response = self.supabase.table("orders").select("*").order("created_at", desc=True).limit(100).execute()
            recent_orders = orders_response.data if orders_response.data else []
            
            # Get current inventory
            inventory_response = self.supabase.table("inventory").select("*").execute()
            inventory = inventory_response.data if inventory_response.data else []
            
            if recent_orders and inventory:
                prompt = f"""
                Analyze market conditions and pricing strategy based on:
                
                Recent Sales Data:
                {recent_orders}
                
                Current Inventory:
                {inventory}
                
                Consider:
                - Demand patterns and seasonality
                - Competition pricing
                - Cost of goods and margins
                - Inventory turnover rates
                - Customer price sensitivity
                - Market trends and external factors
                
                Provide pricing strategy recommendations.
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "pricing_strategy": {
                            "type": "object",
                            "properties": {
                                "overall_strategy": {"type": "string", "enum": ["premium", "competitive", "discount", "maintain"]},
                                "market_conditions": {"type": "string"},
                                "recommended_actions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "action_type": {"type": "string", "enum": ["price_increase", "price_decrease", "promotion", "maintain"]},
                                            "target_items": {"type": "array", "items": {"type": "string"}},
                                            "reasoning": {"type": "string"},
                                            "expected_impact": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                
                decision = await self.make_decision(prompt, response_format)
                
                if decision:
                    await self.log_action("market_analysis", decision)
            
        except Exception as e:
            print(f"Error analyzing market conditions: {e}")
    
    async def optimize_inventory_pricing(self):
        """Optimize pricing for inventory items based on demand and supply"""
        try:
            # Get inventory with pricing data
            inventory_response = self.supabase.table("inventory").select("*").execute()
            inventory = inventory_response.data if inventory_response.data else []
            
            # Get recent order history for demand analysis
            orders_response = self.supabase.table("orders").select("*").order("created_at", desc=True).limit(200).execute()
            recent_orders = orders_response.data if orders_response.data else []
            
            if inventory and recent_orders:
                prompt = f"""
                Optimize pricing for inventory items based on demand and supply:
                
                Current Inventory:
                {inventory}
                
                Recent Order History:
                {recent_orders}
                
                Consider:
                - Current stock levels vs demand
                - Profit margins and cost structure
                - Seasonal demand patterns
                - Inventory age and obsolescence risk
                - Competitive positioning
                - Customer price elasticity
                
                Provide specific pricing recommendations for each item.
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "pricing_recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {"type": "string"},
                                    "current_price": {"type": "number"},
                                    "recommended_price": {"type": "number"},
                                    "price_change_percentage": {"type": "number"},
                                    "reasoning": {"type": "string"},
                                    "urgency": {"type": "string", "enum": ["high", "medium", "low"]},
                                    "expected_impact": {"type": "string"}
                                }
                            }
                        }
                    }
                }
                
                decision = await self.make_decision(prompt, response_format)
                
                if decision:
                    await self.execute_pricing_updates(decision.get("pricing_recommendations", []))
        
        except Exception as e:
            print(f"Error optimizing inventory pricing: {e}")
    
    async def handle_dynamic_pricing(self):
        """Handle dynamic pricing for high-demand or low-supply items"""
        try:
            # Get items with high demand or low supply
            inventory_response = self.supabase.table("inventory").select("*").execute()
            inventory = inventory_response.data if inventory_response.data else []
            
            # Identify items needing dynamic pricing
            high_demand_items = [item for item in inventory if item.get("quantity", 0) < item.get("min_threshold", 10)]
            low_supply_items = [item for item in inventory if item.get("quantity", 0) < 5]
            
            dynamic_pricing_items = high_demand_items + low_supply_items
            
            if dynamic_pricing_items:
                prompt = f"""
                Analyze items requiring dynamic pricing adjustments:
                
                Items Needing Dynamic Pricing:
                {dynamic_pricing_items}
                
                Consider:
                - Current supply vs demand imbalance
                - Customer willingness to pay
                - Competitive pricing in market
                - Inventory turnover urgency
                - Profit optimization vs customer satisfaction
                - Long-term customer relationship impact
                
                Provide dynamic pricing recommendations.
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "dynamic_pricing_recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {"type": "string"},
                                    "current_price": {"type": "number"},
                                    "new_price": {"type": "number"},
                                    "pricing_strategy": {"type": "string", "enum": ["surge_pricing", "discount", "maintain", "limited_time"]},
                                    "duration": {"type": "string"},
                                    "reasoning": {"type": "string"},
                                    "risk_assessment": {"type": "string"}
                                }
                            }
                        }
                    }
                }
                
                decision = await self.make_decision(prompt, response_format)
                
                if decision:
                    await self.execute_dynamic_pricing_updates(decision.get("dynamic_pricing_recommendations", []))
        
        except Exception as e:
            print(f"Error handling dynamic pricing: {e}")
    
    async def execute_pricing_updates(self, recommendations: List[Dict[str, Any]]):
        """Execute pricing updates based on recommendations"""
        try:
            for rec in recommendations:
                # Update inventory pricing
                update_data = {
                    "price": rec.get("new_price"),
                    "last_price_update": asyncio.get_event_loop().time(),
                    "price_change_reason": rec.get("reasoning")
                }
                
                self.supabase.table("inventory").update(update_data).eq("id", rec.get("item_id")).execute()
                
                # Log the pricing action
                await self.log_action("pricing_update", {
                    "item_id": rec.get("item_id"),
                    "old_price": rec.get("current_price"),
                    "new_price": rec.get("new_price"),
                    "change_percentage": rec.get("price_change_percentage"),
                    "reasoning": rec.get("reasoning")
                })
        
        except Exception as e:
            print(f"Error executing pricing updates: {e}")
    
    async def execute_dynamic_pricing_updates(self, recommendations: List[Dict[str, Any]]):
        """Execute dynamic pricing updates"""
        try:
            for rec in recommendations:
                # Create dynamic pricing action
                action_data = {
                    "agent_id": self.agent_id,
                    "action_type": "dynamic_pricing",
                    "target_table": "inventory",
                    "item_id": rec.get("item_id"),
                    "new_price": rec.get("new_price"),
                    "strategy": rec.get("pricing_strategy"),
                    "duration": rec.get("duration"),
                    "reasoning": rec.get("reasoning"),
                    "status": "pending",
                    "created_at": asyncio.get_event_loop().time()
                }
                
                result = self.supabase.table("agent_actions").insert(action_data).execute()
                from app.main import broadcast_agent_action  # lazy import
                broadcast_agent_action(action_data)
                
                await self.log_action("dynamic_pricing_action", rec)
        
        except Exception as e:
            print(f"Error executing dynamic pricing updates: {e}") 