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
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.3"))
    
    # Redis for caching and task queue
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Agent Configuration
    AGENT_UPDATE_INTERVAL: int = int(os.getenv("AGENT_UPDATE_INTERVAL", "300"))  # seconds between autonomous cycles
    MAX_CONCURRENT_AGENTS: int = int(os.getenv("MAX_CONCURRENT_AGENTS", "10"))
    AGENT_MAX_RETRIES: int = int(os.getenv("AGENT_MAX_RETRIES", "3"))
    AGENT_AUTONOMOUS_TURNS: int = int(os.getenv("AGENT_AUTONOMOUS_TURNS", "1"))
    AUTO_START_AGENTS: bool = os.getenv("AUTO_START_AGENTS", "false").lower() in {"1", "true", "yes"}
    SIMULATION_ENABLED: bool = os.getenv("SIMULATION_ENABLED", "false").lower() in {"1", "true", "yes"}
    SIMULATION_TICK_SECONDS: int = int(os.getenv("SIMULATION_TICK_SECONDS", "5"))
    SIMULATION_TOTAL_TICKS: int = int(os.getenv("SIMULATION_TOTAL_TICKS", "96"))
    AUTO_START_SIMULATION: bool = os.getenv("AUTO_START_SIMULATION", "false").lower() in {"1", "true", "yes"}
    SIMULATION_STATUS_ROW_ID: str = os.getenv(
        "SIMULATION_STATUS_ROW_ID",
        "00000000-0000-4000-8000-000000000000",
    )
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings() 
