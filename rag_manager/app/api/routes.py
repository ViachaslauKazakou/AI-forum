"""
API роуты для RAG сервиса
"""
import logging
import time
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import HealthStatus, RAGRequest, RAGResponse, UserKnowledge
from app.services.knowledge_service import KnowledgeService
from app.services.rag_service import RAGService
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)

router = APIRouter()

# Глобальные сервисы
rag_service = RAGService()
knowledge_service = KnowledgeService()
vector_service = VectorService()

# Время старта сервиса
startup_time = time.time()


@router.post("/rag/process", response_model=RAGResponse)
async def process_rag_request(
    request: RAGRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Обрабатывает RAG запрос
    
    Args:
        request: Запрос с параметрами для обработки
        db: Сессия базы данных
        
    Returns:
        Ответ с сгенерированным промптом и контекстом
    """
    try:
        logger.info(f"Processing RAG request for user {request.user_id}, topic: {request.topic}")
        
        response = await rag_service.process_rag_request(request, db)
        
        logger.info(f"RAG request processed successfully in {response.processing_time:.3f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error processing RAG request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing RAG request: {str(e)}"
        )


@router.get("/users/{user_id}/knowledge", response_model=UserKnowledge)
async def get_user_knowledge(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Получает знания пользователя
    
    Args:
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        Знания пользователя
    """
    try:
        knowledge = await knowledge_service.load_user_knowledge(user_id, db)
        
        if not knowledge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge not found for user {user_id}"
            )
        
        return knowledge
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user knowledge: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting user knowledge: {str(e)}"
        )


@router.get("/users", response_model=list[str])
async def list_available_users():
    """
    Возвращает список доступных пользователей
    
    Returns:
        Список ID пользователей
    """
    try:
        user_ids = await knowledge_service.get_all_user_ids()
        return user_ids
        
    except Exception as e:
        logger.error(f"Error listing users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing users: {str(e)}"
        )


@router.get("/health", response_model=HealthStatus)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Проверка здоровья сервиса
    
    Args:
        db: Сессия базы данных
        
    Returns:
        Статус здоровья сервиса
    """
    try:
        # Проверяем подключение к БД
        db_status = "healthy"
        try:
            await vector_service.get_database_stats(db)
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        # Проверяем векторную БД
        vector_db_status = "healthy"
        try:
            stats = await vector_service.get_database_stats(db)
            if stats["total_embeddings"] == 0:
                vector_db_status = "healthy (no embeddings)"
        except Exception as e:
            vector_db_status = f"unhealthy: {str(e)}"
        
        # Проверяем базу знаний
        knowledge_base_status = "healthy"
        try:
            user_ids = await knowledge_service.get_all_user_ids()
            if not user_ids:
                knowledge_base_status = "healthy (no users)"
        except Exception as e:
            knowledge_base_status = f"unhealthy: {str(e)}"
        
        # Общий статус
        overall_status = "healthy"
        if "unhealthy" in db_status or "unhealthy" in vector_db_status or "unhealthy" in knowledge_base_status:
            overall_status = "unhealthy"
        
        uptime = time.time() - startup_time
        
        return HealthStatus(
            status=overall_status,
            timestamp=datetime.now(),
            database_status=db_status,
            vector_db_status=vector_db_status,
            knowledge_base_status=knowledge_base_status,
            uptime=uptime
        )
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return HealthStatus(
            status="unhealthy",
            timestamp=datetime.now(),
            database_status=f"error: {str(e)}",
            vector_db_status="unknown",
            knowledge_base_status="unknown",
            uptime=time.time() - startup_time
        )


@router.post("/cache/clear")
async def clear_cache():
    """
    Очищает кэш сервиса
    
    Returns:
        Статус операции
    """
    try:
        knowledge_service.clear_cache()
        return {"status": "success", "message": "Cache cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing cache: {str(e)}"
        )


@router.get("/stats")
async def get_service_stats(db: AsyncSession = Depends(get_db)):
    """
    Получает статистику сервиса
    
    Args:
        db: Сессия базы данных
        
    Returns:
        Статистика сервиса
    """
    try:
        # Статистика БД
        db_stats = await vector_service.get_database_stats(db)
        
        # Статистика пользователей
        user_ids = await knowledge_service.get_all_user_ids()
        
        uptime = time.time() - startup_time
        
        return {
            "uptime_seconds": uptime,
            "database_stats": db_stats,
            "available_users": len(user_ids),
            "user_list": user_ids,
            "startup_time": datetime.fromtimestamp(startup_time).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting stats: {str(e)}"
        )
