#!/usr/bin/env python3
"""
Простой тест для проверки работы pgvector
"""

import random

import psycopg2


def test_pgvector():
    """Тестирует основные функции pgvector"""
    
    # Подключение к базе данных
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="postgres",
        user="docker",
        password="docker"
    )
    
    try:
        cur = conn.cursor()
        
        # Создаем простой вектор размерности 1536
        test_vector = [random.random() for _ in range(1536)]
        
        # Вставляем тестовый эмбеддинг
        cur.execute("""
            INSERT INTO embeddings (content, embedding) 
            VALUES (%s, %s) 
            RETURNING id
        """, ("Тестовое сообщение pgvector", test_vector))
        
        embedding_id = cur.fetchone()[0]
        print(f"✅ Вставлен эмбеддинг с ID: {embedding_id}")
        
        # Ищем похожие эмбеддинги
        cur.execute("""
            SELECT id, content, embedding <=> %s::vector as distance 
            FROM embeddings 
            ORDER BY embedding <=> %s::vector 
            LIMIT 3
        """, (test_vector, test_vector))
        
        results = cur.fetchall()
        print(f"✅ Найдено {len(results)} записей:")
        for result in results:
            print(f"   ID: {result[0]}, Distance: {result[2]:.6f}")
            
        # Проверяем поиск по сходству (cosine similarity)
        cur.execute("""
            SELECT id, content, 1 - (embedding <=> %s::vector) as similarity
            FROM embeddings 
            WHERE 1 - (embedding <=> %s::vector) > 0.5
            ORDER BY embedding <=> %s::vector 
            LIMIT 5
        """, (test_vector, test_vector, test_vector))
        
        results = cur.fetchall()
        print(f"✅ Найдено {len(results)} записей с similarity > 0.5:")
        for result in results:
            print(f"   ID: {result[0]}, Similarity: {result[2]:.6f}")
        
        conn.commit()
        print("✅ pgvector работает корректно!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        conn.rollback()
        
    finally:
        conn.close()

if __name__ == "__main__":
    test_pgvector()
