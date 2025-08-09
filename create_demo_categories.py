#!/usr/bin/env python3
"""
Скрипт для создания демонстрационных категорий и подкатегорий
"""
import asyncio
from app.database import async_session_maker
from app.managers.db_manager import category_crud, subcategory_crud


async def create_demo_categories():
    """Создает демонстрационные категории и подкатегории"""
    
    async with async_session_maker() as db:
        # Создаем основные категории
        print("Создаем категории...")
        
        general_category = await category_crud.create_category(
            db, 
            "Общие вопросы", 
            "Общие вопросы и обсуждения"
        )
        print(f"✓ Создана категория: {general_category.name}")
        
        tech_category = await category_crud.create_category(
            db, 
            "Технологии", 
            "Обсуждение технологий, программирования и разработки"
        )
        print(f"✓ Создана категория: {tech_category.name}")
        
        news_category = await category_crud.create_category(
            db, 
            "Новости", 
            "Новости и события в мире IT"
        )
        print(f"✓ Создана категория: {news_category.name}")
        
        help_category = await category_crud.create_category(
            db, 
            "Помощь", 
            "Помощь и поддержка пользователей"
        )
        print(f"✓ Создана категория: {help_category.name}")
        
        # Создаем подкатегории для "Технологии"
        print("\nСоздаем подкатегории для 'Технологии'...")
        
        await subcategory_crud.create_subcategory(
            db, 
            "Python", 
            tech_category.id, 
            "Обсуждение языка программирования Python"
        )
        print("✓ Создана подкатегория: Python")
        
        await subcategory_crud.create_subcategory(
            db, 
            "JavaScript", 
            tech_category.id, 
            "Обсуждение JavaScript и веб-разработки"
        )
        print("✓ Создана подкатегория: JavaScript")
        
        await subcategory_crud.create_subcategory(
            db, 
            "DevOps", 
            tech_category.id, 
            "DevOps, CI/CD, контейнеризация"
        )
        print("✓ Создана подкатегория: DevOps")
        
        await subcategory_crud.create_subcategory(
            db, 
            "Базы данных", 
            tech_category.id, 
            "PostgreSQL, MongoDB, Redis и другие БД"
        )
        print("✓ Создана подкатегория: Базы данных")
        
        # Создаем подкатегории для "Общие вопросы"
        print("\nСоздаем подкатегории для 'Общие вопросы'...")
        
        await subcategory_crud.create_subcategory(
            db, 
            "Знакомство", 
            general_category.id, 
            "Представьтесь участникам форума"
        )
        print("✓ Создана подкатегория: Знакомство")
        
        await subcategory_crud.create_subcategory(
            db, 
            "Флейм", 
            general_category.id, 
            "Общие обсуждения и дискуссии"
        )
        print("✓ Создана подкатегория: Флейм")
        
        # Создаем подкатегории для "Помощь"
        print("\nСоздаем подкатегории для 'Помощь'...")
        
        await subcategory_crud.create_subcategory(
            db, 
            "Техническая поддержка", 
            help_category.id, 
            "Проблемы с работой форума"
        )
        print("✓ Создана подкатегория: Техническая поддержка")
        
        await subcategory_crud.create_subcategory(
            db, 
            "Вопросы новичков", 
            help_category.id, 
            "Вопросы от начинающих пользователей"
        )
        print("✓ Создана подкатегория: Вопросы новичков")
        
        print("\n🎉 Демонстрационные категории и подкатегории созданы!")
        print("\nТеперь вы можете:")
        print("1. Зайти в админку: http://localhost:8000/admin/categories")
        print("2. Создать топик с категорией: http://localhost:8000/create-topic")
        print("3. Посмотреть главную страницу: http://localhost:8000/")


if __name__ == "__main__":
    asyncio.run(create_demo_categories())
