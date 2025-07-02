#!/usr/bin/env python3
"""
Test script for AI model integration
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.ai.model_manager import get_ai_model_manager
from app.core.config import settings

async def test_ai_model_manager():
    """Test the AI model manager"""
    print("🤖 Testing AI Model Manager...")
    
    try:
        # Initialize AI model manager
        ai_manager = await get_ai_model_manager()
        
        print(f"✅ AI Model Manager initialized successfully")
        print(f"📊 Available providers: {ai_manager.get_available_providers()}")
        print(f"🔧 Provider status: {ai_manager.get_provider_status()}")
        
        # Test basic generation
        print("\n🧪 Testing AI generation...")
        response = await ai_manager.generate_response(
            prompt="What is the capital of France?",
            system_message="You are a helpful assistant. Provide concise answers."
        )
        
        print(f"✅ AI generation successful")
        print(f"📝 Response: {response['content'][:100]}...")
        print(f"🤖 Model: {response['model']}")
        print(f"🏢 Provider: {response['provider']}")
        
        print("\n🎉 All AI integration tests completed successfully!")
        
    except Exception as e:
        print(f"❌ AI integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def main():
    """Main test function"""
    print("🚀 Starting AI Model Integration Tests")
    print("=" * 50)
    
    # Check configuration
    print("🔧 Checking AI configuration...")
    print(f"   Default provider: {settings.DEFAULT_AI_PROVIDER}")
    print(f"   Fallback provider: {settings.AI_FALLBACK_PROVIDER}")
    print(f"   Cache enabled: {settings.AI_CACHE_ENABLED}")
    print(f"   Monitoring enabled: {settings.AI_MONITORING_ENABLED}")
    
    # Check API keys
    print("\n🔑 Checking API keys...")
    if settings.OPENAI_API_KEY:
        print("   ✅ OpenAI API key configured")
    else:
        print("   ⚠️  OpenAI API key not configured")
    
    if settings.ANTHROPIC_API_KEY:
        print("   ✅ Anthropic API key configured")
    else:
        print("   ⚠️  Anthropic API key not configured")
    
    print("\n" + "=" * 50)
    
    # Run tests
    success = await test_ai_model_manager()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 AI Integration Test Summary: SUCCESS")
    else:
        print("❌ AI Integration Test Summary: FAILED")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
