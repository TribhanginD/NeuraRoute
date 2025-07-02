"""
Pytest configuration and fixtures for NeuraRoute backend tests
"""

import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.agents.manager import AgentManager
from app.simulation.engine import SimulationEngine


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:neuraroute123@localhost:5432/neuraroute_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def test_session_factory(test_engine):
    """Create test session factory."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    yield async_session


@pytest.fixture
async def test_db(test_engine, test_session_factory):
    """Create test database and session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with test_session_factory() as session:
        yield session
    
    # Cleanup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_redis():
    """Create test Redis client."""
    redis_client = redis.from_url("redis://localhost:6379/1")
    yield redis_client
    await redis_client.flushdb()
    await redis_client.close()


@pytest.fixture
def client(test_db, test_redis):
    """Create test client with overridden dependencies."""
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_agent_manager():
    """Create mock agent manager."""
    manager = AsyncMock(spec=AgentManager)
    manager.is_healthy.return_value = True
    manager.get_agents.return_value = []
    manager.start_agent.return_value = True
    manager.stop_agent.return_value = True
    return manager


@pytest.fixture
def mock_simulation_engine():
    """Create mock simulation engine."""
    engine = AsyncMock(spec=SimulationEngine)
    engine.is_healthy.return_value = True
    engine.is_running.return_value = False
    engine.start.return_value = True
    engine.stop.return_value = True
    return engine


@pytest.fixture
def sample_merchant_data():
    """Sample merchant data for testing."""
    return {
        "id": "merchant_001",
        "name": "Test Merchant",
        "location": {"lat": 40.7128, "lng": -74.0060},
        "category": "restaurant",
        "status": "active"
    }


@pytest.fixture
def sample_fleet_data():
    """Sample fleet data for testing."""
    return {
        "id": "fleet_001",
        "vehicle_type": "van",
        "capacity": 1000,
        "current_location": {"lat": 40.7128, "lng": -74.0060},
        "status": "available"
    }


@pytest.fixture
def sample_inventory_data():
    """Sample inventory data for testing."""
    return {
        "id": "inventory_001",
        "merchant_id": "merchant_001",
        "items": [
            {"name": "Item 1", "quantity": 10, "price": 5.99},
            {"name": "Item 2", "quantity": 5, "price": 12.99}
        ],
        "last_updated": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_forecast_data():
    """Sample forecast data for testing."""
    return {
        "merchant_id": "merchant_001",
        "timestamp": "2024-01-01T00:00:00Z",
        "demand_forecast": 150,
        "confidence": 0.85,
        "factors": {
            "weather": "sunny",
            "events": ["local_festival"],
            "seasonal_factor": 1.2
        }
    } 