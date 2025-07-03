"""
AI Model Manager for NeuraRoute
Handles multiple AI providers, models, caching, and fallbacks
"""

import asyncio
import structlog
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
import time

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False
    ChatGoogleGenerativeAI = None
try:
    from langchain_community.llms import Ollama
except ImportError:
    Ollama = None
    import warnings
    warnings.warn("Ollama integration is unavailable due to missing or incompatible langchain_community.")
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
# from langchain.cache import RedisCache  # Disabled: requires langchain-community
from langchain.globals import set_llm_cache
from langchain_groq import ChatGroq

from app.core.config import settings
from app.core.database import get_db

logger = structlog.get_logger()

class AIModelProvider(ABC):
    """Abstract base class for AI model providers"""
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the provider"""
        pass
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[BaseMessage], 
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response from the model"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available"""
        pass

class OpenAIProvider(AIModelProvider):
    """OpenAI provider implementation"""
    
    def __init__(self):
        self.client = None
        self.available_models = [
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"
        ]
    
    async def initialize(self) -> bool:
        """Initialize OpenAI provider"""
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            return False
        
        try:
            self.client = ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
                model=settings.DEFAULT_MODEL
            )
            logger.info("OpenAI provider initialized successfully")
            return True
        except Exception as e:
            logger.error("Failed to initialize OpenAI provider", error=str(e))
            return False
    
    async def generate_response(
        self, 
        messages: List[BaseMessage], 
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        if not self.client:
            raise ValueError("OpenAI client not initialized")
        
        try:
            model_name = model or settings.DEFAULT_MODEL
            response = await self.client.ainvoke(
                messages,
                model=model_name,
                **kwargs
            )
            
            return {
                "content": response.content,
                "model": model_name,
                "provider": "openai",
                "usage": getattr(response, 'usage', {}),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("OpenAI generation failed", error=str(e))
            raise
    
    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return self.client is not None and settings.OPENAI_API_KEY is not None

class AnthropicProvider(AIModelProvider):
    """Anthropic provider implementation"""
    
    def __init__(self):
        self.client = None
        self.available_models = [
            "claude-3-opus-20240229", "claude-3-sonnet-20240229", 
            "claude-3-haiku-20240307"
        ]
    
    async def initialize(self) -> bool:
        """Initialize Anthropic provider"""
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("Anthropic API key not configured")
            return False
        
        try:
            self.client = ChatAnthropic(
                api_key=settings.ANTHROPIC_API_KEY,
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS,
                model=settings.AI_FALLBACK_MODEL
            )
            logger.info("Anthropic provider initialized successfully")
            return True
        except Exception as e:
            logger.error("Failed to initialize Anthropic provider", error=str(e))
            return False
    
    async def generate_response(
        self, 
        messages: List[BaseMessage], 
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using Anthropic"""
        if not self.client:
            raise ValueError("Anthropic client not initialized")
        
        try:
            model_name = model or settings.AI_FALLBACK_MODEL
            response = await self.client.ainvoke(
                messages,
                model=model_name,
                **kwargs
            )
            
            return {
                "content": response.content,
                "model": model_name,
                "provider": "anthropic",
                "usage": getattr(response, 'usage', {}),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Anthropic generation failed", error=str(e))
            raise
    
    def is_available(self) -> bool:
        """Check if Anthropic is available"""
        return self.client is not None and settings.ANTHROPIC_API_KEY is not None

class GroqProvider(AIModelProvider):
    """Groq provider implementation"""
    def __init__(self):
        self.client = None
        self.available_models = [
            "meta-llama/llama-4-scout-17b-16e-instruct",  # Add more as needed
        ]

    async def initialize(self) -> bool:
        if not settings.GROQ_API_KEY:
            logger.warning("Groq API key not configured")
            return False
        try:
            self.client = ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=settings.GROQ_MODEL,
                temperature=settings.AI_TEMPERATURE,
                max_tokens=settings.AI_MAX_TOKENS
            )
            logger.info("Groq provider initialized successfully")
            return True
        except Exception as e:
            logger.error("Failed to initialize Groq provider", error=str(e))
            return False

    async def generate_response(
        self,
        messages: List[BaseMessage],
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        if not self.client:
            raise ValueError("Groq client not initialized")
        try:
            model_name = model or settings.GROQ_MODEL
            response = await self.client.ainvoke(
                messages,
                model=model_name,
                **kwargs
            )
            return {
                "content": response.content,
                "model": model_name,
                "provider": "groq",
                "usage": getattr(response, 'usage', {}),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Groq generation failed", error=str(e))
            raise

    def is_available(self) -> bool:
        return self.client is not None and settings.GROQ_API_KEY is not None

class AIModelManager:
    """Central AI model manager for NeuraRoute"""
    
    def __init__(self):
        self.providers: Dict[str, AIModelProvider] = {}
        self.active_provider: Optional[AIModelProvider] = None
        self.fallback_provider: Optional[AIModelProvider] = None
        self.cache: Dict[str, Any] = {}
        self.rate_limit_tracker: Dict[str, List[float]] = {}
        self.metrics: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "provider_usage": {}
        }
    
    async def initialize(self):
        """Initialize the AI model manager"""
        logger.info("Initializing AI Model Manager")
        
        # Initialize providers
        await self._initialize_providers()
        
        # Setup caching
        if settings.AI_CACHE_ENABLED:
            await self._setup_caching()
        
        # Setup monitoring
        if settings.AI_MONITORING_ENABLED:
            await self._setup_monitoring()
        
        logger.info("AI Model Manager initialized successfully")
    
    async def _initialize_providers(self):
        """Initialize all available AI providers"""
        provider_classes = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "groq": GroqProvider
        }
        
        for provider_name, provider_class in provider_classes.items():
            try:
                provider = provider_class()
                if await provider.initialize():
                    self.providers[provider_name] = provider
                    logger.info(f"Initialized {provider_name} provider")
            except Exception as e:
                logger.error(f"Failed to initialize {provider_name} provider", error=str(e))
        
        # Set active and fallback providers
        default_provider = settings.DEFAULT_AI_PROVIDER
        fallback_provider = settings.AI_FALLBACK_PROVIDER
        
        if default_provider in self.providers:
            self.active_provider = self.providers[default_provider]
            logger.info(f"Set {default_provider} as active provider")
        
        if fallback_provider in self.providers and fallback_provider != default_provider:
            self.fallback_provider = self.providers[fallback_provider]
            logger.info(f"Set {fallback_provider} as fallback provider")
    
    async def _setup_caching(self):
        """Setup AI response caching"""
        try:
            # Use Redis for caching if available
            # cache = RedisCache(
            #     redis_url=settings.REDIS_URL,
            #     ttl=settings.AI_CACHE_TTL
            # )
            # set_llm_cache(cache)
            logger.info("AI caching setup with Redis")
        except Exception as e:
            logger.warning("Failed to setup Redis caching, using in-memory cache", error=str(e))
    
    async def _setup_monitoring(self):
        """Setup AI model monitoring"""
        logger.info("AI monitoring enabled")
    
    async def generate_response(
        self,
        prompt: str,
        system_message: str = None,
        model: str = None,
        provider: str = None,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate AI response with fallback and caching"""
        
        # Create cache key
        cache_key = self._create_cache_key(prompt, system_message, model, provider, kwargs)
        
        # Check cache
        if use_cache and settings.AI_CACHE_ENABLED:
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                self.metrics["cache_hits"] += 1
                return cached_response
        
        self.metrics["cache_misses"] += 1
        self.metrics["total_requests"] += 1
        
        # Rate limiting
        await self._check_rate_limit(provider or settings.DEFAULT_AI_PROVIDER)
        
        # Prepare messages
        messages = self._prepare_messages(prompt, system_message)
        
        # Try primary provider
        try:
            response = await self._try_provider(
                provider or settings.DEFAULT_AI_PROVIDER,
                messages,
                model,
                **kwargs
            )
            
            self.metrics["successful_requests"] += 1
            self._update_provider_usage(provider or settings.DEFAULT_AI_PROVIDER)
            
            # Cache response
            if use_cache and settings.AI_CACHE_ENABLED:
                await self._cache_response(cache_key, response)
            
            return response
            
        except Exception as e:
            logger.error("Primary provider failed", error=str(e))
            self.metrics["failed_requests"] += 1
            
            # Try fallback provider
            if settings.AI_ENABLE_FALLBACK and self.fallback_provider:
                try:
                    logger.info("Trying fallback provider")
                    response = await self._try_provider(
                        settings.AI_FALLBACK_PROVIDER,
                        messages,
                        settings.AI_FALLBACK_MODEL,
                        **kwargs
                    )
                    
                    self.metrics["successful_requests"] += 1
                    self._update_provider_usage(settings.AI_FALLBACK_PROVIDER)
                    
                    # Cache response
                    if use_cache and settings.AI_CACHE_ENABLED:
                        await self._cache_response(cache_key, response)
                    
                    return response
                    
                except Exception as fallback_error:
                    logger.error("Fallback provider also failed", error=str(fallback_error))
                    self.metrics["failed_requests"] += 1
                    raise
    
    async def _try_provider(
        self,
        provider_name: str,
        messages: List[BaseMessage],
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Try to generate response with a specific provider"""
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not available")
        
        provider = self.providers[provider_name]
        
        if not provider.is_available():
            raise ValueError(f"Provider {provider_name} not available")
        
        return await provider.generate_response(messages, model, **kwargs)
    
    def _prepare_messages(
        self,
        prompt: str,
        system_message: str = None
    ) -> List[BaseMessage]:
        """Prepare messages for AI model"""
        messages = []
        
        if system_message:
            messages.append(SystemMessage(content=system_message))
        
        messages.append(HumanMessage(content=prompt))
        return messages
    
    def _create_cache_key(
        self,
        prompt: str,
        system_message: str = None,
        model: str = None,
        provider: str = None,
        kwargs: Dict[str, Any] = None
    ) -> str:
        """Create cache key for response"""
        key_data = {
            "prompt": prompt,
            "system_message": system_message,
            "model": model,
            "provider": provider,
            "kwargs": kwargs or {}
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        return self.cache.get(cache_key)
    
    async def _cache_response(self, cache_key: str, response: Dict[str, Any]):
        """Cache response"""
        if len(self.cache) >= settings.AI_CACHE_MAX_SIZE:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = response
    
    async def _check_rate_limit(self, provider: str):
        """Check rate limit for provider"""
        current_time = time.time()
        window_start = current_time - 60  # 1 minute window
        
        if provider not in self.rate_limit_tracker:
            self.rate_limit_tracker[provider] = []
        
        # Remove old timestamps
        self.rate_limit_tracker[provider] = [
            t for t in self.rate_limit_tracker[provider] 
            if t > window_start
        ]
        
        # Check if rate limit exceeded
        if len(self.rate_limit_tracker[provider]) >= settings.AI_RATE_LIMIT_PER_MINUTE:
            raise Exception(f"Rate limit exceeded for provider {provider}")
        
        # Add current timestamp
        self.rate_limit_tracker[provider].append(current_time)
    
    def _update_provider_usage(self, provider: str):
        """Update provider usage metrics"""
        if provider not in self.metrics["provider_usage"]:
            self.metrics["provider_usage"][provider] = 0
        self.metrics["provider_usage"][provider] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get AI model metrics"""
        return self.metrics.copy()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all providers"""
        return {
            provider: provider_instance.is_available()
            for provider, provider_instance in self.providers.items()
        }
    
    def get_default_provider(self) -> Optional[AIModelProvider]:
        """Get the default (active) provider"""
        return self.active_provider

# Global AI model manager instance
ai_model_manager: Optional[AIModelManager] = None

async def get_ai_model_manager() -> AIModelManager:
    """Get global AI model manager instance"""
    global ai_model_manager
    if ai_model_manager is None:
        ai_model_manager = AIModelManager()
        await ai_model_manager.initialize()
    return ai_model_manager
