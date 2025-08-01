#!/usr/bin/env python3
"""
Test Redis Connection for Law Agent
"""

import redis
import time

def test_redis():
    print('🧪 TESTING REDIS CONNECTION')
    print('=' * 40)

    try:
        # Wait a moment for Redis to fully start
        time.sleep(2)
        
        # Connect to Redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Test connection
        response = client.ping()
        print(f'✅ Redis Ping: {response}')
        
        # Test basic operations
        client.set('law_agent_test', 'Redis is working!')
        value = client.get('law_agent_test')
        print(f'✅ Set/Get Test: {value}')
        
        # Test hash operations (used by Law Agent)
        client.hset('session_test', 'user_id', 'test_user')
        client.hset('session_test', 'created_at', '2025-08-01')
        session_data = client.hgetall('session_test')
        print(f'✅ Hash Test: {session_data}')
        
        # Clean up test data
        client.delete('law_agent_test', 'session_test')
        
        # Get Redis info
        info = client.info()
        print(f'✅ Redis Version: {info["redis_version"]}')
        print(f'✅ Connected Clients: {info["connected_clients"]}')
        print(f'✅ Used Memory: {info["used_memory_human"]}')
        
        print('\n🎉 REDIS IS FULLY OPERATIONAL!')
        return True
        
    except Exception as e:
        print(f'❌ Redis connection failed: {e}')
        return False

if __name__ == "__main__":
    test_redis()
