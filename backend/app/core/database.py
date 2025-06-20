from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Database engine
engine = create_engine(
    settings.database_url,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=settings.debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Redis client
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Dependency to get Redis client"""
    return redis_client

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise

def check_db_connection():
    """Check database connection"""
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error("Database connection failed", error=str(e))
        return False

def check_redis_connection():
    """Check Redis connection"""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))
        return False 