"""
Celery tasks for AI Forum
"""
from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.celery_config import celery_app
from app.config import get_settings
from shared_models.models import Task  # используем модель из shared_models (таблица "tasks")

# Асинхронное подключение к той же БД, что и у основного приложения
settings = get_settings
async_engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def _process_task_async(task_db_id: int) -> Dict[str, Any]:
    """Асинхронная обработка задачи"""
    async with AsyncSessionLocal() as session:
        # 1) Получаем задачу из БД
        q = await session.execute(select(Task).where(Task.id == task_db_id))
        task = q.scalar_one_or_none()
        if not task:
            return {"error": f"Task with ID {task_db_id} not found"}

        # 2) Помечаем задачу как processing и фиксируем started_at
        task.status = "processing"
        task.started_at = datetime.utcnow()
        await session.commit()

        try:
            # TODO: здесь реализуйте основную логику обработки задачи
            # В зависимости от типа задачи можно добавить разную логику
            
            # Имитация обработки
            await asyncio.sleep(1)
            
            # Завершаем задачу успешно
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            if hasattr(task, "result"):
                task.result = "Task completed successfully"
            await session.commit()
            
            return {"status": "success", "task_id": task_db_id}
            
        except Exception as e:
            # Фиксируем ошибку
            q = await session.execute(select(Task).where(Task.id == task_db_id))
            task = q.scalar_one_or_none()
            if task:
                task.status = "failed"
                task.completed_at = datetime.utcnow()
                if hasattr(task, "error_message"):
                    task.error_message = str(e)
                await session.commit()
            
            return {"status": "error", "task_id": task_db_id, "error": str(e)}


@celery_app.task(name="process_task", bind=True)
def process_task(self, task_db_id: int):
    """
    Celery-задача: принимает ID записи в таблице tasks, 
    обрабатывает и обновляет статус.
    """
    try:
        result = asyncio.run(_process_task_async(task_db_id))
        return result
    except Exception as exc:
        # Повторная попытка с экспоненциальной задержкой
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task(name="test_task")
def test_task(message: str = "Hello from Celery!"):
    """Тестовая задача для проверки работы Celery"""
    return f"Test task executed: {message}"


@celery_app.task(name="ai_analysis_task")
def ai_analysis_task(topic_id: int, message_id: int):
    """Задача для AI анализа сообщений"""
    # TODO: Реализовать AI анализ
    return {"topic_id": topic_id, "message_id": message_id, "analysis": "completed"}
