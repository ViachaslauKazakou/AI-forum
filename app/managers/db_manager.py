from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update, func
from sqlalchemy.orm import selectinload
from shared_models.models import Topic, Message, User, Category, Subcategory
from shared_models.schemas import TopicCreate, MessageCreate, TopicUpdate, MessageUpdate
from app.models.pydantic_models import UserBaseModel
from typing import List, Optional, Sequence


class UserApi:
    @staticmethod
    async def get_users_list(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[User]:
        """Получить список пользователей"""
        result = await db.execute(select(User).order_by(desc(User.created_at)).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Получить пользователя по username"""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, user: UserBaseModel) -> User:
        """Создать нового пользователя"""
        db_user = User(
            username=user.username,
            firstname=user.firstname,
            lastname=user.lastname,
            password=user.password,  # В реальном приложении нужно хешировать
            email=user.email,
            user_type=user.user_type,
            status=user.status,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_data: UserBaseModel) -> Optional[User]:
        """Обновить пользователя"""
        result = await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                username=user_data.username,
                firstname=user_data.firstname,
                lastname=user_data.lastname,
                email=user_data.email,
                user_type=user_data.user_type,
                status=user_data.status,
            )
            .returning(User)
        )
        await db.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """Удалить пользователя"""
        user = await db.get(User, user_id)
        if user:
            await db.delete(user)
            await db.commit()
            return True
        return False


class TopicApi:
    @staticmethod
    async def get_topics_list(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Topic]:
        """Получить список тем с количеством сообщений с предзагрузкой связанных данных"""
        result = await db.execute(
            select(Topic)
            .options(selectinload(Topic.category), selectinload(Topic.subcategory))
            .where(Topic.is_active)
            .order_by(desc(Topic.updated_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_all_topics(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Topic]:
        """Получить все темы (включая неактивные) для админ-панели с предзагрузкой связанных данных"""
        result = await db.execute(
            select(Topic)
            .options(selectinload(Topic.category), selectinload(Topic.subcategory))
            .order_by(desc(Topic.updated_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_topic_by_id(db: AsyncSession, topic_id: int) -> Optional[Topic]:
        """Получить тему по ID с предзагрузкой связанных данных"""
        result = await db.execute(
            select(Topic)
            .options(selectinload(Topic.category), selectinload(Topic.subcategory))
            .where(Topic.id == topic_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_topic(db: AsyncSession, topic: TopicCreate) -> Topic:
        """Создать новую тему"""
        db_topic = Topic(
            title=topic.title,
            description=topic.description,
            user_id=getattr(topic, "user_id", None),
            category_id=getattr(topic, "category_id", None),
            subcategory_id=getattr(topic, "subcategory_id", None),
        )
        db.add(db_topic)
        await db.commit()
        await db.refresh(db_topic)
        return db_topic

    @staticmethod
    async def update_topic(db: AsyncSession, topic_id: int, topic_data: TopicUpdate) -> Optional[Topic]:
        """Обновить тему"""
        result = await db.execute(
            update(Topic)
            .where(Topic.id == topic_id)
            .values(
                title=topic_data.title,
                description=topic_data.description,
                is_active=topic_data.is_active,
                category_id=getattr(topic_data, "category_id", None),
                subcategory_id=getattr(topic_data, "subcategory_id", None),
            )
            .returning(Topic)
        )
        await db.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_topic(db: AsyncSession, topic_id: int) -> bool:
        """Удалить тему по ID"""
        topic = await db.get(Topic, topic_id)
        if topic:
            await db.delete(topic)
            await db.commit()
            return True
        return False


class MessageApi:
    @staticmethod
    async def get_topic_messages(db: AsyncSession, topic_id: int, limit: int = 20) -> List[Message]:
        """Получить последние сообщения темы"""
        result = await db.execute(
            select(Message).where(Message.topic_id == topic_id).order_by(desc(Message.created_at)).limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # Показываем от старых к новым

    @staticmethod
    async def get_all_messages(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Message]:
        """Получить все сообщения для админ-панели"""
        result = await db.execute(select(Message).order_by(desc(Message.created_at)).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_recent_messages_with_topics(db: AsyncSession, limit: int = 10):
        """Получить последние сообщения с информацией о топиках"""
        from shared_models import Topic
        
        result = await db.execute(
            select(Message, Topic)
            .join(Topic, Message.topic_id == Topic.id)
            .order_by(desc(Message.created_at))
            .limit(limit)
        )
        
        messages_with_topics = []
        for row in result:
            message, topic = row
            messages_with_topics.append({
                'message': message,
                'topic': topic
            })
        
        return messages_with_topics

    @staticmethod
    async def create_message(db: AsyncSession, message: MessageCreate, last_message_content: str = "") -> Message:
        """Создать новое сообщение"""
        result_message = f"<div class='quote-message' style='border: 1px solid #007bff; padding-left: 20px; margin-bottom: 10px;'> {'<i>' + last_message_content[:50] + '...</i><br></div>' if last_message_content else ''}{message.content}"
        db_message = Message(
            content=result_message,
            author_name=message.author_name,
            topic_id=message.topic_id,
            parent_id=message.parent_id,
            user_id=getattr(message, "user_id", None),
        )
        db.add(db_message)

        # Обновляем время изменения темы
        await db.execute(select(Topic).where(Topic.id == db_message.topic_id))

        await db.commit()
        await db.refresh(db_message)
        return db_message

    @staticmethod
    async def get_message_by_id(db: AsyncSession, message_id: int) -> Optional[Message]:
        """Получить сообщение по ID"""
        result = await db.execute(select(Message).where(Message.id == message_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_message(db: AsyncSession, message_id: int, message_data: MessageUpdate) -> Optional[Message]:
        """Обновить сообщение"""
        result = await db.execute(
            update(Message)
            .where(Message.id == message_id)
            .values(
                content=message_data.content,
                author_name=message_data.author_name,
            )
            .returning(Message)
        )
        await db.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_message_by_id(db: AsyncSession, message_id: int) -> bool:
        """Удалить сообщение по ID"""
        message = await db.get(Message, message_id)
        if message:
            await db.delete(message)
            await db.commit()
            return True
        return False
    
    @staticmethod
    async def get_username_by_id(db: AsyncSession, user_id: int) -> Optional[str]:
        """Получить имя пользователя по ID"""
        result = await db.execute(select(User.username).where(User.id == user_id))
        return result.scalar_one_or_none()


class CategoryApi:
    @staticmethod
    async def get_categories_list(db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Category]:
        """Получить список категорий"""
        result = await db.execute(
            select(Category).order_by(Category.name).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: int) -> Optional[Category]:
        """Получить категорию по ID"""
        result = await db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_category(
        db: AsyncSession, 
        name: str, 
        description: str = "", 
        slug: str = "",
        color: str = "",
        icon: str = "",
        is_active: bool = True,
        sort_order: int = 0
    ) -> Category:
        """Создать новую категорию"""
        # Генерируем slug из названия если не указан
        if not slug:
            import re
            slug = re.sub(r'[^a-zA-Z0-9а-яё\-_]', '-', name.lower())
            slug = re.sub(r'-+', '-', slug).strip('-')
        
        db_category = Category(
            name=name, 
            description=description,
            slug=slug,
            color=color if color else None,
            icon=icon if icon else None,
            is_active=is_active,
            sort_order=sort_order
        )
        db.add(db_category)
        await db.commit()
        await db.refresh(db_category)
        return db_category

    @staticmethod
    async def update_category(
        db: AsyncSession, 
        category_id: int, 
        name: str, 
        description: str = "",
        slug: str = "",
        color: str = "",
        icon: str = "",
        is_active: bool = True,
        sort_order: int = 0
    ) -> Optional[Category]:
        """Обновить категорию"""
        # Генерируем slug из названия если не указан
        if not slug:
            import re
            slug = re.sub(r'[^a-zA-Z0-9а-яё\-_]', '-', name.lower())
            slug = re.sub(r'-+', '-', slug).strip('-')
        
        result = await db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(
                name=name, 
                description=description,
                slug=slug,
                color=color if color else None,
                icon=icon if icon else None,
                is_active=is_active,
                sort_order=sort_order
            )
            .returning(Category)
        )
        await db.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int) -> bool:
        """Удалить категорию"""
        category = await db.get(Category, category_id)
        if category:
            await db.delete(category)
            await db.commit()
            return True
        return False

    @staticmethod
    async def get_categories_with_topic_count(db: AsyncSession) -> List[dict]:
        """Получить категории с количеством топиков"""
        result = await db.execute(
            select(
                Category,
                func.count(Topic.id).label('topic_count')
            )
            .outerjoin(Topic, (Topic.category_id == Category.id) & Topic.is_active)
            .group_by(Category.id)
            .order_by(Category.name)
        )
        return [{"category": row[0], "topic_count": row[1]} for row in result.all()]


class SubcategoryApi:
    @staticmethod
    async def get_subcategories_list(db: AsyncSession, category_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> Sequence[Subcategory]:
        """Получить список подкатегорий с предзагрузкой связанных категорий"""
        query = select(Subcategory).options(selectinload(Subcategory.category)).order_by(Subcategory.name)
        if category_id:
            query = query.where(Subcategory.category_id == category_id)
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_subcategory_by_id(db: AsyncSession, subcategory_id: int) -> Optional[Subcategory]:
        """Получить подкатегорию по ID с предзагрузкой связанных данных"""
        result = await db.execute(
            select(Subcategory)
            .options(selectinload(Subcategory.category))
            .where(Subcategory.id == subcategory_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_subcategory(
        db: AsyncSession, 
        name: str, 
        category_id: int, 
        description: str = "",
        slug: str = "",
        color: str = "",
        icon: str = "",
        is_active: bool = True,
        sort_order: int = 0
    ) -> Subcategory:
        """Создать новую подкатегорию"""
        # Генерируем slug из названия если не указан
        if not slug:
            import re
            slug = re.sub(r'[^a-zA-Z0-9а-яё\-_]', '-', name.lower())
            slug = re.sub(r'-+', '-', slug).strip('-')
        
        db_subcategory = Subcategory(
            name=name, 
            category_id=category_id, 
            description=description,
            slug=slug,
            color=color if color else None,
            icon=icon if icon else None,
            is_active=is_active,
            sort_order=sort_order
        )
        db.add(db_subcategory)
        await db.commit()
        await db.refresh(db_subcategory)
        return db_subcategory

    @staticmethod
    async def update_subcategory(
        db: AsyncSession, 
        subcategory_id: int, 
        name: str, 
        category_id: int, 
        description: str = "",
        slug: str = "",
        color: str = "",
        icon: str = "",
        is_active: bool = True,
        sort_order: int = 0
    ) -> Optional[Subcategory]:
        """Обновить подкатегорию"""
        # Генерируем slug из названия если не указан
        if not slug:
            import re
            slug = re.sub(r'[^a-zA-Z0-9а-яё\-_]', '-', name.lower())
            slug = re.sub(r'-+', '-', slug).strip('-')
        
        result = await db.execute(
            update(Subcategory)
            .where(Subcategory.id == subcategory_id)
            .values(
                name=name, 
                category_id=category_id, 
                description=description,
                slug=slug,
                color=color if color else None,
                icon=icon if icon else None,
                is_active=is_active,
                sort_order=sort_order
            )
            .returning(Subcategory)
        )
        await db.commit()
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_subcategory(db: AsyncSession, subcategory_id: int) -> bool:
        """Удалить подкатегорию"""
        subcategory = await db.get(Subcategory, subcategory_id)
        if subcategory:
            await db.delete(subcategory)
            await db.commit()
            return True
        return False


# Создаем экземпляры CRUD
user_crud = UserApi()
topic_crud = TopicApi()
message_crud = MessageApi()
category_crud = CategoryApi()
subcategory_crud = SubcategoryApi()
