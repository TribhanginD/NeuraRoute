import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent
from .inventory_agent import InventoryAgent
from .routing_agent import RoutingAgent
from .pricing_agent import PricingAgent
from ..core.supabase import supabase_client

class AgentManager:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.supabase = supabase_client.get_client()
        self.is_running = False
        self.agent_tasks: Dict[str, asyncio.Task] = {}
    
    async def initialize_agents(self):
        """Initialize all agents"""
        try:
            # Create agent instances
            self.agents = {
                "inventory": InventoryAgent("inventory_agent_001"),
                "routing": RoutingAgent("routing_agent_001"),
                "pricing": PricingAgent("pricing_agent_001")
            }
            
            # Log agent initialization
            await self.log_manager_action("agents_initialized", {
                "agent_count": len(self.agents),
                "agent_types": list(self.agents.keys())
            })
            
            print(f"Initialized {len(self.agents)} agents")
            
        except Exception as e:
            print(f"Error initializing agents: {e}")
    
    async def start_agents(self):
        """Start all agents"""
        try:
            self.is_running = True
            
            # Start each agent in its own task
            for agent_id, agent in self.agents.items():
                task = asyncio.create_task(agent.run())
                self.agent_tasks[agent_id] = task
                print(f"Started agent: {agent_id}")
            
            await self.log_manager_action("agents_started", {
                "running_agents": list(self.agents.keys())
            })
            
        except Exception as e:
            print(f"Error starting agents: {e}")
    
    async def stop_agents(self):
        """Stop all agents"""
        try:
            self.is_running = False
            
            # Stop each agent
            for agent_id, agent in self.agents.items():
                agent.is_active = False
                if agent_id in self.agent_tasks:
                    self.agent_tasks[agent_id].cancel()
            
            # Wait for all tasks to complete
            if self.agent_tasks:
                await asyncio.gather(*self.agent_tasks.values(), return_exceptions=True)
            
            await self.log_manager_action("agents_stopped", {
                "stopped_agents": list(self.agents.keys())
            })
            
            print("All agents stopped")
            
        except Exception as e:
            print(f"Error stopping agents: {e}")
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        try:
            status = {}
            for agent_id, agent in self.agents.items():
                status[agent_id] = {
                    "is_active": agent.is_active,
                    "agent_type": agent.agent_type,
                    "last_action_time": agent.last_action_time
                }
            
            return {
                "manager_running": self.is_running,
                "agents": status,
                "total_agents": len(self.agents)
            }
            
        except Exception as e:
            print(f"Error getting agent status: {e}")
            return {}
    
    async def orchestrate_agents(self):
        """Orchestrate agent interactions and coordination"""
        try:
            while self.is_running:
                # Check for pending decisions that require multi-agent coordination
                await self.handle_multi_agent_decisions()
                
                # Monitor agent performance and health
                await self.monitor_agent_health()
                
                # Coordinate agent actions
                await self.coordinate_agent_actions()
                
                # Wait before next orchestration cycle
                await asyncio.sleep(60)  # 1 minute between orchestration cycles
                
        except Exception as e:
            print(f"Error in agent orchestration: {e}")
    
    async def handle_multi_agent_decisions(self):
        """Handle decisions that require multiple agents to coordinate"""
        try:
            # Get pending decisions that might need coordination
            decisions_response = self.supabase.table("agent_decisions").select("*").eq("status", "pending").execute()
            pending_decisions = decisions_response.data if decisions_response.data else []
            
            for decision in pending_decisions:
                if self.requires_coordination(decision):
                    await self.coordinate_decision(decision)
        
        except Exception as e:
            print(f"Error handling multi-agent decisions: {e}")
    
    def requires_coordination(self, decision: Dict[str, Any]) -> bool:
        """Check if a decision requires multiple agents to coordinate"""
        decision_type = decision.get("decision_type", "")
        return decision_type in ["inventory_routing", "pricing_inventory", "routing_pricing"]
    
    async def coordinate_decision(self, decision: Dict[str, Any]):
        """Coordinate a decision between multiple agents"""
        try:
            decision_type = decision.get("decision_type", "")
            
            if decision_type == "inventory_routing":
                await self.coordinate_inventory_routing(decision)
            elif decision_type == "pricing_inventory":
                await self.coordinate_pricing_inventory(decision)
            elif decision_type == "routing_pricing":
                await self.coordinate_routing_pricing(decision)
        
        except Exception as e:
            print(f"Error coordinating decision: {e}")
    
    async def coordinate_inventory_routing(self, decision: Dict[str, Any]):
        """Coordinate inventory and routing decisions"""
        try:
            # Get inventory and routing agents
            inventory_agent = self.agents.get("inventory")
            routing_agent = self.agents.get("routing")
            
            if inventory_agent and routing_agent:
                # Create a coordinated decision prompt
                prompt = f"""
                Coordinate inventory and routing decisions for:
                {decision}
                
                Consider:
                - Inventory availability for routing
                - Route optimization based on stock levels
                - Delivery timing and inventory replenishment
                - Cost optimization across both domains
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "inventory_actions": {
                            "type": "array",
                            "items": {"type": "object"}
                        },
                        "routing_actions": {
                            "type": "array",
                            "items": {"type": "object"}
                        },
                        "coordination_notes": {"type": "string"}
                    }
                }
                
                # Use the inventory agent to make the decision
                coordinated_decision = await inventory_agent.make_decision(prompt, response_format)
                
                if coordinated_decision:
                    await self.log_manager_action("coordinated_decision", {
                        "decision_id": decision.get("id"),
                        "decision_type": "inventory_routing",
                        "result": coordinated_decision
                    })
        
        except Exception as e:
            print(f"Error coordinating inventory-routing: {e}")
    
    async def coordinate_pricing_inventory(self, decision: Dict[str, Any]):
        """Coordinate pricing and inventory decisions"""
        try:
            pricing_agent = self.agents.get("pricing")
            inventory_agent = self.agents.get("inventory")
            
            if pricing_agent and inventory_agent:
                prompt = f"""
                Coordinate pricing and inventory decisions for:
                {decision}
                
                Consider:
                - Price impact on inventory demand
                - Inventory levels affecting pricing strategy
                - Profit optimization across both domains
                - Customer satisfaction and retention
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "pricing_actions": {
                            "type": "array",
                            "items": {"type": "object"}
                        },
                        "inventory_actions": {
                            "type": "array",
                            "items": {"type": "object"}
                        },
                        "expected_outcome": {"type": "string"}
                    }
                }
                
                coordinated_decision = await pricing_agent.make_decision(prompt, response_format)
                
                if coordinated_decision:
                    await self.log_manager_action("coordinated_decision", {
                        "decision_id": decision.get("id"),
                        "decision_type": "pricing_inventory",
                        "result": coordinated_decision
                    })
        
        except Exception as e:
            print(f"Error coordinating pricing-inventory: {e}")
    
    async def coordinate_routing_pricing(self, decision: Dict[str, Any]):
        """Coordinate routing and pricing decisions"""
        try:
            routing_agent = self.agents.get("routing")
            pricing_agent = self.agents.get("pricing")
            
            if routing_agent and pricing_agent:
                prompt = f"""
                Coordinate routing and pricing decisions for:
                {decision}
                
                Consider:
                - Route optimization affecting delivery costs
                - Pricing strategy for premium delivery services
                - Customer willingness to pay for faster delivery
                - Operational cost vs revenue optimization
                """
                
                response_format = {
                    "type": "object",
                    "properties": {
                        "routing_actions": {
                            "type": "array",
                            "items": {"type": "object"}
                        },
                        "pricing_actions": {
                            "type": "array",
                            "items": {"type": "object"}
                        },
                        "service_tier_recommendations": {
                            "type": "array",
                            "items": {"type": "object"}
                        }
                    }
                }
                
                coordinated_decision = await routing_agent.make_decision(prompt, response_format)
                
                if coordinated_decision:
                    await self.log_manager_action("coordinated_decision", {
                        "decision_id": decision.get("id"),
                        "decision_type": "routing_pricing",
                        "result": coordinated_decision
                    })
        
        except Exception as e:
            print(f"Error coordinating routing-pricing: {e}")
    
    async def monitor_agent_health(self):
        """Monitor agent health and performance"""
        try:
            for agent_id, agent in self.agents.items():
                # Check if agent is still active
                if not agent.is_active:
                    print(f"Agent {agent_id} is not active, attempting restart...")
                    await self.restart_agent(agent_id)
                
                # Log agent health status
                await self.log_manager_action("agent_health_check", {
                    "agent_id": agent_id,
                    "is_active": agent.is_active,
                    "last_action_time": agent.last_action_time
                })
        
        except Exception as e:
            print(f"Error monitoring agent health: {e}")
    
    async def restart_agent(self, agent_id: str):
        """Restart a specific agent"""
        try:
            if agent_id in self.agents:
                # Stop the current agent
                self.agents[agent_id].is_active = False
                if agent_id in self.agent_tasks:
                    self.agent_tasks[agent_id].cancel()
                
                # Create a new instance
                if agent_id == "inventory":
                    self.agents[agent_id] = InventoryAgent("inventory_agent_001")
                elif agent_id == "routing":
                    self.agents[agent_id] = RoutingAgent("routing_agent_001")
                elif agent_id == "pricing":
                    self.agents[agent_id] = PricingAgent("pricing_agent_001")
                
                # Start the new agent
                task = asyncio.create_task(self.agents[agent_id].run())
                self.agent_tasks[agent_id] = task
                
                await self.log_manager_action("agent_restarted", {"agent_id": agent_id})
                print(f"Restarted agent: {agent_id}")
        
        except Exception as e:
            print(f"Error restarting agent {agent_id}: {e}")
    
    async def coordinate_agent_actions(self):
        """Coordinate actions between agents to avoid conflicts"""
        try:
            # Get pending actions from all agents
            actions_response = self.supabase.table("agent_actions").select("*").eq("status", "pending").execute()
            pending_actions = actions_response.data if actions_response.data else []
            
            # Group actions by target table to check for conflicts
            actions_by_table = {}
            for action in pending_actions:
                table = action.get("target_table", "")
                if table not in actions_by_table:
                    actions_by_table[table] = []
                actions_by_table[table].append(action)
            
            # Check for conflicts and resolve them
            for table, actions in actions_by_table.items():
                if len(actions) > 1:
                    await self.resolve_action_conflicts(table, actions)
        
        except Exception as e:
            print(f"Error coordinating agent actions: {e}")
    
    async def resolve_action_conflicts(self, table: str, actions: List[Dict[str, Any]]):
        """Resolve conflicts between actions on the same table"""
        try:
            # Create a conflict resolution prompt
            prompt = f"""
            Resolve conflicts between the following actions on table '{table}':
            {actions}
            
            Consider:
            - Action priorities and urgency
            - Business impact and customer satisfaction
            - Resource availability and constraints
            - Logical consistency and data integrity
            
            Provide a resolution that maintains system consistency.
            """
            
            response_format = {
                "type": "object",
                "properties": {
                    "resolved_actions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "action_id": {"type": "string"},
                                "status": {"type": "string", "enum": ["approved", "rejected", "modified"]},
                                "modifications": {"type": "object"},
                                "reasoning": {"type": "string"}
                            }
                        }
                    }
                }
            }
            
            # Use the first agent to make the decision
            first_agent = list(self.agents.values())[0]
            resolution = await first_agent.make_decision(prompt, response_format)
            
            if resolution:
                await self.execute_conflict_resolution(resolution.get("resolved_actions", []))
        
        except Exception as e:
            print(f"Error resolving action conflicts: {e}")
    
    async def execute_conflict_resolution(self, resolved_actions: List[Dict[str, Any]]):
        """Execute the conflict resolution"""
        try:
            for action in resolved_actions:
                action_id = action.get("action_id")
                status = action.get("status")
                
                if status == "approved":
                    # Approve the action
                    self.supabase.table("agent_actions").update({"status": "approved"}).eq("id", action_id).execute()
                elif status == "rejected":
                    # Reject the action
                    self.supabase.table("agent_actions").update({"status": "rejected"}).eq("id", action_id).execute()
                elif status == "modified":
                    # Apply modifications
                    modifications = action.get("modifications", {})
                    self.supabase.table("agent_actions").update(modifications).eq("id", action_id).execute()
                
                await self.log_manager_action("conflict_resolved", action)
        
        except Exception as e:
            print(f"Error executing conflict resolution: {e}")
    
    async def log_manager_action(self, action: str, details: Dict[str, Any]):
        """Log manager actions"""
        try:
            log_data = {
                "agent_id": "agent_manager",
                "agent_type": "manager",
                "action": action,
                "details": json.dumps(details),
                "status": "completed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("agent_logs").insert(log_data).execute()
            return result
        except Exception as e:
            print(f"Error logging manager action: {e}")
    
    async def run(self):
        """Main manager loop"""
        try:
            await self.initialize_agents()
            await self.start_agents()
            
            # Start orchestration
            orchestration_task = asyncio.create_task(self.orchestrate_agents())
            
            # Keep the manager running
            while self.is_running:
                await asyncio.sleep(1)
            
            # Cleanup
            orchestration_task.cancel()
            await self.stop_agents()
            
        except Exception as e:
            print(f"Error in agent manager: {e}")
            await self.log_manager_action("manager_error", {"error": str(e)})

# Global instance
agent_manager = AgentManager() 