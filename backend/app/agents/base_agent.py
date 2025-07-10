import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..ai.groq_client import groq_client
from ..core.supabase import supabase_client

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.supabase = supabase_client.get_client()
        self.last_action_time = None
        self.is_active = True
    
    async def log_action(self, action: str, details: Dict[str, Any], status: str = "completed"):
        """Log agent action to Supabase"""
        try:
            log_data = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "action": action,
                "details": json.dumps(details),
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("agent_logs").insert(log_data).execute()
            return result
        except Exception as e:
            print(f"Error logging action: {e}")
    
    async def get_context(self) -> Dict[str, Any]:
        """Get current system context for decision making"""
        try:
            # Get current inventory
            inventory_response = self.supabase.table("inventory").select("*").execute()
            inventory = inventory_response.data if inventory_response.data else []
            
            # Get current fleet status
            fleet_response = self.supabase.table("fleet").select("*").execute()
            fleet = fleet_response.data if fleet_response.data else []
            
            # Get pending decisions
            decisions_response = self.supabase.table("agent_decisions").select("*").eq("status", "pending").execute()
            pending_decisions = decisions_response.data if decisions_response.data else []
            
            # Get recent orders
            orders_response = self.supabase.table("orders").select("*").order("created_at", desc=True).limit(10).execute()
            recent_orders = orders_response.data if orders_response.data else []
            
            return {
                "inventory": inventory,
                "fleet": fleet,
                "pending_decisions": pending_decisions,
                "recent_orders": recent_orders,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error getting context: {e}")
            return {}
    
    async def make_decision(self, prompt: str, response_format: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a decision using Groq LLM"""
        try:
            context = await self.get_context()
            
            # Add context to prompt
            enhanced_prompt = f"""
            Current System Context:
            {json.dumps(context, indent=2)}
            
            Decision Request:
            {prompt}
            
            Please analyze the context and provide a decision in the specified format.
            """
            
            decision = await groq_client.get_structured_response(
                enhanced_prompt, 
                response_format,
                temperature=0.3
            )
            
            if decision:
                await self.log_action("decision_made", {
                    "prompt": prompt,
                    "decision": decision,
                    "response_format": response_format
                })
            
            return decision
        except Exception as e:
            print(f"Error making decision: {e}")
            await self.log_action("decision_error", {"error": str(e)}, "error")
            return None
    
    @abstractmethod
    async def process(self) -> bool:
        """Main processing method - must be implemented by subclasses"""
        pass
    
    async def run(self):
        """Main agent loop"""
        while self.is_active:
            try:
                success = await self.process()
                if success:
                    await self.log_action("process_success", {"agent_type": self.agent_type})
                else:
                    await self.log_action("process_failed", {"agent_type": self.agent_type}, "error")
                
                # Wait before next iteration
                await asyncio.sleep(30)  # 30 seconds between runs
                
            except Exception as e:
                print(f"Error in agent {self.agent_id}: {e}")
                await self.log_action("run_error", {"error": str(e)}, "error")
                await asyncio.sleep(60)  # Wait longer on error 