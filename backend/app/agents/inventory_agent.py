import asyncio
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
# Avoid circular import by importing broadcast_agent_action lazily inside methods
from datetime import datetime

class InventoryAgent(BaseAgent):
    def __init__(self, agent_id: str = "aa0e8400-e29b-41d4-a716-446655440001"):
        super().__init__(agent_id, "inventory_management")
    
    async def process(self) -> bool:
        """Process inventory management decisions"""
        try:
            # Check for low stock items
            await self.check_low_stock()
            
            # Optimize inventory levels
            await self.optimize_inventory()
            
            # Handle inventory optimization (removed expiry handling)
            await self.handle_inventory_optimization()
            
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
                    # Create separate reorder actions for each recommendation
                    for rec in decision.get("reorder_recommendations", []):
                        await self.create_reorder_action(rec)
                else:
                    # If Groq fails, create a simple action
                    await self.create_inventory_check_action()
            else:
                # Create a simple inventory check action even when no low stock items
                await self.create_inventory_check_action()
        
        except Exception as e:
            print(f"Error checking low stock: {e}")
            # Create a fallback action on error
            await self.create_inventory_check_action()
    
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
                    # Create separate actions for each optimization recommendation
                    for rec in decision.get("optimization_recommendations", []):
                        await self.create_optimization_action(rec)
        
        except Exception as e:
            print(f"Error optimizing inventory: {e}")
    
    async def handle_inventory_optimization(self):
        """Handle inventory optimization based on current stock levels"""
        try:
            # Get current inventory levels
            inventory_response = self.supabase.table("inventory").select("*").execute()
            inventory = inventory_response.data if inventory_response.data else []
            
            if inventory:
                prompt = f"""
                Analyze current inventory levels and recommend specific actions:
                {inventory}
                
                Consider:
                - Current stock levels vs demand
                - Storage space utilization
                - Product performance and profitability
                - Seasonal trends and market conditions
                
                Provide specific recommendations for inventory management.
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "inventory_recommendations": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "item_id": {"type": "string"},
                                    "action": {"type": "string", "enum": ["discount", "restock", "discontinue", "maintain"]},
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
                    # Create separate actions for each recommendation
                    for rec in decision.get("inventory_recommendations", []):
                        await self.create_inventory_action(rec)
        
        except Exception as e:
            print(f"Error handling inventory optimization: {e}")
    
    async def create_reorder_action(self, recommendation: Dict[str, Any]):
        """Create a reorder action in the system"""
        try:
            action_data = {
                "agent_id": self.agent_id,
                "action_type": "reorder",
                "payload": {
                    "item_id": recommendation.get("item_id"),
                    "recommended_quantity": recommendation.get("recommended_quantity", 0),
                    "reasoning": recommendation.get("reasoning", ""),
                    "priority": recommendation.get("priority", "medium")
                },
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("agent_actions").insert(action_data).execute()
            # Avoid circular import by importing broadcast_agent_action lazily inside methods
            from app.main import broadcast_agent_action
            broadcast_agent_action(action_data)
            return result
        
        except Exception as e:
            print(f"Error creating reorder action: {e}")

    async def create_inventory_check_action(self):
        """Create a simple inventory check action"""
        try:
            action_data = {
                "agent_id": self.agent_id,
                "action_type": "inventory_check",
                "payload": {
                    "reason": "Routine inventory check completed",
                    "status": "pending"
                },
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("agent_actions").insert(action_data).execute()
            # Avoid circular import by importing broadcast_agent_action lazily inside methods
            from app.main import broadcast_agent_action
            broadcast_agent_action(action_data)
            return result
        
        except Exception as e:
            print(f"Error creating inventory check action: {e}") 
    
    async def create_optimization_action(self, recommendation: Dict[str, Any]):
        """Create an optimization action in the system"""
        try:
            action_data = {
                "agent_id": self.agent_id,
                "action_type": "optimization",
                "payload": {
                    "item_id": recommendation.get("item_id"),
                    "current_level": recommendation.get("current_level", 0),
                    "recommended_level": recommendation.get("recommended_level", 0),
                    "action": recommendation.get("action", "maintain"),
                    "reasoning": recommendation.get("reasoning", ""),
                    "expected_impact": recommendation.get("expected_impact", "")
                },
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }

            result = self.supabase.table("agent_actions").insert(action_data).execute()
            print(f"Created optimization action for {recommendation.get('item_id')}")
            
        except Exception as e:
            print(f"Error creating optimization action: {e}")
    
    async def create_inventory_action(self, recommendation: Dict[str, Any]):
        """Create an inventory action in the system"""
        try:
            action_data = {
                "agent_id": self.agent_id,
                "action_type": "inventory_management",
                "payload": {
                    "item_id": recommendation.get("item_id"),
                    "action": recommendation.get("action", "maintain"),
                    "discount_percentage": recommendation.get("discount_percentage", 0),
                    "reasoning": recommendation.get("reasoning", ""),
                    "urgency": recommendation.get("urgency", "medium")
                },
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }

            result = self.supabase.table("agent_actions").insert(action_data).execute()
            print(f"Created inventory action for {recommendation.get('item_id')}")
            
        except Exception as e:
            print(f"Error creating inventory action: {e}") 