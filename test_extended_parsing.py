#!/usr/bin/env python3
"""
Тестирование расширенного парсинга JSON массивов
"""

from app.ai_manager.forum_manager import ForumRAG

def test_extended_parsing():
    print("🧪 Тестирование расширенного парсинга JSON массивов")
    
    # Создаем экземпляр ForumRAG
    rag = ForumRAG('app/ai_manager/forum_knowledge_base', 'forum_cache')
    
    print("\n1️⃣ Тестирование стандартного парсинга (текущий метод)")
    docs_standard = rag.get_character_relevant_docs("Что думаешь о женщинах?", "Domen77")
    print(f"   Стандартный метод: {len(docs_standard)} документов для Domen77")
    for i, doc in enumerate(docs_standard, 1):
        print(f"   {i}. [{doc['mood']}] {doc['content'][:80]}... (score={doc['similarity_score']:.3f})")
    
    print("\n2️⃣ Настройка RAG с расширенным парсингом...")
    rag.setup_rag_with_extended_parsing()
    
    print("\n3️⃣ Тестирование расширенного парсинга")
    docs_extended = rag.get_character_relevant_docs_extended("Что думаешь о женщинах?", "Domen77")
    print(f"   Расширенный метод: {len(docs_extended)} документов для Domen77")
    
    for i, doc in enumerate(docs_extended, 1):
        print(f"   {i}. [{doc['mood']}] Thread: '{doc.get('thread_id', 'N/A')}' | Reply to: '{doc.get('reply_to', 'N/A')}'")
        print(f"      Context: {doc.get('context', 'general')}")
        print(f"      Content: {doc['content'][:100]}...")
        print(f"      Score: {doc['similarity_score']:.3f} | Method: {doc.get('extraction_method', 'standard')}")
        print()
    
    print("\n4️⃣ Сравнение результатов:")
    print(f"   📊 Стандартный метод: {len(docs_standard)} документов")
    print(f"   📊 Расширенный метод: {len(docs_extended)} документов")
    print(f"   📈 Улучшение: {len(docs_extended) - len(docs_standard)} дополнительных документов")
    
    print("\n5️⃣ Тестирование nechaos (проблемный персонаж)")
    docs_nechaos = rag.get_character_relevant_docs_extended("Что думаешь о женщинах?", "nechaos")
    print(f"   nechaos (расширенный): {len(docs_nechaos)} документов")
    
    for i, doc in enumerate(docs_nechaos, 1):
        print(f"   {i}. Thread: '{doc.get('thread_id', 'N/A')}' | Context: '{doc.get('context', 'general')}'")
        print(f"      Content: {doc['content'][:100]}...")
        print(f"      Score: {doc['similarity_score']:.3f}")
        print()

if __name__ == "__main__":
    test_extended_parsing()
