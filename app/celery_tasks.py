from __future__ import annotations

from celery import Celery
import os
import asyncio
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import get_settings
from shared_models.models import Task  # используем модель из shared_models (таблица "tasks")

# Celery: независимый воркер, брокер RabbitMQ, backend RPC (без зависимости от redis)
RABBITMQ_URL = os.getenv("RABBITMQ_URL", get_settings.RABBITMQ_URL)
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "rpc://")

celery_app = Celery(
    "ai_forum_tasks",
    broker=RABBITMQ_URL,
    backend=RESULT_BACKEND,
)

# Асинхронное подключение к той же БД, что и у основного приложения
ASYNC_DB_URL = get_settings.DATABASE_URL
async_engine = create_async_engine(ASYNC_DB_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def _process_task_async(task_db_id: int):
    async with AsyncSessionLocal() as session:
        # 1) Помечаем задачу как processing и фиксируем started_at
        q = await session.execute(select(Task).where(Task.id == task_db_id))
        task = q.scalar_one_or_none()
        if not task:
            return

        task.status = "processing"
        task.started_at = datetime.utcnow()
        await session.commit()

        try:
            # TODO: здесь реализуйте основную логику обработки задачи
            # В качестве примера просто завершаем задачу успешно
            task.status = "completed"
            task.completed_at = datetime.utcnow()
            if hasattr(task, "result"):
                task.result = "OK"
            await session.commit()
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


@celery_app.task(name="process_task")
def process_task(task_db_id: int):
    """Celery-задача: принимает ID записи в таблице tasks, обрабатывает и обновляет статус."""
    asyncio.run(_process_task_async(task_db_id))
