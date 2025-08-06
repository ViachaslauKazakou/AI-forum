""" convert files  from json to python objects
"""
from pathlib import Path
from typing import List
from fastapi.params import Depends
from sqlalchemy import desc, select
from app.database import get_db
from app.models.models import User, Topic, Message, UsersContext
from shared_models.schemas import UserBaseContext

import json
import asyncio


class JsonConverter:
    def __init__(self):
        self.file_path = Path("app/ai_manager/forum_knowledge_base/users.json")
        pass

    def read_json(self):
        """Read JSON data from the file."""
        with self.file_path.open('r', encoding='utf-8') as file:
            return json.load(file)

    def write_json(self, data):
        """Write data to the JSON file."""
        with self.file_path.open('w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def convert_to_object(self):
        """Convert JSON data to a Python object."""
        data = self.read_json()
        return type('JsonObject', (object,), data)

    @staticmethod
    async def get_all_context(user_id=1, skip: int = 0, limit: int = 100) -> List[Topic]:
        """Получить все темы (включая неактивные) для админ-панели"""
        async for db in get_db():
            result = await db.execute(
                select(UsersContext).where(UsersContext.user_id == user_id)
                .order_by(desc(UsersContext.timestamp)).offset(skip).limit(limit)
            )
            return result.scalars().all()

    async def save_json_to_db(self):
        """Save JSON data to the database."""
        data = self.read_json()
        async for db in get_db():
            for item in data["messages"]:
                context = UserBaseContext(
                    # user_id=item["id"],
                    topic_id=item["thread_id"],
                    character=item["character"],
                    character_type=item["character_type"],
                    mood=item["mood"],
                    context=item["context"],
                    content=item["content"],
                    timestamp=item["timestamp"],
                    reply_to=item["reply_to"]
                )
                db.add(context)
            await db.commit()

    async def get_user_messages(self, username: int) -> List[UsersContext]:
        """Get all messages for a specific user."""
        async for db in get_db():
            result = await db.execute(
                select(UsersContext).where(UsersContext.character == username)
            )
            return result.scalars().all()
            


        # db.add(user)
        # db.add(topic)
        # db.add(message)
        
        # await db.commit()
        # await db.refresh(user)
        # await db.refresh(topic)
        # await db.refresh(message)

        # return user, topic, message


if __name__ == "__main__":
    # Example usage
    converter = JsonConverter()
    # asyncio.run(converter.get_all_context(user_id=1))
    asyncio.run(converter.save_json_to_db())


    
