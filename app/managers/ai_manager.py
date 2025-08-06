
import httpx
import logging
import json
from app.config import get_settings
from app.database import get_db
from app.database import async_session_maker
from app.managers.db_manager import TopicApi, MessageApi
from shared_models.models import Topic
from shared_models.schemas import MessageCreate

logger = logging.getLogger(__name__)


class AIManager:
    def __init__(self):
        self.settings = get_settings
        self.db_session = get_db()

    async def get_prompt(self, topic_id: str, user_id: str, question: str):
        """Получение подсказки для AI на основе темы и пользователя from RAG_service"""
        logger.info(f"Получение подсказки для topic_id={topic_id}, user_id={user_id}")
        service_url = self.settings.RAG_MANAGER_URL
        # Преобразуем строки в числа с валидацией
        async with async_session_maker() as session:
            topic: Topic = await TopicApi.get_topic_by_id(session, int(topic_id))  # type: ignore
        try:
            user_id_int = int(user_id)
            async with httpx.AsyncClient(timeout=120.0) as client:
                client.headers.update({
                    "Authorization": f"Bearer {self.settings.RAG_SERVICE_API_KEY}",
                    "Content-Type": "application/json",
                    "Accept": "*/*"
                })
                # Получаем подсказку
                prompt = await client.post(f"{service_url}/api/v1/rag/process", json={
                    "topic": topic.title or "",
                    "user_id": user_id_int,
                    "question": question,
                    "reply_to": "string",
                    "context_limit": 10,
                    "similarity_threshold": 0.5
                })
                print(f"Prompt response: {prompt.text}")
                return prompt.text
        except ValueError as e:
            logger.error(f"Ошибка преобразования ID: {e}")
            raise ValueError("Неверный формат ID")
        except Exception as e:
            logger.error(f"Ошибка при получении подсказки: {e}")
            raise RuntimeError("Ошибка при получении подсказки")
        
    async def generate_ai_message(self, prompt, question: str):
        """Генерация AI сообщения на основе темы и пользователя"""
        # logger.info(f"Генерация AI сообщения для topic_id={topic_id}, user_id={user_id}")
        # prompt = await self.get_prompt(str(topic_id), str(user_id), "Какой сегодня день?")
        
        if not prompt:
            raise RuntimeError("Не удалось получить подсказку от RAG сервиса")
        prompt = json.loads(prompt)  # Предполагаем, что ответ в формате JSON
        ai_url = self.settings.AI_MANAGER_URL
        headers = {
            "Authorization": f"Bearer {self.settings.AI_MANAGER_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "*/*"
        }
        try:
            timeout = 600.0  # Таймаут в 10 минут
            async with httpx.AsyncClient(timeout=timeout) as client:
                client.headers.update(headers)
                response = await client.post(f"{ai_url}/generate", params={
                    "prompt": prompt["generated_prompt"],
                    "model": "gemma3:latest",
                    "timeout": timeout,
                })
                if response.status_code != 200:
                    logger.error(f"Ошибка при генерации AI сообщения: {response.text}")
                    raise RuntimeError("Ошибка при генерации AI сообщения")
        except httpx.RequestError as e:
            logger.error(f"Ошибка запроса к AI Manager: {e}")
            raise RuntimeError("Ошибка запроса к AI Manager")
        ai_message = json.loads(response.text)
        return ai_message["response"]

    async def generate_and_save_ai_message(
        self,
        topic_id: str,
        user_id: str,
        question: str,
        last_message_content: str = "",
        reply_message_id: int = None
        ):
        """Создание AI сообщения в фоновом режиме"""
        try:
            # Преобразуем строки в числа с валидацией
            topic_id_int = int(topic_id)
            user_id_int = int(user_id)
            # make prompt
            prompt = await self.get_prompt(topic_id, user_id, question)
            # generate message
            generated_message = await self.generate_ai_message(prompt, question)

            # Сохранение AI сообщения в базе данных
            async with async_session_maker() as session:
                username = await MessageApi.get_username_by_id(session, user_id_int)
                message = MessageCreate(
                    topic_id=topic_id_int,
                    user_id=user_id_int,
                    author_name=username or "AI",
                    content=generated_message,
                    parent_id=reply_message_id
                )
                # Создаем сообщение в базе данных
                await MessageApi.create_message(session, message, last_message_content)

        except ValueError as e:
            logger.error(f"Ошибка преобразования ID: {e}")
        except Exception as e:
            logger.error(f"Ошибка при создании AI сообщения: {e}")


if __name__ == "__main__":
    # Пример использования AiManager
    rag = AIManager()
    topic_id = "1"
    user_id = "1"
    question = "Какой сегодня день?"

    import asyncio
    asyncio.run(rag.generate_and_save_ai_message(topic_id, user_id, question))