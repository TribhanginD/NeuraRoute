#!/usr/bin/env python3
"""
Simple script to test API endpoints and see what data they return
"""
import asyncio
import json
from httpx import AsyncClient
from app.main import app

async def test_api_endpoints():
    """Test various API endpoints and print their responses"""
    async with AsyncClient(base_url="http://test") as client:
        
        print("=== API Data Test Results ===\n")
        
        # Test health endpoint
        print("1. Health Check:")
        try:
            response = await client.get("/health")
            print(f"   Status: {response.status_code}")
            print(f"   Data: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"   Error: {e}")
        print()
        
        # Test simulation status
        print("2. Simulation Status:")
        try:
            response = await client.get("/api/v1/simulation/status")
            print(f"   Status: {response.status_code}")
            print(f"   Data: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"   Error: {e}")
        print()
        
        # Test forecasting current
        print("3. Forecasting Current:")
        try:
            response = await client.get("/api/v1/forecasting/current")
            print(f"   Status: {response.status_code}")
            print(f"   Data: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"   Error: {e}")
        print()
        
        # Test inventory
        print("4. Inventory All:")
        try:
            response = await client.get("/api/v1/inventory/")
            print(f"   Status: {response.status_code}")
            print(f"   Data: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"   Error: {e}")
        print()
        
        # Test fleet
        print("5. Fleet All:")
        try:
            response = await client.get("/api/v1/fleet/")
            print(f"   Status: {response.status_code}")
            print(f"   Data: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"   Error: {e}")
        print()
        
        # Test merchant creation
        print("6. Merchant Creation:")
        try:
            merchant_data = {
                "name": "Test Merchant",
                "location": {"lat": 40.7128, "lng": -74.0060},
                "category": "retail",
                "status": "active"
            }
            response = await client.post("/api/v1/merchants/", json=merchant_data)
            print(f"   Status: {response.status_code}")
            print(f"   Data: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"   Error: {e}")
        print()

if __name__ == "__main__":
    asyncio.run(test_api_endpoints()) 