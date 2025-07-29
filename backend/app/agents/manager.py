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
        # Remove is_running, agent_tasks, and all orchestration/loop logic
        # Only keep agent initialization and direct action methods
    
    async def initialize_agents(self):
        """Initialize all agents"""
        try:
            # Create agent instances
            self.agents = {
                "inventory": InventoryAgent(),
                "routing": RoutingAgent(),
                "pricing": PricingAgent()
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
            # Start each agent in its own task
            for agent_id, agent in self.agents.items():
                task = asyncio.create_task(agent.run())
                # self.agent_tasks[agent_id] = task # This line is removed
                print(f"Started agent: {agent_id}")
            
            await self.log_manager_action("agents_started", {
                "running_agents": list(self.agents.keys())
            })
        except Exception as e:
            print(f"Error starting agents: {e}")
    
    async def stop_agents(self):
        """Stop all agents"""
        try:
            # Stop each agent
            for agent_id, agent in self.agents.items():
                agent.is_active = False
                # if agent_id in self.agent_tasks: # This line is removed
                #     self.agent_tasks[agent_id].cancel() # This line is removed
            
            # Wait for all tasks to complete # This line is removed
            # if self.agent_tasks: # This line is removed
            #     await asyncio.gather(*self.agent_tasks.values(), return_exceptions=True) # This line is removed
            
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
                "manager_running": True, # This line is changed
                "agents": status,
                "total_agents": len(self.agents)
            }
            
        except Exception as e:
            print(f"Error getting agent status: {e}")
            return {}
    
    # Remove orchestrate_agents, handle_multi_agent_decisions, requires_coordination, coordinate_decision, coordinate_inventory_routing, coordinate_pricing_inventory, coordinate_routing_pricing
    # Remove monitor_agent_health and restart_agent
    # Remove coordinate_agent_actions and resolve_action_conflicts
    # Remove execute_conflict_resolution
    
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
            
            # Keep the manager running
            while True: # This line is changed
                await asyncio.sleep(1)
            
            # Cleanup # This block is removed
            # orchestration_task.cancel()
            # await self.stop_agents()
            
        except Exception as e:
            print(f"Error in agent manager: {e}")
            await self.log_manager_action("manager_error", {"error": str(e)})

# Global instance
agent_manager = AgentManager() 