#!/usr/bin/env python3
"""
Скрипт для запуска Celery worker в режиме разработки
"""
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.celery_config import celery_app

if __name__ == "__main__":
    # Устанавливаем PYTHONPATH
    os.environ.setdefault("PYTHONPATH", str(project_root))
    
    # Запускаем Celery worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=2",
        "--queues=ai_forum_queue",
    ])
