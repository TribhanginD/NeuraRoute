import json
from abc import ABC
from typing import Dict, Any, Optional
from datetime import datetime
from ..ai.groq_client import groq_client

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        from ..core.supabase import supabase_client
        self.supabase = supabase_client.get_client()
        self.is_active = True
    
    async def log_action(self, action: str, details: Dict[str, Any], status: str = "completed"):
        """Log agent action to Supabase"""
        try:
            log_data = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "action": action,
                "payload": json.dumps(details),  # Use payload instead of details
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result = self.supabase.table("agent_logs").insert(log_data).execute()
            return result
        except Exception as e:
            print(f"Error logging action: {e}")
    
    async def get_context(self) -> Dict[str, Any]:
        """Get current system context for decision making, with limited context size."""
        try:
            # Get actual counts from the database
            inventory_response = self.supabase.table("inventory").select("id", count="exact").execute()
            inventory_count = inventory_response.count if hasattr(inventory_response, 'count') else len(inventory_response.data or [])

            fleet_response = self.supabase.table("fleet").select("id", count="exact").execute()
            fleet_count = fleet_response.count if hasattr(fleet_response, 'count') else len(fleet_response.data or [])

            orders_response = self.supabase.table("orders").select("id", count="exact").execute()
            orders_count = orders_response.count if hasattr(orders_response, 'count') else len(orders_response.data or [])

            # Get a sample of recent data for context (limited to avoid Groq limits)
            recent_inventory = self.supabase.table("inventory").select("id, name, quantity, location").limit(3).execute()
            recent_fleet = self.supabase.table("fleet").select("id, vehicle_type, status").limit(2).execute()
            recent_orders = self.supabase.table("orders").select("id, status, total_amount").order("created_at", desc=True).limit(2).execute()

            return {
                "inventory_summary": f"{inventory_count} total items",
                "fleet_summary": f"{fleet_count} total vehicles",
                "orders_summary": f"{orders_count} total orders",
                "recent_inventory": recent_inventory.data or [],
                "recent_fleet": recent_fleet.data or [],
                "recent_orders": recent_orders.data or [],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"Error getting context: {e}")
            return {}
    
    async def check_for_duplicate_decision(self, payload: Dict[str, Any], time_window_hours: int = 24) -> bool:
        """Check if a similar decision was recently made for the same item"""
        try:
            item_id = payload.get("item_id")
            action = payload.get("action")
            
            if not item_id or not action:
                return False
            
            # Check for recent similar actions within the specified time window
            from datetime import datetime, timedelta
            cutoff_time = (datetime.utcnow() - timedelta(hours=time_window_hours)).isoformat()
            
            # Query for recent actions with same item_id and action using proper JSONB syntax
            # Use contains operator for JSONB fields
            result = self.supabase.table("agent_actions").select("*").gte("created_at", cutoff_time).execute()
            
            # Filter results manually since Supabase JSONB queries can be tricky
            duplicate_found = False
            for action_record in result.data or []:
                action_payload = action_record.get("payload", {})
                if isinstance(action_payload, dict):
                    if action_payload.get("item_id") == item_id and action_payload.get("action") == action:
                        print(f"⚠️ [DUPLICATE DETECTED] Similar action for {item_id} ({action}) already exists within {time_window_hours}h")
                        duplicate_found = True
                        break
            
            if duplicate_found:
                return True
            
            # Additional check: Look for similar reasoning patterns
            reasoning = payload.get("reasoning", "")
            if reasoning:
                # Check for actions with similar reasoning (basic similarity check)
                for action_record in result.data or []:
                    action_payload = action_record.get("payload", {})
                    if isinstance(action_payload, dict) and action_payload.get("item_id") == item_id:
                        recent_reasoning = action_payload.get("reasoning", "")
                        if recent_reasoning and self._similar_reasoning(reasoning, recent_reasoning):
                            print(f"⚠️ [DUPLICATE DETECTED] Similar reasoning for {item_id} already exists")
                            return True
            
            return False
            
        except Exception as e:
            print(f"Error checking for duplicates: {e}")
            return False
    
    def _similar_reasoning(self, reasoning1: str, reasoning2: str, similarity_threshold: float = 0.7) -> bool:
        """Check if two reasoning strings are similar (basic implementation)"""
        try:
            # Convert to lowercase and split into words
            words1 = set(reasoning1.lower().split())
            words2 = set(reasoning2.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return False
            
            similarity = intersection / union
            return similarity > similarity_threshold
            
        except Exception as e:
            print(f"Error calculating reasoning similarity: {e}")
            return False
    
    async def make_decision(self, prompt: str, response_format: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a decision using Groq LLM and log to agent_actions."""
        try:
            print(f"\n🤖 [AGENT DECISION] {self.agent_id} ({self.agent_type})")
            print(f"📋 Prompt: {prompt[:200]}{'...' if len(prompt) > 200 else ''}")
            
            context = await self.get_context()
            # Add context to prompt
            enhanced_prompt = f"""
            Current System Context:
            {json.dumps(context, indent=2)}
            Decision Request:
            {prompt}
            Please analyze the context and provide a decision in the specified format.
            """
            
            print(f"📋 Enhanced Prompt: {enhanced_prompt[:300]}{'...' if len(enhanced_prompt) > 300 else ''}")
            print(f"📋 Response Format: {json.dumps(response_format, indent=2)}")
            
            decision = await groq_client.get_structured_response(
                enhanced_prompt, 
                response_format,
                temperature=0.3
            )
            
            if decision:
                print(f"✅ [AGENT DECISION SUCCESS] {self.agent_id}")
                print(f"📊 Decision: {json.dumps(decision, indent=2)}")
                
                # Check for duplicates before creating actions
                if isinstance(decision, dict):
                    # For single decisions
                    if await self.check_for_duplicate_decision(decision):
                        print(f"⏭️ [SKIPPING DUPLICATE] Decision for {decision.get('item_id')} already exists")
                        return decision
                elif isinstance(decision, list):
                    # For multiple decisions, check each one
                    filtered_decisions = []
                    for single_decision in decision:
                        if not await self.check_for_duplicate_decision(single_decision):
                            filtered_decisions.append(single_decision)
                        else:
                            print(f"⏭️ [SKIPPING DUPLICATE] Decision for {single_decision.get('item_id')} already exists")
                    
                    if not filtered_decisions:
                        print(f"⏭️ [ALL DECISIONS DUPLICATE] No new decisions to create")
                        return decision
                    
                    decision = filtered_decisions
                
                await self.log_action("decision_made", {
                    "prompt": prompt,
                    "decision": decision,
                    "response_format": response_format
                })
                # Insert a generic agent action for every decision (unless subclass does more specific insert)
                action_data = {
                    "agent_id": self.agent_id,
                    "action_type": "decision",
                    "payload": decision,  # Use the actual decision dict for jsonb
                    "status": "pending",
                    "created_at": datetime.utcnow().isoformat()
                }
                try:
                    self.supabase.table("agent_actions").insert(action_data).execute()
                    print(f"✅ [AGENT ACTION CREATED] {self.agent_id} - Action ID: {action_data.get('id', 'N/A')}")
                except Exception as e:
                    print(f"❌ [AGENT ACTION ERROR] {self.agent_id} - Error: {e}")
            else:
                print(f"❌ [AGENT DECISION FAILED] {self.agent_id} - No decision returned from Groq")
                
            return decision
        except Exception as e:
            print(f"❌ [AGENT DECISION ERROR] {self.agent_id} - Error: {e}")
            await self.log_action("decision_error", {"error": str(e)}, "error")
            return None
    
    # Remove the run method and the abstract process method
    # Agents will only act when triggered via API 