"""
Database configuration and connection management
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
import redis.asyncio as redis
import structlog

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    poolclass=NullPool,  # Disable connection pooling for async
    future=True
)

# Create sync engine for migrations
sync_engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()

# Redis client
redis_client: redis.Redis = None


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_keepalive=True,
            socket_keepalive_options={},
            retry_on_timeout=True,
            health_check_interval=30,
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established successfully")
        
    except Exception as e:
        logger.error("Failed to connect to Redis", error=str(e))
        raise


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")


async def init_db():
    """Initialize database connection and create tables"""
    try:
        # Test connection
        async with async_engine.begin() as conn:
            await conn.run_sync(lambda sync_conn: sync_conn.execute(text("SELECT 1")))
        
        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_db():
    """Close database connections"""
    try:
        await async_engine.dispose()
        sync_engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_db_session() -> AsyncSession:
    """Get database session (for dependency injection)"""
    async with AsyncSessionLocal() as session:
        return session


# Database utilities
async def execute_query(query: str, params: Optional[dict] = None):
    """Execute a raw SQL query"""
    async for db in get_db():
        result = await db.execute(query, params or {})
        break
    return result


async def health_check() -> bool:
    """Check database health"""
    try:
        async for db in get_db():
            await db.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


# Migration utilities
def get_migration_engine():
    """Get engine for migrations"""
    return sync_engine


def get_migration_metadata():
    """Get metadata for migrations"""
    return metadata


# Connection pool monitoring
async def get_connection_info():
    """Get database connection information"""
    try:
        async for db in get_db():
            result = await db.execute(text("SELECT version()"))
            version = result.scalar()
            
            return {
                "status": "connected",
                "version": version,
                "url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "unknown"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# Redis utilities
async def get_cache(key: str) -> str:
    """Get value from Redis cache"""
    try:
        if redis_client:
            return await redis_client.get(key)
    except Exception as e:
        logger.error("Redis get failed", key=key, error=str(e))
    return None


async def set_cache(key: str, value: str, expire: int = 3600) -> bool:
    """Set value in Redis cache with expiration"""
    try:
        if redis_client:
            await redis_client.setex(key, expire, value)
            return True
    except Exception as e:
        logger.error("Redis set failed", key=key, error=str(e))
    return False


async def delete_cache(key: str) -> bool:
    """Delete value from Redis cache"""
    try:
        if redis_client:
            await redis_client.delete(key)
            return True
    except Exception as e:
        logger.error("Redis delete failed", key=key, error=str(e))
    return False


async def clear_cache_pattern(pattern: str) -> int:
    """Clear cache entries matching pattern"""
    try:
        if redis_client:
            keys = await redis_client.keys(pattern)
            if keys:
                return await redis_client.delete(*keys)
    except Exception as e:
        logger.error("Redis clear pattern failed", pattern=pattern, error=str(e))
    return 0


# Initialize connections on module import
async def init_connections():
    """Initialize all database connections"""
    await init_db()
    await init_redis()


async def close_connections():
    """Close all database connections"""
    await close_db()
    await close_redis() 