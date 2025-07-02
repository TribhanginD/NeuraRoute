"""
Logging configuration for NeuraRoute
"""

import logging
import logging.handlers
import sys
import os
from pathlib import Path
from typing import Dict, Any

import structlog
from app.core.config import settings

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" else structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


def setup_logging():
    """Setup logging configuration"""
    
    # Create logs directory if it doesn't exist
    log_path = Path(settings.LOG_FILE_PATH)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    if settings.LOG_FORMAT == "json":
        console_formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer()
        )
    else:
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE_PATH,
        maxBytes=settings.LOG_MAX_SIZE_MB * 1024 * 1024,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    if settings.LOG_FORMAT == "json":
        file_formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer()
        )
    else:
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Set specific log levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    
    # Create logger for this module
    logger = structlog.get_logger(__name__)
    logger.info("Logging configured successfully", 
                level=settings.LOG_LEVEL, 
                format=settings.LOG_FORMAT,
                file_path=settings.LOG_FILE_PATH)


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get structured logger"""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin to add logging capabilities to classes"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs):
        """Log info message with context"""
        self.logger.info(message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self.logger.warning(message, **kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log error message with context"""
        self.logger.error(message, **kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self.logger.debug(message, **kwargs)


# Context managers for logging
class LogContext:
    """Context manager for logging with additional context"""
    
    def __init__(self, logger: structlog.BoundLogger, context: Dict[str, Any]):
        self.logger = logger.bind(**context)
        self.context = context
    
    def __enter__(self):
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.logger.error("Context execution failed", 
                             exc_type=exc_type.__name__,
                             exc_value=str(exc_val))


def log_execution_time(logger: structlog.BoundLogger, operation: str):
    """Decorator to log execution time"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{operation} completed successfully",
                           execution_time=execution_time)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{operation} failed",
                            execution_time=execution_time,
                            error=str(e))
                raise
        
        def sync_wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(f"{operation} completed successfully",
                           execution_time=execution_time)
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{operation} failed",
                            execution_time=execution_time,
                            error=str(e))
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Performance monitoring
class PerformanceLogger:
    """Performance logging utilities"""
    
    def __init__(self, logger: structlog.BoundLogger):
        self.logger = logger
        self.metrics = {}
    
    def start_timer(self, operation: str):
        """Start timing an operation"""
        import time
        self.metrics[operation] = {"start": time.time()}
    
    def end_timer(self, operation: str, success: bool = True):
        """End timing an operation"""
        import time
        if operation in self.metrics:
            end_time = time.time()
            duration = end_time - self.metrics[operation]["start"]
            self.logger.info(f"Operation {operation} completed",
                           operation=operation,
                           duration=duration,
                           success=success)
            del self.metrics[operation]
    
    def log_metric(self, name: str, value: float, unit: str = None):
        """Log a metric"""
        self.logger.info("Metric recorded",
                        metric_name=name,
                        metric_value=value,
                        metric_unit=unit)


# Error tracking
def log_exception(logger: structlog.BoundLogger, exception: Exception, context: Dict[str, Any] = None):
    """Log an exception with context"""
    logger.error("Exception occurred",
                exception_type=type(exception).__name__,
                exception_message=str(exception),
                context=context or {},
                exc_info=True)


# Request logging
def log_request(logger: structlog.BoundLogger, method: str, url: str, status_code: int = None, 
                duration: float = None, user_id: str = None):
    """Log HTTP request"""
    log_data = {
        "method": method,
        "url": url,
        "status_code": status_code,
        "duration": duration,
        "user_id": user_id
    }
    
    if status_code and status_code >= 400:
        logger.warning("HTTP request", **log_data)
    else:
        logger.info("HTTP request", **log_data)


# Agent logging
def log_agent_action(logger: structlog.BoundLogger, agent_id: str, action: str, 
                    result: Dict[str, Any] = None, duration: float = None):
    """Log agent action"""
    logger.info("Agent action executed",
                agent_id=agent_id,
                action=action,
                result=result,
                duration=duration)


# Simulation logging
def log_simulation_tick(logger: structlog.BoundLogger, tick_number: int, 
                       agent_count: int, events_count: int, duration: float):
    """Log simulation tick"""
    logger.info("Simulation tick completed",
                tick_number=tick_number,
                agent_count=agent_count,
                events_count=events_count,
                duration=duration) 