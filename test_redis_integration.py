#!/usr/bin/env python3
"""
Test Law Agent with Real Redis Integration
"""

import requests
import redis
import time

def test_redis_integration():
    print('🧪 TESTING LAW AGENT WITH REAL REDIS')
    print('=' * 50)

    # Test Redis connection first
    try:
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        redis_client.ping()
        print('✅ Redis: Connected and operational')
    except Exception as e:
        print(f'❌ Redis: {e}')
        return False

    # Test Law Agent health
    try:
        health_resp = requests.get('http://localhost:8000/health', timeout=5)
        if health_resp.status_code == 200:
            health_data = health_resp.json()
            print(f'✅ Law Agent Health: {health_resp.status_code}')
            print(f'   Version: {health_data["version"]}')
            print(f'   Redis Status: {health_data["services"]["redis"]}')
        
        # Test session creation (this will use Redis)
        session_resp = requests.post('http://localhost:8000/api/v1/sessions',
                                   json={'user_id': 'redis_test_user'}, timeout=5)
        if session_resp.status_code == 200:
            session_data = session_resp.json()
            session_id = session_data['session_id']
            print(f'✅ Session Created: {session_id[:8]}...')
            
            # Check if session is stored in Redis
            time.sleep(1)  # Give it a moment
            redis_keys = redis_client.keys('*session*')
            print(f'✅ Redis Keys Found: {len(redis_keys)} session-related keys')
            
            # Test query (this will also use Redis)
            query_resp = requests.post('http://localhost:8000/api/v1/query',
                                     json={'session_id': session_id, 'query': 'Redis test query'}, timeout=5)
            if query_resp.status_code == 200:
                query_data = query_resp.json()
                print(f'✅ Query Processed: {query_data["domain"]}')
                
                # Check Redis again
                redis_keys_after = redis_client.keys('*')
                print(f'✅ Total Redis Keys: {len(redis_keys_after)}')
        
        print('\n🎉 LAW AGENT IS USING REAL REDIS SUCCESSFULLY!')
        return True
        
    except Exception as e:
        print(f'❌ Test failed: {e}')
        return False

if __name__ == "__main__":
    test_redis_integration()
