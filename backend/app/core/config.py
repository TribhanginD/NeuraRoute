"""
Configuration settings for NeuraRoute
"""

import os
from typing import List, Optional
from pydantic import validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv; load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "NeuraRoute"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:neuraroute123@localhost:5432/neuraroute"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Supabase Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # AI/ML API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_AI_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None
    LOCAL_AI_BASE_URL: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "meta-llama/llama-4-scout-17b-16e-instruct"  # Default Groq model
    
    # AI Model Configuration
    DEFAULT_AI_PROVIDER: str = "openai"  # openai, anthropic, google, cohere, huggingface, local
    DEFAULT_MODEL: str = "gpt-4o"  # Default model for general tasks
    FORECASTING_MODEL: str = "gpt-4o"  # Model for demand forecasting
    ROUTING_MODEL: str = "gpt-4o"  # Model for route optimization
    PRICING_MODEL: str = "gpt-4o"  # Model for pricing decisions
    DISPATCH_MODEL: str = "gpt-4o"  # Model for dispatch decisions
    
    # AI Model Parameters
    AI_TEMPERATURE: float = 0.1  # Default temperature for AI models
    AI_MAX_TOKENS: int = 4000  # Default max tokens
    AI_TOP_P: float = 0.9  # Default top_p parameter
    AI_FREQUENCY_PENALTY: float = 0.0  # Default frequency penalty
    AI_PRESENCE_PENALTY: float = 0.0  # Default presence penalty
    
    # AI Model Fallbacks
    AI_FALLBACK_PROVIDER: str = "anthropic"  # Fallback provider if primary fails
    AI_FALLBACK_MODEL: str = "claude-3-sonnet-20240229"  # Fallback model
    AI_ENABLE_FALLBACK: bool = True  # Enable fallback to secondary provider
    
    # AI Model Caching
    AI_CACHE_ENABLED: bool = True  # Enable AI response caching
    AI_CACHE_TTL: int = 3600  # Cache TTL in seconds
    AI_CACHE_MAX_SIZE: int = 10000  # Maximum cache entries
    
    # AI Model Monitoring
    AI_MONITORING_ENABLED: bool = True  # Enable AI model monitoring
    AI_RATE_LIMIT_PER_MINUTE: int = 60  # Rate limit for AI API calls
    AI_TIMEOUT_SECONDS: int = 30  # Timeout for AI API calls
    AI_RETRY_ATTEMPTS: int = 3  # Number of retry attempts for failed calls
    
    # Vector Database Configuration
    VECTOR_DB_TYPE: str = "chroma"  # chroma, faiss, pinecone, weaviate
    VECTOR_DB_PATH: str = "./vector_db"  # Local vector database path
    VECTOR_EMBEDDING_MODEL: str = "text-embedding-3-small"  # Embedding model
    VECTOR_DIMENSION: int = 1536  # Vector dimension size
    
    # Frontend Configuration
    REACT_APP_API_URL: str = "http://localhost:8000"
    REACT_APP_MAPBOX_TOKEN: Optional[str] = None
    REACT_APP_WS_URL: str = "ws://localhost:8000/ws"
    
    # Simulation Configuration
    SIMULATION_TICK_INTERVAL: int = 900  # 15 minutes in seconds
    AGENT_CYCLE_INTERVAL: int = 60  # 1 minute in seconds
    SIMULATION_SPEED_MULTIPLIER: float = 1.0
    
    # Agent Configuration
    AGENT_MEMORY_RETENTION_DAYS: int = 30
    AGENT_LOG_LEVEL: str = "INFO"
    AGENT_MAX_RETRIES: int = 3
    AGENT_RESTART_DELAY: int = 60
    
    # Forecasting Configuration
    FORECAST_HORIZON_HOURS: int = 24
    FORECAST_UPDATE_INTERVAL: int = 900  # 15 minutes
    FORECAST_CONFIDENCE_THRESHOLD: float = 0.7
    
    # Route Optimization
    ROUTE_OPTIMIZATION_ALGORITHM: str = "genetic"
    ROUTE_MAX_VEHICLES: int = 50
    ROUTE_MAX_STOPS_PER_VEHICLE: int = 20
    ROUTE_TRAFFIC_WEIGHT: float = 0.3
    
    # Fleet Management
    FLEET_MAX_CAPACITY: int = 1000
    FLEET_FUEL_EFFICIENCY: float = 0.8
    FLEET_MAINTENANCE_INTERVAL_HOURS: int = 168  # 1 week
    
    # Inventory Management
    INVENTORY_REORDER_THRESHOLD: float = 0.2
    INVENTORY_SAFETY_STOCK: float = 0.1
    INVENTORY_MAX_STORAGE: int = 10000
    
    # Pricing Configuration
    PRICING_BASE_MARKUP: float = 0.15
    PRICING_DYNAMIC_THRESHOLD: float = 0.3
    PRICING_MAX_INCREASE: float = 0.5
    PRICING_MAX_DECREASE: float = 0.3
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE_PATH: str = "./logs/neuraroute.log"
    LOG_MAX_SIZE_MB: int = 100
    LOG_BACKUP_COUNT: int = 5
    
    # Security Configuration
    JWT_SECRET_KEY: str = "your_jwt_secret_key_here"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # API Configuration
    API_RATE_LIMIT_PER_MINUTE: int = 100
    API_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    API_VERSION: str = "v1"
    ENABLE_SWAGGER_UI: bool = True
    ENABLE_REDOC: bool = True
    
    # Monitoring Configuration
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    HEALTH_CHECK_INTERVAL: int = 30
    ALERT_EMAIL: str = "alerts@neuraroute.com"
    
    # Optional: External Services
    WEATHER_API_KEY: Optional[str] = None
    TRAFFIC_API_KEY: Optional[str] = None
    SMS_API_KEY: Optional[str] = None
    EMAIL_API_KEY: Optional[str] = None
    
    # Optional: Analytics
    ANALYTICS_ENABLED: bool = False
    ANALYTICS_TRACKING_ID: Optional[str] = None
    
    # Optional: Backup Configuration
    BACKUP_ENABLED: bool = True
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_PATH: str = "./backups"
    
    @validator("API_CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"ENVIRONMENT must be one of {valid_envs}")
        return v.lower()
    
    @validator("ROUTE_OPTIMIZATION_ALGORITHM")
    def validate_route_algorithm(cls, v):
        valid_algorithms = ["genetic", "ant_colony", "simulated_annealing", "nearest_neighbor"]
        if v.lower() not in valid_algorithms:
            raise ValueError(f"ROUTE_OPTIMIZATION_ALGORITHM must be one of {valid_algorithms}")
        return v.lower()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance"""
    return settings 