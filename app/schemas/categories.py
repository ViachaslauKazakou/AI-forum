from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TopicCreateWithCategories(BaseModel):
    """Схема для создания топика с поддержкой категорий"""
    title: str = Field(..., max_length=200, description="Название темы")
    description: Optional[str] = Field(None, description="Описание темы")
    user_id: Optional[int] = Field(None, description="ID пользователя-автора")
    category_id: Optional[int] = Field(None, description="ID категории")
    subcategory_id: Optional[int] = Field(None, description="ID подкатегории")


class TopicUpdateWithCategories(BaseModel):
    """Схема для обновления топика с поддержкой категорий"""
    title: str = Field(..., max_length=200, description="Название темы")
    description: Optional[str] = Field(None, description="Описание темы")
    is_active: bool = Field(True, description="Активность темы")
    category_id: Optional[int] = Field(None, description="ID категории")
    subcategory_id: Optional[int] = Field(None, description="ID подкатегории")


class CategoryBase(BaseModel):
    """Базовая схема категории"""
    name: str = Field(..., max_length=100, description="Название категории")
    description: Optional[str] = Field(None, description="Описание категории")


class CategoryCreate(CategoryBase):
    """Схема создания категории"""
    pass


class CategoryResponse(CategoryBase):
    """Схема ответа категории"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubcategoryBase(BaseModel):
    """Базовая схема подкатегории"""
    name: str = Field(..., max_length=100, description="Название подкатегории")
    description: Optional[str] = Field(None, description="Описание подкатегории")
    category_id: int = Field(..., description="ID родительской категории")


class SubcategoryCreate(SubcategoryBase):
    """Схема создания подкатегории"""
    pass


class SubcategoryResponse(SubcategoryBase):
    """Схема ответа подкатегории"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
