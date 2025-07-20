from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class MessageBase(BaseModel):
    content: str
    author_name: str


class MessageCreate(MessageBase):
    topic_id: int
    parent_id: Optional[int] = None
    user_id: Optional[int] = None


class MessageUpdate(BaseModel):
    content: str
    author_name: str


class MessageResponse(MessageBase):
    id: int
    topic_id: int
    parent_id: Optional[int]
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    replies: List["MessageResponse"] = []

    class Config:
        from_attributes = True


class TopicBase(BaseModel):
    title: str
    description: Optional[str] = None


class TopicCreate(TopicBase):
    user_id: Optional[int] = None


class TopicUpdate(TopicBase):
    is_active: bool = True


class TopicResponse(TopicBase):
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class TopicWithMessages(TopicResponse):
    messages: List[MessageResponse] = []


class TopicList(TopicBase):
    id: int
    user_id: Optional[int]
    created_at: datetime
    message_count: int = 0
    is_active: bool

    class Config:
        from_attributes = True


# Обновляем forward reference
MessageResponse.model_rebuild()
