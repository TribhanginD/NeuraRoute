import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "NeuraRoute Agentic System"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # Groq LLM Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-8b-8192")
    
    # Redis for caching and task queue
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Agent Configuration
    AGENT_UPDATE_INTERVAL: int = int(os.getenv("AGENT_UPDATE_INTERVAL", "30"))  # seconds
    MAX_CONCURRENT_AGENTS: int = int(os.getenv("MAX_CONCURRENT_AGENTS", "10"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings() 