"""
Redis utilities for NeuraRoute
"""

from app.core.database import redis_client


async def get_redis():
    """Get Redis client instance"""
    return redis_client 