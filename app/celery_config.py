"""
Celery configuration for AI Forum
"""
from celery import Celery
import os
from app.config import get_settings

# Получаем настройки
settings = get_settings

# Создаем экземпляр Celery
celery_app = Celery(
    "ai_forum",
    broker=settings.RABBITMQ_URL,
    backend="rpc://",  # RPC backend для результатов
    include=["app.celery_tasks"]  # Автоматически импортируем задачи
)

# Конфигурация Celery
celery_app.conf.update(
    # Часовой пояс
    timezone="UTC",
    enable_utc=True,
    
    # Настройки задач
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Настройки worker'а
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    
    # Настройки результатов
    result_expires=3600,  # Результаты храним 1 час
    
    # Маршрутизация задач
    task_routes={
        "app.celery_tasks.*": {"queue": "ai_forum_queue"},
    },
)

# Автоматическое обнаружение задач
celery_app.autodiscover_tasks(["app"])