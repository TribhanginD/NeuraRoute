from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "NeuraRoute"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Database
    database_url: str = "postgresql://neuraroute:neuraroute123@localhost:5432/neuraroute"
    redis_url: str = "redis://localhost:6379"
    
    # AI APIs
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Mapbox
    mapbox_token: Optional[str] = None
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Simulation
    simulation_tick_interval: int = 900  # 15 minutes in seconds
    max_agent_retries: int = 3
    agent_timeout: int = 300  # 5 minutes
    
    # Agent Settings
    agent_memory_size: int = 1000
    agent_retention_days: int = 7
    
    # Forecasting
    forecast_horizon_hours: int = 24
    forecast_update_interval: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings() 