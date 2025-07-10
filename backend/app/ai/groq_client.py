import asyncio
import json
from typing import Dict, List, Any, Optional
from groq import Groq
from groq.types.chat import ChatCompletion
from ..core.config import settings

class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
    
    async def get_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Optional[str]:
        """Get completion from Groq LLM"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                messages=messages,
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting Groq completion: {e}")
            return None
    
    async def get_structured_response(
        self, 
        prompt: str, 
        response_format: Dict[str, Any],
        temperature: float = 0.3
    ) -> Optional[Dict[str, Any]]:
        """Get structured JSON response from Groq"""
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
                return json.loads(response)
            return None
        except Exception as e:
            print(f"Error getting structured response: {e}")
            return None

# Global instance
groq_client = GroqClient() 