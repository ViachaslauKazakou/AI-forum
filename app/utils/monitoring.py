"""
Мониторинг и метрики для AI-форума
"""
import logging
import time
from functools import wraps
from typing import Any, Callable

import structlog
from prometheus_client import Counter, Gauge, Histogram, generate_latest

# Метрики Prometheus
REQUEST_COUNT = Counter(
    'forum_requests_total', 
    'Total requests', 
    ['service', 'endpoint', 'method']
)

REQUEST_DURATION = Histogram(
    'forum_request_duration_seconds',
    'Request duration',
    ['service', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'forum_active_users',
    'Number of active users'
)

RAG_PROCESSING_TIME = Histogram(
    'rag_processing_duration_seconds',
    'RAG processing time',
    ['character', 'success']
)

AI_GENERATION_TIME = Histogram(
    'ai_generation_duration_seconds', 
    'AI response generation time',
    ['model', 'success']
)

# Структурированное логирование
logger = structlog.get_logger()

def monitor_performance(service_name: str):
    """Декоратор для мониторинга производительности"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            endpoint = func.__name__
            
            REQUEST_COUNT.labels(
                service=service_name,
                endpoint=endpoint,
                method='POST'
            ).inc()
            
            try:
                result = await func(*args, **kwargs)
                
                duration = time.time() - start_time
                REQUEST_DURATION.labels(
                    service=service_name,
                    endpoint=endpoint
                ).observe(duration)
                
                logger.info(
                    "Request completed",
                    service=service_name,
                    endpoint=endpoint,
                    duration=duration,
                    success=True
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(
                    "Request failed",
                    service=service_name,
                    endpoint=endpoint,
                    duration=duration,
                    error=str(e),
                    success=False
                )
                raise
                
        return wrapper
    return decorator

class HealthChecker:
    """Проверка здоровья сервисов"""
    
    def __init__(self):
        self.checks = {}
    
    def register_check(self, name: str, check_func: Callable):
        """Регистрация проверки здоровья"""
        self.checks[name] = check_func
    
    async def get_health_status(self) -> dict:
        """Получение статуса здоровья всех компонентов"""
        results = {}
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                result = await check_func()
                results[name] = {
                    "status": "healthy",
                    "details": result
                }
            except Exception as e:
                results[name] = {
                    "status": "unhealthy", 
                    "error": str(e)
                }
                overall_healthy = False
        
        return {
            "overall_status": "healthy" if overall_healthy else "unhealthy",
            "services": results,
            "timestamp": time.time()
        }
