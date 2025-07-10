#!/usr/bin/env python3
"""
Standalone script to start the NeuraRoute Agentic System
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables
load_dotenv()

from app.agents.manager import agent_manager

async def main():
    """Main function to start the agentic system"""
    print("🚀 Starting NeuraRoute Agentic System...")
    
    try:
        # Check required environment variables
        required_vars = ['SUPABASE_URL', 'SUPABASE_KEY', 'GROQ_API_KEY']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {missing_vars}")
            print("Please set these variables in your .env file")
            return
        
        print("✅ Environment variables loaded successfully")
        
        # Initialize and start agents
        await agent_manager.initialize_agents()
        print("✅ Agents initialized")
        
        await agent_manager.start_agents()
        print("✅ Agents started")
        
        print("🤖 Agentic system is now running!")
        print("Press Ctrl+C to stop...")
        
        # Keep the system running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping agentic system...")
            await agent_manager.stop_agents()
            print("✅ Agentic system stopped")
    
    except Exception as e:
        print(f"❌ Error starting agentic system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 