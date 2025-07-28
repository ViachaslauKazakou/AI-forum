#!/usr/bin/env python3
"""
Тестирование RAG Manager API
"""
import asyncio
import json
import time
from typing import Any, Dict

import httpx


class RAGManagerTester:
    """Класс для тестирования RAG Manager API"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.client = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def test_health(self) -> Dict[str, Any]:
        """Тест health check"""
        print("🏥 Testing health check...")
        
        try:
            response = await self.client.get("/api/v1/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                print(f"   Database: {data['database_status']}")
                print(f"   Vector DB: {data['vector_db_status']}")
                print(f"   Knowledge Base: {data['knowledge_base_status']}")
                print(f"   Uptime: {data['uptime']:.1f}s")
                return data
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return {"status": "failed", "error": response.text}
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_ready(self) -> Dict[str, Any]:
        """Тест ready check"""
        print("\n🚀 Testing ready check...")
        
        try:
            response = await self.client.get("/ready")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Ready check passed: {data['status']}")
                print(f"   Available users: {data.get('available_users', 'unknown')}")
                return data
            else:
                print(f"❌ Ready check failed: {response.status_code}")
                return {"status": "failed", "error": response.text}
        except Exception as e:
            print(f"❌ Ready check error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_list_users(self) -> list[str]:
        """Тест получения списка пользователей"""
        print("\n👥 Testing list users...")
        
        try:
            response = await self.client.get("/api/v1/users")
            if response.status_code == 200:
                users = response.json()
                print(f"✅ Found {len(users)} users: {users}")
                return users
            else:
                print(f"❌ List users failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ List users error: {e}")
            return []
    
    async def test_user_knowledge(self, user_id: str) -> Dict[str, Any]:
        """Тест получения знаний пользователя"""
        print(f"\n🧠 Testing user knowledge for {user_id}...")
        
        try:
            response = await self.client.get(f"/api/v1/users/{user_id}/knowledge")
            if response.status_code == 200:
                knowledge = response.json()
                print(f"✅ User knowledge loaded:")
                print(f"   Role: {knowledge['role']}")
                print(f"   Experience: {knowledge['experience_level']}")
                print(f"   Expertise: {knowledge['expertise'][:3]}...")  # Первые 3
                return knowledge
            else:
                print(f"❌ User knowledge failed: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ User knowledge error: {e}")
            return {}
    
    async def test_rag_process(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Тест обработки RAG запроса"""
        print(f"\n🤖 Testing RAG process...")
        print(f"   Topic: {request_data['topic']}")
        print(f"   User: {request_data['user_id']}")
        print(f"   Question: {request_data['question'][:50]}...")
        
        start_time = time.time()
        
        try:
            response = await self.client.post("/api/v1/rag/process", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                process_time = time.time() - start_time
                
                print(f"✅ RAG process completed in {process_time:.3f}s")
                print(f"   Enhanced prompt length: {len(data['enhanced_prompt'])} chars")
                print(f"   Context items: {len(data['context_items'])}")
                print(f"   User persona: {data['user_persona'].get('role', 'Unknown')}")
                print(f"   Processing time: {data['processing_time']:.3f}s")
                
                # Показываем часть промпта
                prompt_preview = data['enhanced_prompt'][:200] + "..." if len(data['enhanced_prompt']) > 200 else data['enhanced_prompt']
                print(f"   Prompt preview: {prompt_preview}")
                
                return data
            else:
                print(f"❌ RAG process failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {"status": "failed", "error": response.text}
                
        except Exception as e:
            print(f"❌ RAG process error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_stats(self) -> Dict[str, Any]:
        """Тест получения статистики"""
        print("\n📊 Testing stats...")
        
        try:
            response = await self.client.get("/api/v1/stats")
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Stats retrieved:")
                print(f"   Uptime: {stats['uptime_seconds']:.1f}s")
                print(f"   Available users: {stats['available_users']}")
                print(f"   Database stats: {stats['database_stats']}")
                return stats
            else:
                print(f"❌ Stats failed: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Stats error: {e}")
            return {}
    
    async def run_comprehensive_test(self):
        """Запуск всех тестов"""
        print("🧪 Starting comprehensive RAG Manager API test\n")
        print("=" * 60)
        
        # Базовые проверки
        await self.test_health()
        await self.test_ready()
        
        # Пользователи
        users = await self.test_list_users()
        
        if users:
            # Тестируем знания первого пользователя
            await self.test_user_knowledge(users[0])
        
        # Статистика
        await self.test_stats()
        
        # RAG запросы
        test_requests = [
            {
                "topic": "Machine Learning Fundamentals",
                "user_id": "alice_researcher",
                "question": "What are the key differences between supervised and unsupervised learning?",
                "reply_to": None
            },
            {
                "topic": "Python Development",
                "user_id": "bob_developer", 
                "question": "How can I optimize my Python code for better performance?",
                "reply_to": None
            },
            {
                "topic": "AI Basics",
                "user_id": "charlie_student",
                "question": "I'm new to AI. Where should I start learning?",
                "reply_to": None
            }
        ]
        
        for i, request_data in enumerate(test_requests, 1):
            print(f"\n--- RAG Test {i}/{len(test_requests)} ---")
            await self.test_rag_process(request_data)
        
        print("\n" + "=" * 60)
        print("🎉 Comprehensive test completed!")


async def main():
    """Основная функция"""
    print("RAG Manager API Tester")
    print("=====================")
    
    # Проверяем, запущен ли сервис
    async with RAGManagerTester() as tester:
        try:
            # Проверяем доступность сервиса
            response = await tester.client.get("/")
            if response.status_code == 200:
                print("🟢 RAG Manager service is running")
                data = response.json()
                print(f"   Service: {data['service']}")
                print(f"   Version: {data['version']}")
                print(f"   Status: {data['status']}")
            else:
                print("🔴 RAG Manager service not responding correctly")
                return
        except Exception as e:
            print(f"🔴 Cannot connect to RAG Manager service: {e}")
            print("   Make sure the service is running on http://localhost:8001")
            return
        
        # Запускаем полный тест
        await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())
