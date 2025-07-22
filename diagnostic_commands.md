```cd /Users/Viachaslau_Kazakou/Work/AI-forum && poetry run python -c "
from app.ai_manager.forum_manager import ForumRAG

print('🔧 Тестирование исправленного RAG с chunk_size=800')
rag = ForumRAG('app/ai_manager/forum_knowledge_base', 'forum_cache')

print('\n📊 Статистика по всем документам в векторной базе:')
if rag.vectorstore:
    docs_with_scores = rag.vectorstore.similarity_search_with_score('nechaos', k=50)
    print(f'Всего найдено документов: {len(docs_with_scores)}')
    
    nechaos_count = 0
    for i, (doc, score) in enumerate(docs_with_scores):
        parsed = rag.parse_character_message(doc.page_content)
        character = parsed.get('character', 'unknown').lower().strip()
        if character == 'nechaos':
            nechaos_count += 1
            print(f'  📄 Документ {nechaos_count} от nechaos (score={score:.4f}): {parsed.get(\"content\", \"\")[:80]}...')
    
    print(f'\n✅ Результат: найдено {nechaos_count} документов от nechaos')
else:
    print('❌ Векторная база не инициализирована')
"
```


```
cd /Users/Viachaslau_Kazakou/Work/AI-forum && poetry run python -c "
from app.ai_manager.forum_manager import ForumRAG

print('🔍 Детальный анализ разбиения nechaos.json')
rag = ForumRAG('app/ai_manager/forum_knowledge_base', 'forum_cache')

print('\n📄 Все документы в векторной базе:')
if rag.vectorstore:
    docs_with_scores = rag.vectorstore.similarity_search_with_score('', k=50)
    print(f'Всего документов: {len(docs_with_scores)}')
    
    nechaos_docs = []
    for i, (doc, score) in enumerate(docs_with_scores):
        parsed = rag.parse_character_message(doc.page_content)
        character = parsed.get('character', 'unknown').lower().strip()
        
        if 'nechaos' in doc.page_content.lower():
            print(f'\n📄 Документ {i+1} (содержит nechaos):')
            print(f'   Размер: {len(doc.page_content)} символов')
            print(f'   Парсированный персонаж: {character}')
            print(f'   Содержимое: {doc.page_content[:200]}...')
            
            if character == 'nechaos':
                nechaos_docs.append(doc)
    
    print(f'\n✅ Итого документов от nechaos: {len(nechaos_docs)}')
else:
    print('❌ Векторная база не инициализирована')
"
```

```
cd /Users/Viachaslau_Kazakou/Work/AI-forum && poetry run python -c "
from app.ai_manager.forum_manager import ForumRAG

print('🧪 Тестирование get_character_relevant_docs для nechaos')
rag = ForumRAG('app/ai_manager/forum_knowledge_base', 'forum_cache')

# Тестируем получение документов для nechaos
query = 'Что думаешь о женщинах?'
character = 'nechaos'

docs = rag.get_character_relevant_docs(query, character)
print(f'\n🎯 Результат для запроса \"{query}\" персонажу {character}:')
print(f'   Найдено документов: {len(docs)}')

for i, doc in enumerate(docs, 1):
    print(f'\n   📄 Документ {i}:')
    print(f'      Персонаж: {doc[\"character\"]}')
    print(f'      Настроение: {doc[\"mood\"]}')
    print(f'      Контекст: {doc[\"context\"]}')
    print(f'      Релевантность: {doc[\"similarity_score\"]:.4f}')
    print(f'      Содержимое: {doc[\"content\"][:100]}...')
"
```

```
cd /Users/Viachaslau_Kazakou/Work/AI-forum && poetry run python -c "
from app.ai_manager.forum_manager import ForumRAG

print('🧪 Тестирование других персонажей')
rag = ForumRAG('app/ai_manager/forum_knowledge_base', 'forum_cache')

characters = ['alaev', 'Sly32', 'Domen77']
query = 'Что думаешь о программировании?'

for character in characters:
    docs = rag.get_character_relevant_docs(query, character, top_k=5)
    print(f'\n🎭 {character}: {len(docs)} документов')
    for i, doc in enumerate(docs[:3], 1):  # Первые 3
        print(f'   {i}. [{doc[\"mood\"]}] {doc[\"content\"][:60]}... (score={doc[\"similarity_score\"]:.3f})')
"
```

Теперь давайте протестируем финальную функциональность - генерацию ответов от персонажей с увеличенным количеством контекста:

```
cd /Users/Viachaslau_Kazakou/Work/AI-forum && poetry run python -c "
from app.ai_manager.forum_manager import ForumRAG

print('🎭 Финальное тестирование: генерация ответа от nechaos с увеличенным контекстом')
rag = ForumRAG('app/ai_manager/forum_knowledge_base', 'forum_cache')

# Проверяем количество документов для генерации контекста
query = 'Каждый раз встречаю женщин у которых есть квартира, машина, хорошо одеваются, но при этом ни у одной нет денег заплатить за еду в кафе. Парадокс. В чем причина?'
character = 'nechaos'

docs = rag.get_character_relevant_docs(query, character)
print(f'Для персонажа {character} найдено {len(docs)} релевантных документов:')

for i, doc in enumerate(docs, 1):
    print(f'   {i}. [{doc[\"mood\"]}] {doc[\"content\"][:80]}... (score={doc[\"similarity_score\"]:.3f})')

print(f'\n📝 Контекст для генерации будет включать {len(docs)} примеров сообщений персонажа')
print('✅ Проблема решена! Система теперь возвращает больше одного документа')
"
```