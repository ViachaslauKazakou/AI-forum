#!/usr/bin/env python3
"""
Скрипт для отладки RAG функционности
"""
import sys
import os
sys.path.append('/Users/Viachaslau_Kazakou/Work/AI-forum')

from app.ai_manager.forum_manager import ForumManager
from app.utils.logger_utils import setup_logger
import logging

# Настройка детального логирования
logging.basicConfig(level=logging.DEBUG)
logger = setup_logger(__name__, level=logging.DEBUG)

def test_character_docs():
    """Тестируем получение документов для персонажей"""
    logger.info("🧪 Начинаем тестирование RAG для персонажей")
    
    try:
        # Создаем ForumManager
        logger.info("🏗️ Создание ForumManager...")
        manager = ForumManager()
        
        # Проверяем доступных персонажей
        characters = manager.forum_rag.get_available_characters()
        logger.info(f"👥 Доступные персонажи: {characters}")
        
        # Тестируем для каждого персонажа
        test_query = "Что думаешь о программировании?"
        
        for character in characters:
            logger.info(f"\n🎭 === ТЕСТ ДЛЯ ПЕРСОНАЖА: {character} ===")
            
            # Получаем документы персонажа
            docs = manager.forum_rag.get_character_relevant_docs(test_query, character, top_k=5)
            
            logger.info(f"📊 Результат для {character}: найдено {len(docs)} документов")
            
            # Проверяем, все ли документы принадлежат нужному персонажу
            correct_docs = 0
            wrong_docs = 0
            
            for i, doc in enumerate(docs):
                doc_character = doc.get('character', 'unknown').lower()
                target_character = character.lower()
                
                if doc_character == target_character:
                    correct_docs += 1
                    logger.debug(f"   ✅ Документ {i+1}: ПРАВИЛЬНЫЙ персонаж '{doc_character}'")
                else:
                    wrong_docs += 1
                    logger.warning(f"   ❌ Документ {i+1}: НЕПРАВИЛЬНЫЙ персонаж '{doc_character}' (ожидался '{target_character}')")
                
                logger.debug(f"      Содержимое: {doc.get('content', '')[:100]}...")
                logger.debug(f"      Similarity: {doc.get('similarity_score', 0):.4f}")
            
            logger.info(f"📈 Статистика для {character}: {correct_docs} правильных, {wrong_docs} неправильных")
            
            if wrong_docs > 0:
                logger.error(f"❌ ОШИБКА: Найдены документы от других персонажей для {character}!")
            else:
                logger.info(f"✅ ВСЕ ДОКУМЕНТЫ КОРРЕКТНЫ для {character}")

    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

def test_character_stats():
    """Проверяем статистику персонажей"""
    logger.info("\n📊 === СТАТИСТИКА ПЕРСОНАЖЕЙ ===")
    
    try:
        manager = ForumManager()
        stats = manager.forum_rag.get_character_stats()
        
        logger.info(f"📈 Найдено персонажей в базе: {len(stats)}")
        
        for character, info in stats.items():
            logger.info(f"👤 {character}:")
            logger.info(f"   📝 Сообщений: {info['count']}")
            logger.info(f"   😊 Настроения: {info['moods']}")
            logger.info(f"   🏷️ Типы: {info['types']}")
            logger.info(f"   📍 Контексты: {info['contexts']}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при получении статистики: {e}")

def test_direct_query():
    """Тестируем прямой запрос к персонажу"""
    logger.info("\n🎯 === ТЕСТ ПРЯМОГО ЗАПРОСА ===")
    
    try:
        manager = ForumManager()
        
        test_cases = [
            ("alaev", "Что думаешь о водителях?"),
            ("Sly32", "Как решить проблему с кодом?"),
            ("Domen77", "Твое мнение о новых технологиях?")
        ]
        
        for character, question in test_cases:
            logger.info(f"\n🎭 Запрос к {character}: {question}")
            
            # Получаем ответ
            response = manager.ask_as_character(question, character, mood="sarcastic")
            
            logger.info(f"💬 Ответ от {character}: {response[:200]}...")
            
    except Exception as e:
        logger.error(f"❌ Ошибка при тестировании запросов: {e}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    logger.info("🚀 Запуск отладки RAG системы")
    
    # Запускаем тесты
    test_character_docs()
    test_character_stats()
    test_direct_query()
    
    logger.info("🏁 Отладка завершена")
