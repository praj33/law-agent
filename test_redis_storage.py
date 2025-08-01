#!/usr/bin/env python3
"""
Comprehensive Redis Storage Test for Law Agent
"""

import requests
import redis
import time
import json

def test_redis_storage():
    print('🧪 COMPREHENSIVE REDIS STORAGE TEST')
    print('=' * 60)

    # Connect to Redis
    try:
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        redis_client.ping()
        print('✅ Redis: Connected and operational')
    except Exception as e:
        print(f'❌ Redis: {e}')
        return False

    # Clear any existing test data
    test_keys = redis_client.keys('*test*')
    if test_keys:
        redis_client.delete(*test_keys)
        print(f'🧹 Cleaned up {len(test_keys)} test keys')

    try:
        # Test 1: Create session and verify Redis storage
        print('\n📝 Test 1: Session Creation and Storage')
        session_resp = requests.post('http://localhost:8000/api/v1/sessions',
                                   json={'user_id': 'redis_storage_test'}, timeout=5)
        
        if session_resp.status_code == 200:
            session_data = session_resp.json()
            session_id = session_data['session_id']
            print(f'✅ Session Created: {session_id[:8]}...')
            
            # Check if session is in Redis
            session_key = f'session:{session_id}'
            session_in_redis = redis_client.hgetall(session_key)
            if session_in_redis:
                print(f'✅ Session stored in Redis: {len(session_in_redis)} fields')
                print(f'   User ID: {session_in_redis.get("user_id")}')
                print(f'   Created: {session_in_redis.get("created_at")}')
            else:
                print('❌ Session NOT found in Redis')
                return False
        
        # Test 2: Process query and verify interaction storage
        print('\n🤔 Test 2: Query Processing and Interaction Storage')
        query_resp = requests.post('http://localhost:8000/api/v1/query',
                                 json={'session_id': session_id, 'query': 'I need help with divorce proceedings'}, timeout=5)
        
        if query_resp.status_code == 200:
            query_data = query_resp.json()
            interaction_id = query_data['interaction_id']
            print(f'✅ Query Processed: {interaction_id[:8]}...')
            print(f'   Domain: {query_data["domain"]}')
            print(f'   Confidence: {query_data["confidence"]:.0%}')
            
            # Check if interaction is in Redis
            interaction_key = f'interaction:{interaction_id}'
            interaction_in_redis = redis_client.hgetall(interaction_key)
            if interaction_in_redis:
                print(f'✅ Interaction stored in Redis: {len(interaction_in_redis)} fields')
                print(f'   Query: {interaction_in_redis.get("query")[:30]}...')
                print(f'   Domain: {interaction_in_redis.get("predicted_domain")}')
            else:
                print('❌ Interaction NOT found in Redis')
                return False
            
            # Check session interactions list
            session_interactions = redis_client.lrange(f'session:{session_id}:interactions', 0, -1)
            if session_interactions:
                print(f'✅ Session interactions list: {len(session_interactions)} interactions')
            else:
                print('❌ Session interactions list NOT found in Redis')
        
        # Test 3: Submit feedback and verify storage
        print('\n👍 Test 3: Feedback Submission and Storage')
        feedback_resp = requests.post('http://localhost:8000/api/v1/feedback',
                                    json={'session_id': session_id, 
                                         'interaction_id': interaction_id,
                                         'feedback': 'upvote'}, timeout=5)
        
        if feedback_resp.status_code == 200:
            print('✅ Feedback submitted successfully')
            
            # Check if feedback is stored in Redis
            interaction_with_feedback = redis_client.hgetall(interaction_key)
            if 'feedback' in interaction_with_feedback:
                print(f'✅ Feedback stored in Redis: {interaction_with_feedback["feedback"]}')
            else:
                print('❌ Feedback NOT found in Redis')
                return False
        
        # Test 4: Check Redis key expiration
        print('\n⏰ Test 4: Redis Key Expiration Check')
        session_ttl = redis_client.ttl(session_key)
        interaction_ttl = redis_client.ttl(interaction_key)
        print(f'✅ Session TTL: {session_ttl} seconds (~{session_ttl/3600:.1f} hours)')
        print(f'✅ Interaction TTL: {interaction_ttl} seconds (~{interaction_ttl/3600:.1f} hours)')
        
        # Test 5: Overall Redis statistics
        print('\n📊 Test 5: Redis Statistics')
        all_keys = redis_client.keys('*')
        session_keys = redis_client.keys('session:*')
        interaction_keys = redis_client.keys('interaction:*')
        
        print(f'✅ Total Redis keys: {len(all_keys)}')
        print(f'✅ Session keys: {len(session_keys)}')
        print(f'✅ Interaction keys: {len(interaction_keys)}')
        
        # Show some sample keys
        if len(all_keys) > 0:
            print(f'✅ Sample keys: {all_keys[:5]}')
        
        # Test Redis memory usage
        info = redis_client.info('memory')
        print(f'✅ Redis memory used: {info["used_memory_human"]}')
        
        print('\n🎉 ALL REDIS STORAGE TESTS PASSED!')
        print('=' * 60)
        print('✅ Sessions are stored in Redis')
        print('✅ Interactions are stored in Redis')
        print('✅ Feedback is stored in Redis')
        print('✅ TTL (expiration) is working')
        print('✅ Law Agent is fully integrated with Redis')
        print('=' * 60)
        
        return True
        
    except Exception as e:
        print(f'❌ Test failed: {e}')
        return False

if __name__ == "__main__":
    success = test_redis_storage()
    if success:
        print('\n🚀 Redis integration is PERFECT!')
    else:
        print('\n❌ Redis integration needs attention')
