"""
FastAPI приложение для AI Manager
Предоставляет REST API для работы с AI персонажами форума
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Добавляем путь к модулям форума
sys.path.append('/app')
sys.path.append('/app/app')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/ai_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pydantic модели для API
class MessageRequest(BaseModel):
    character_id: int = Field(..., description="ID AI персонажа")
    user_id: int = Field(..., description="ID пользователя")
    topic_id: int = Field(..., description="ID темы форума")
    content: str = Field(..., min_length=1, max_length=2000, description="Содержание сообщения")
    context: Optional[str] = Field(None, description="Дополнительный контекст")

class MessageResponse(BaseModel):
    message_id: int = Field(..., description="ID созданного сообщения")
    content: str = Field(..., description="Содержание ответа AI")
    character_name: str = Field(..., description="Имя AI персонажа")
    created_at: str = Field(..., description="Время создания")

class CharacterInfo(BaseModel):
    id: int
    name: str
    description: str
    personality: str
    is_active: bool
    model_name: str

class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]
    uptime: float

class ErrorResponse(BaseModel):
    detail: str
    error_code: str

class OllamaService:
    """Простая обертка для работы с Ollama"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
    
    async def health_check(self):
        """Проверка работы Ollama"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def list_models(self):
        """Получение списка моделей"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["name"] for model in data.get("models", [])]
                    return []
        except Exception:
            return []
    
    async def generate_response(self, model: str, prompt: str):
        """Генерация ответа от модели"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    return "Ошибка генерации ответа"
        except Exception as e:
            return f"Ошибка: {str(e)}"

# Глобальные переменные для сервисов
ollama_service: Optional[OllamaService] = None
app_start_time: float = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекст-менеджер для инициализации и очистки ресурсов"""
    global ollama_service, app_start_time
    
    logger.info("Запуск AI Manager API...")
    app_start_time = asyncio.get_event_loop().time()
    
    try:
        # Инициализация сервисов
        ollama_service = OllamaService()
        
        logger.info("AI Manager API успешно запущен")
        
        yield
        
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
        raise
    finally:
        logger.info("AI Manager API остановлен")

# Создание FastAPI приложения
app = FastAPI(
    title="AI Manager API",
    description="REST API для управления AI персонажами форума",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency для получения OllamaService
async def get_ollama_service() -> OllamaService:
    if ollama_service is None:
        raise HTTPException(status_code=503, detail="Ollama Service не инициализирован")
    return ollama_service

# API эндпоинты

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка состояния сервиса"""
    global app_start_time
    
    uptime = asyncio.get_event_loop().time() - app_start_time
    
    services = {
        "ollama": "checking...",
        "api": "online"
    }
    
    # Проверка Ollama
    if ollama_service:
        try:
            is_healthy = await ollama_service.health_check()
            services["ollama"] = "online" if is_healthy else "offline"
        except Exception:
            services["ollama"] = "offline"
    
    return HealthResponse(
        status="healthy" if all(s == "online" for s in services.values()) else "degraded",
        version="1.0.0",
        services=services,
        uptime=uptime
    )

@app.get("/models")
async def get_available_models(
    ollama: OllamaService = Depends(get_ollama_service)
):
    """Получение списка доступных моделей Ollama"""
    try:
        models = await ollama.list_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Ошибка при получении моделей: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_response(
    model: str,
    prompt: str,
    ollama: OllamaService = Depends(get_ollama_service)
):
    """Генерация ответа от AI модели"""
    try:
        response = await ollama.generate_response(model, prompt)
        return {"response": response}
    except Exception as e:
        logger.error(f"Ошибка при генерации ответа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "AI Manager API", "version": "1.0.0"}

@app.get("/status")
async def status():
    """Статус API"""
    return {
        "status": "running",
        "timestamp": asyncio.get_event_loop().time(),
        "uptime": asyncio.get_event_loop().time() - app_start_time
    }

# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Необработанная ошибка: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            detail="Внутренняя ошибка сервера",
            error_code="INTERNAL_ERROR"
        ).dict()
    )

if __name__ == "__main__":
    # Запуск для разработки
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Dict, List, Optional

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Добавляем путь к модулям форума
sys.path.append('/app')
sys.path.append('/app/app')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/ai_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pydantic модели для API
class MessageRequest(BaseModel):
    character_id: int = Field(..., description="ID AI персонажа")
    user_id: int = Field(..., description="ID пользователя")
    topic_id: int = Field(..., description="ID темы форума")
    content: str = Field(..., min_length=1, max_length=2000, description="Содержание сообщения")
    context: Optional[str] = Field(None, description="Дополнительный контекст")

class MessageResponse(BaseModel):
    message_id: int = Field(..., description="ID созданного сообщения")
    content: str = Field(..., description="Содержание ответа AI")
    character_name: str = Field(..., description="Имя AI персонажа")
    created_at: str = Field(..., description="Время создания")

class CharacterInfo(BaseModel):
    id: int
    name: str
    description: str
    personality: str
    is_active: bool
    model_name: str

class HealthResponse(BaseModel):
    status: str
    version: str
    services: Dict[str, str]
    uptime: float

class ErrorResponse(BaseModel):
    detail: str
    error_code: str

class OllamaService:
    """Простая обертка для работы с Ollama"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
    
    async def health_check(self):
        """Проверка работы Ollama"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def list_models(self):
        """Получение списка моделей"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["name"] for model in data.get("models", [])]
                    return []
        except Exception:
            return []
    
    async def generate_response(self, model: str, prompt: str):
        """Генерация ответа от модели"""
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    return "Ошибка генерации ответа"
        except Exception as e:
            return f"Ошибка: {str(e)}"

# Глобальные переменные для сервисов
ollama_service: Optional[OllamaService] = None
app_start_time: float = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекст-менеджер для инициализации и очистки ресурсов"""
    global ollama_service, app_start_time
    
    logger.info("Запуск AI Manager API...")
    app_start_time = asyncio.get_event_loop().time()
    
    try:
        # Инициализация сервисов
        ollama_service = OllamaService()
        
        logger.info("AI Manager API успешно запущен")
        
        yield
        
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
        raise
    finally:
        logger.info("AI Manager API остановлен")

# Создание FastAPI приложения
app = FastAPI(
    title="AI Manager API",
    description="REST API для управления AI персонажами форума",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency для получения OllamaService
async def get_ollama_service() -> OllamaService:
    if ollama_service is None:
        raise HTTPException(status_code=503, detail="Ollama Service не инициализирован")
    return ollama_service

# API эндпоинты

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка состояния сервиса"""
    global app_start_time
    
    uptime = asyncio.get_event_loop().time() - app_start_time
    
    services = {
        "ollama": "checking...",
        "api": "online"
    }
    
    # Проверка Ollama
    if ollama_service:
        try:
            is_healthy = await ollama_service.health_check()
            services["ollama"] = "online" if is_healthy else "offline"
        except Exception:
            services["ollama"] = "offline"
    
    return HealthResponse(
        status="healthy" if all(s == "online" for s in services.values()) else "degraded",
        version="1.0.0",
        services=services,
        uptime=uptime
    )

@app.get("/models")
async def get_available_models(
    ollama: OllamaService = Depends(get_ollama_service)
):
    """Получение списка доступных моделей Ollama"""
    try:
        models = await ollama.list_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Ошибка при получении моделей: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_response(
    model: str,
    prompt: str,
    ollama: OllamaService = Depends(get_ollama_service)
):
    """Генерация ответа от AI модели"""
    try:
        response = await ollama.generate_response(model, prompt)
        return {"response": response}
    except Exception as e:
        logger.error(f"Ошибка при генерации ответа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "AI Manager API", "version": "1.0.0"}

@app.get("/status")
async def status():
    """Статус API"""
    return {
        "status": "running",
        "timestamp": asyncio.get_event_loop().time(),
        "uptime": asyncio.get_event_loop().time() - app_start_time
    }

# Обработчики ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Необработанная ошибка: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            detail="Внутренняя ошибка сервера",
            error_code="INTERNAL_ERROR"
        ).dict()
    )

if __name__ == "__main__":
    # Запуск для разработки
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
