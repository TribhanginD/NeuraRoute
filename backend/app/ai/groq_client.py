import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from groq import Groq
from groq.types.chat import ChatCompletion
from ..core.config import settings

class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        print(f"🔧 GroqClient initialized with model: {self.model}")
    
    async def get_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Optional[str]:
        """Get completion from Groq LLM"""
        start_time = time.time()
        request_id = f"groq_{int(start_time * 1000)}"
        
        print(f"\n🚀 [GROQ REQUEST] {request_id}")
        print(f"📤 Model: {self.model}")
        print(f"📤 Temperature: {temperature}")
        print(f"📤 Max Tokens: {max_tokens}")
        print(f"📤 Messages: {len(messages)}")
        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            print(f"📤 Message {i+1} ({role}): {content[:200]}{'...' if len(content) > 200 else ''}")
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                messages=messages,
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n✅ [GROQ RESPONSE] {request_id}")
            print(f"📥 Duration: {duration:.2f}s")
            print(f"📥 Usage: {response.usage}")
            print(f"📥 Response: {response.choices[0].message.content[:500]}{'...' if len(response.choices[0].message.content) > 500 else ''}")
            
            return response.choices[0].message.content
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n❌ [GROQ ERROR] {request_id}")
            print(f"📥 Duration: {duration:.2f}s")
            print(f"📥 Error: {e}")
            print(f"📥 Error Type: {type(e).__name__}")
            return None
    
    async def get_structured_response(
        self, 
        prompt: str, 
        response_format: Dict[str, Any],
        temperature: float = 0.3
    ) -> Optional[Dict[str, Any]]:
        """Get structured JSON response from Groq"""
        start_time = time.time()
        request_id = f"groq_structured_{int(start_time * 1000)}"
        
        print(f"\n🎯 [GROQ STRUCTURED REQUEST] {request_id}")
        print(f"📤 Model: {self.model}")
        print(f"📤 Temperature: {temperature}")
        print(f"📤 Response Format: {json.dumps(response_format, indent=2)}")
        print(f"📤 Prompt: {prompt[:300]}{'...' if len(prompt) > 300 else ''}")
        
        try:
            # Add system message to ensure JSON output
            system_message = f"""You are an AI agent that responds in valid JSON format. 
            Always respond with valid JSON that matches the expected structure.
            Response format: {json.dumps(response_format, indent=2)}"""
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.get_completion(messages, temperature)
            if response:
                try:
                    parsed_response = json.loads(response)
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    print(f"\n✅ [GROQ STRUCTURED RESPONSE] {request_id}")
                    print(f"📥 Duration: {duration:.2f}s")
                    print(f"📥 Parsed JSON: {json.dumps(parsed_response, indent=2)}")
                    
                    return parsed_response
                except json.JSONDecodeError as json_error:
                    # Try to extract JSON from the response if there's extra data
                    try:
                        # Look for the last JSON object in the response (skip schema definitions)
                        json_objects = []
                        start = 0
                        while True:
                            start_idx = response.find('{', start)
                            if start_idx == -1:
                                break
                            
                            # Find the matching closing brace
                            brace_count = 0
                            end_idx = start_idx
                            for i in range(start_idx, len(response)):
                                if response[i] == '{':
                                    brace_count += 1
                                elif response[i] == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        end_idx = i + 1
                                        break
                            
                            if end_idx > start_idx:
                                json_part = response[start_idx:end_idx]
                                try:
                                    parsed = json.loads(json_part)
                                    json_objects.append(parsed)
                                except:
                                    pass
                            
                            start = end_idx
                        
                        # Use the last valid JSON object (skip schema definitions)
                        if json_objects:
                            # Look for the object that matches our expected structure
                            for obj in reversed(json_objects):
                                if isinstance(obj, dict) and any(key in obj for key in ['expiry_recommendations', 'recommendations', 'actions']):
                                    parsed_response = obj
                                    break
                            else:
                                # If no matching structure found, use the last object
                                parsed_response = json_objects[-1]
                            
                            end_time = time.time()
                            duration = end_time - start_time
                            
                            print(f"\n✅ [GROQ STRUCTURED RESPONSE - EXTRACTED] {request_id}")
                            print(f"📥 Duration: {duration:.2f}s")
                            print(f"📥 Extracted JSON: {json.dumps(parsed_response, indent=2)}")
                            print(f"📥 Note: Found {len(json_objects)} JSON objects, used the most relevant one")
                            
                            return parsed_response
                    except Exception as extract_error:
                        end_time = time.time()
                        duration = end_time - start_time
                        
                        print(f"\n❌ [GROQ JSON PARSE ERROR] {request_id}")
                        print(f"📥 Duration: {duration:.2f}s")
                        print(f"📥 Raw Response: {response}")
                        print(f"📥 JSON Error: {json_error}")
                        print(f"📥 Extract Error: {extract_error}")
                        return None
            return None
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n❌ [GROQ STRUCTURED ERROR] {request_id}")
            print(f"📥 Duration: {duration:.2f}s")
            print(f"📥 Error: {e}")
            print(f"📥 Error Type: {type(e).__name__}")
            return None

# Global instance
groq_client = GroqClient() 