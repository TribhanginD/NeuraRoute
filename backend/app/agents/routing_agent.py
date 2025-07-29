import asyncio
from typing import Dict, Any, Optional, List
from .base_agent import BaseAgent
# Avoid circular import by importing broadcast_agent_action lazily inside methods

class RoutingAgent(BaseAgent):
    def __init__(self, agent_id: str = "bb0e8400-e29b-41d4-a716-446655440001"):
        super().__init__(agent_id, "route_optimization")
    
    async def process(self) -> bool:
        """Process routing and delivery optimization decisions"""
        try:
            # Optimize delivery routes
            await self.optimize_routes()
            
            # Assign vehicles to orders
            await self.assign_vehicles()
            
            # Handle dynamic routing updates
            await self.handle_dynamic_routing()
            
            return True
        except Exception as e:
            print(f"Error in routing agent process: {e}")
            return False
    
    async def optimize_routes(self):
        """Optimize delivery routes for current orders"""
        try:
            # Get pending orders
            orders_response = self.supabase.table("orders").select("*").eq("status", "pending").execute()
            pending_orders = orders_response.data if orders_response.data else []
            
            # Get available fleet
            fleet_response = self.supabase.table("fleet").select("*").eq("status", "available").execute()
            available_fleet = fleet_response.data if fleet_response.data else []
            
            if pending_orders and available_fleet:
                prompt = f"""
                Optimize delivery routes for the following orders and available fleet:
                
                Pending Orders:
                {pending_orders}
                
                Available Fleet:
                {available_fleet}
                
                Consider:
                - Order priorities and delivery windows
                - Vehicle capacity and capabilities
                - Traffic conditions and distance optimization
                - Fuel efficiency and cost
                - Customer satisfaction and delivery time
                
                Create optimal route assignments.
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "route_assignments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "vehicle_id": {"type": "string"},
                                    "vehicle_type": {"type": "string"},
                                    "assigned_orders": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "route_sequence": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "estimated_duration": {"type": "integer"},
                                    "estimated_distance": {"type": "number"},
                                    "optimization_score": {"type": "number"},
                                    "reasoning": {"type": "string"}
                                }
                            }
                        }
                    }
                }
                
                decision = await self.make_decision(prompt, response_format)
                
                if decision:
                    await self.create_route_assignments(decision.get("route_assignments", []))
        
        except Exception as e:
            print(f"Error optimizing routes: {e}")
    
    async def assign_vehicles(self):
        """Assign vehicles to orders based on capacity and requirements"""
        try:
            # Get unassigned orders
            orders_response = self.supabase.table("orders").select("*").eq("status", "pending").is_("vehicle_id", "null").execute()
            unassigned_orders = orders_response.data if orders_response.data else []
            
            # Get available vehicles
            fleet_response = self.supabase.table("fleet").select("*").eq("status", "available").execute()
            available_vehicles = fleet_response.data if fleet_response.data else []
            
            if unassigned_orders and available_vehicles:
                prompt = f"""
                Assign vehicles to the following unassigned orders:
                
                Unassigned Orders:
                {unassigned_orders}
                
                Available Vehicles:
                {available_vehicles}
                
                Consider:
                - Order size and vehicle capacity
                - Special requirements (refrigeration, fragile items)
                - Vehicle location and pickup efficiency
                - Driver availability and skills
                - Cost optimization
                
                Provide vehicle assignments for each order.
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "vehicle_assignments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "order_id": {"type": "string"},
                                    "vehicle_id": {"type": "string"},
                                    "assignment_reason": {"type": "string"},
                                    "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                                    "estimated_pickup_time": {"type": "string"},
                                    "estimated_delivery_time": {"type": "string"}
                                }
                            }
                        }
                    }
                }
                
                decision = await self.make_decision(prompt, response_format)
                
                if decision:
                    await self.execute_vehicle_assignments(decision.get("vehicle_assignments", []))
        
        except Exception as e:
            print(f"Error assigning vehicles: {e}")
    
    async def handle_dynamic_routing(self):
        """Handle dynamic routing updates for in-progress deliveries"""
        try:
            # Get in-progress deliveries
            orders_response = self.supabase.table("orders").select("*").eq("status", "in_transit").execute()
            in_transit_orders = orders_response.data if orders_response.data else []
            
            if in_transit_orders:
                prompt = f"""
                Analyze in-progress deliveries for potential route optimizations:
                
                In-Transit Orders:
                {in_transit_orders}
                
                Consider:
                - Traffic conditions and delays
                - Customer requests for time changes
                - New high-priority orders
                - Vehicle breakdowns or issues
                - Weather conditions
                
                Provide dynamic routing recommendations.
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "dynamic_updates": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "order_id": {"type": "string"},
                                    "current_status": {"type": "string"},
                                    "recommended_action": {"type": "string", "enum": ["reroute", "delay", "expedite", "maintain"]},
                                    "new_route": {"type": "array", "items": {"type": "string"}},
                                    "reasoning": {"type": "string"},
                                    "urgency": {"type": "string", "enum": ["high", "medium", "low"]}
                                }
                            }
                        }
                    }
                }
                
                decision = await self.make_decision(prompt, response_format)
                
                if decision:
                    await self.execute_dynamic_updates(decision.get("dynamic_updates", []))
        
        except Exception as e:
            print(f"Error handling dynamic routing: {e}")
    
    async def create_route_assignments(self, assignments: List[Dict[str, Any]]):
        """Create route assignments in the system"""
        try:
            for assignment in assignments:
                assignment_data = {
                    "agent_id": self.agent_id,
                    "action_type": "route_assignment",
                    "vehicle_id": assignment.get("vehicle_id"),
                    "route_data": assignment,
                    "status": "pending",
                    "created_at": asyncio.get_event_loop().time()
                }
                
                result = self.supabase.table("agent_actions").insert(assignment_data).execute()
                # Avoid circular import by importing broadcast_agent_action lazily inside methods
                from app.main import broadcast_agent_action
                broadcast_agent_action(assignment_data)
                
                # Update vehicle status
                self.supabase.table("fleet").update({"status": "assigned"}).eq("id", assignment.get("vehicle_id")).execute()
        
        except Exception as e:
            print(f"Error creating route assignments: {e}")
    
    async def execute_vehicle_assignments(self, assignments: List[Dict[str, Any]]):
        """Execute vehicle assignments"""
        try:
            for assignment in assignments:
                # Update order with vehicle assignment
                update_data = {
                    "vehicle_id": assignment.get("vehicle_id"),
                    "status": "assigned",
                    "estimated_pickup_time": assignment.get("estimated_pickup_time"),
                    "estimated_delivery_time": assignment.get("estimated_delivery_time")
                }
                
                self.supabase.table("orders").update(update_data).eq("id", assignment.get("order_id")).execute()
                
                # Update vehicle status
                self.supabase.table("fleet").update({"status": "assigned"}).eq("id", assignment.get("vehicle_id")).execute()
                
                await self.log_action("vehicle_assigned", assignment)
        
        except Exception as e:
            print(f"Error executing vehicle assignments: {e}")
    
    async def execute_dynamic_updates(self, updates: List[Dict[str, Any]]):
        """Execute dynamic routing updates"""
        try:
            for update in updates:
                if update.get("recommended_action") == "reroute":
                    # Update order with new route
                    self.supabase.table("orders").update({
                        "route": update.get("new_route"),
                        "status": "rerouted"
                    }).eq("id", update.get("order_id")).execute()
                
                await self.log_action("dynamic_routing_update", update)
        
        except Exception as e:
            print(f"Error executing dynamic updates: {e}") 