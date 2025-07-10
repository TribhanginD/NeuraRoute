import asyncio
from typing import Dict, Any, Optional
from .base_agent import BaseAgent

class InventoryAgent(BaseAgent):
    def __init__(self, agent_id: str = "inventory_agent_001"):
        super().__init__(agent_id, "inventory_management")
    
    async def process(self) -> bool:
        """Process inventory management decisions"""
        try:
            # Check for low stock items
            await self.check_low_stock()
            
            # Optimize inventory levels
            await self.optimize_inventory()
            
            # Handle expired items
            await self.handle_expired_items()
            
            return True
        except Exception as e:
            print(f"Error in inventory agent process: {e}")
            return False
    
    async def check_low_stock(self):
        """Check for items with low stock and make reorder decisions"""
        try:
            # Get current inventory levels
            inventory_response = self.supabase.table("inventory").select("*").execute()
            inventory = inventory_response.data if inventory_response.data else []
            
            low_stock_items = [item for item in inventory if item.get("quantity", 0) < item.get("min_threshold", 10)]
            
            if low_stock_items:
                prompt = f"""
                Analyze the following low stock items and determine reorder quantities:
                {low_stock_items}
                
                Consider:
                - Current demand patterns
                - Lead times for suppliers
                - Storage capacity
                - Cost optimization
                
                Provide reorder recommendations for each item.
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "reorder_recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {"type": "string"},
                                    "item_name": {"type": "string"},
                                    "current_quantity": {"type": "integer"},
                                    "recommended_quantity": {"type": "integer"},
                                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                                    "reasoning": {"type": "string"}
                                }
                            }
                        }
                    }
                }
                
                decision = await self.make_decision(prompt, response_format)
                
                if decision:
                    # Create reorder actions
                    for rec in decision.get("reorder_recommendations", []):
                        await self.create_reorder_action(rec)
        
        except Exception as e:
            print(f"Error checking low stock: {e}")
    
    async def optimize_inventory(self):
        """Optimize inventory levels based on demand patterns"""
        try:
            # Get recent order history
            orders_response = self.supabase.table("orders").select("*").order("created_at", desc=True).limit(50).execute()
            recent_orders = orders_response.data if orders_response.data else []
            
            if recent_orders:
                prompt = f"""
                Analyze the recent order history and optimize inventory levels:
                {recent_orders}
                
                Consider:
                - Demand patterns and seasonality
                - Storage costs vs stockout costs
                - Supplier reliability and lead times
                - Product lifecycle and obsolescence risk
                
                Provide inventory optimization recommendations.
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "optimization_recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {"type": "string"},
                                    "current_level": {"type": "integer"},
                                    "recommended_level": {"type": "integer"},
                                    "action": {"type": "string", "enum": ["increase", "decrease", "maintain"]},
                                    "reasoning": {"type": "string"},
                                    "expected_impact": {"type": "string"}
                                }
                            }
                        }
                    }
                }
                
                decision = await self.make_decision(prompt, response_format)
                
                if decision:
                    await self.log_action("inventory_optimization", decision)
        
        except Exception as e:
            print(f"Error optimizing inventory: {e}")
    
    async def handle_expired_items(self):
        """Handle expired or near-expiry items"""
        try:
            # Get items near expiry
            inventory_response = self.supabase.table("inventory").select("*").execute()
            inventory = inventory_response.data if inventory_response.data else []
            
            # Simulate expiry check (in real system, would check actual expiry dates)
            near_expiry_items = [item for item in inventory if item.get("quantity", 0) > 0]
            
            if near_expiry_items:
                prompt = f"""
                Analyze items that may be approaching expiry and recommend actions:
                {near_expiry_items}
                
                Consider:
                - Discount strategies to move inventory
                - Alternative uses for the items
                - Disposal costs vs discount revenue
                - Impact on customer satisfaction
                
                Provide recommendations for handling near-expiry items.
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "expiry_recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {"type": "string"},
                                    "action": {"type": "string", "enum": ["discount", "dispose", "donate", "maintain"]},
                                    "discount_percentage": {"type": "integer"},
                                    "reasoning": {"type": "string"},
                                    "urgency": {"type": "string", "enum": ["high", "medium", "low"]}
                                }
                            }
                        }
                    }
                }
                
                decision = await self.make_decision(prompt, response_format)
                
                if decision:
                    await self.log_action("expiry_handling", decision)
        
        except Exception as e:
            print(f"Error handling expired items: {e}")
    
    async def create_reorder_action(self, recommendation: Dict[str, Any]):
        """Create a reorder action in the system"""
        try:
            action_data = {
                "agent_id": self.agent_id,
                "action_type": "reorder",
                "target_table": "inventory",
                "item_id": recommendation.get("item_id"),
                "quantity": recommendation.get("recommended_quantity", 0),
                "priority": recommendation.get("priority", "medium"),
                "reasoning": recommendation.get("reasoning", ""),
                "status": "pending",
                "created_at": asyncio.get_event_loop().time()
            }
            
            result = self.supabase.table("agent_actions").insert(action_data).execute()
            return result
        
        except Exception as e:
            print(f"Error creating reorder action: {e}") 