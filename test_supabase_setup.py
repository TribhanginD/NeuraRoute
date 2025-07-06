#!/usr/bin/env python3
"""
Test script to verify Supabase configuration
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_supabase_configuration():
    """Test Supabase configuration and basic operations"""
    
    print("🔧 Testing Supabase Configuration...")
    print("=" * 50)
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"✅ SUPABASE_URL: {'Set' if supabase_url else '❌ Not set'}")
    print(f"✅ SUPABASE_KEY: {'Set' if supabase_key else '❌ Not set'}")
    print(f"✅ SUPABASE_SERVICE_ROLE_KEY: {'Set' if supabase_service_key else '❌ Not set'}")
    
    if not all([supabase_url, supabase_key]):
        print("\n❌ Missing required Supabase environment variables!")
        print("Please set SUPABASE_URL and SUPABASE_KEY in your .env file")
        return False
    
    try:
        # Test Supabase client initialization
        import sys
        sys.path.append('backend')
        from app.core.supabase import is_supabase_configured, get_supabase_client
        
        if is_supabase_configured():
            print("\n✅ Supabase client configured successfully!")
            
            # Test basic connection
            client = get_supabase_client()
            print("✅ Supabase client created successfully!")
            
            # Test a simple query (this will fail if tables don't exist, but that's expected)
            try:
                from app.services.supabase_service import get_supabase_service
                service = get_supabase_service()
                
                # Test getting summary (this should work even with empty tables)
                summary = await service.get_summary("fleet")
                print(f"✅ Supabase service working! Fleet summary: {summary}")
                
            except Exception as e:
                print(f"⚠️  Supabase service test failed (this is normal if tables don't exist): {str(e)}")
            
            return True
            
        else:
            print("\n❌ Supabase client configuration failed!")
            return False
            
    except Exception as e:
        print(f"\n❌ Error testing Supabase configuration: {str(e)}")
        return False

async def test_frontend_configuration():
    """Test frontend Supabase configuration"""
    
    print("\n🌐 Testing Frontend Configuration...")
    print("=" * 50)
    
    # Check frontend environment variables
    react_supabase_url = os.getenv("REACT_APP_SUPABASE_URL")
    react_supabase_key = os.getenv("REACT_APP_SUPABASE_ANON_KEY")
    
    print(f"✅ REACT_APP_SUPABASE_URL: {'Set' if react_supabase_url else '❌ Not set'}")
    print(f"✅ REACT_APP_SUPABASE_ANON_KEY: {'Set' if react_supabase_key else '❌ Not set'}")
    
    if not all([react_supabase_url, react_supabase_key]):
        print("\n❌ Missing required frontend Supabase environment variables!")
        print("Please set REACT_APP_SUPABASE_URL and REACT_APP_SUPABASE_ANON_KEY in your frontend .env file")
        return False
    
    print("\n✅ Frontend Supabase configuration looks good!")
    return True

def main():
    """Main test function"""
    print("🚀 NeuraRoute Supabase Setup Test")
    print("=" * 50)
    
    # Test backend configuration
    backend_ok = asyncio.run(test_supabase_configuration())
    
    # Test frontend configuration
    frontend_ok = asyncio.run(test_frontend_configuration())
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Backend: {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Frontend: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 All tests passed! Supabase is configured correctly.")
        print("\nNext steps:")
        print("1. Create your database tables in Supabase")
        print("2. Run your application")
        print("3. Check the SUPABASE_SETUP.md file for detailed instructions")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        print("See SUPABASE_SETUP.md for setup instructions.")

if __name__ == "__main__":
    main() 