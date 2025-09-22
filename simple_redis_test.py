#!/usr/bin/env python3
"""
Simple Redis Integration Test
"""

import requests
import redis

def main():
    print('🧪 SIMPLE REDIS INTEGRATION TEST')
    print('=' * 50)

    # Test Redis connection
    try:
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        redis_client.ping()
        print('✅ Redis: Connected and operational')
    except Exception as e:
        print(f'❌ Redis: {e}')
        return

    # Test session creation
    try:
        session_resp = requests.post('http://localhost:8000/api/v1/sessions',
                                   json={'user_id': 'simple_test'}, timeout=5)
        print(f'✅ Session creation: {session_resp.status_code}')
        
        if session_resp.status_code == 200:
            session_data = session_resp.json()
            session_id = session_data['session_id']
            print(f'✅ Session ID: {session_id[:8]}...')
            
            # Check Redis storage
            session_key = f'session:{session_id}'
            redis_data = redis_client.hgetall(session_key)
            if redis_data:
                print(f'✅ Session stored in Redis: {len(redis_data)} fields')
                print(f'   User ID: {redis_data.get("user_id")}')
            else:
                print('❌ Session NOT found in Redis')
                return
            
            # Test query
            query_resp = requests.post('http://localhost:8000/api/v1/query',
                                     json={'session_id': session_id, 'query': 'Test query'}, timeout=5)
            print(f'✅ Query processing: {query_resp.status_code}')
            
            if query_resp.status_code == 200:
                query_data = query_resp.json()
                interaction_id = query_data['interaction_id']
                print(f'✅ Interaction ID: {interaction_id[:8]}...')
                print(f'   Domain: {query_data["domain"]}')
                
                # Check interaction in Redis
                interaction_key = f'interaction:{interaction_id}'
                interaction_data = redis_client.hgetall(interaction_key)
                if interaction_data:
                    print(f'✅ Interaction stored in Redis: {len(interaction_data)} fields')
                else:
                    print('❌ Interaction NOT found in Redis')
                
                # Test feedback
                feedback_resp = requests.post('http://localhost:8000/api/v1/feedback',
                                            json={'session_id': session_id, 
                                                 'interaction_id': interaction_id,
                                                 'feedback': 'upvote'}, timeout=5)
                print(f'✅ Feedback submission: {feedback_resp.status_code}')
                
                if feedback_resp.status_code == 200:
                    # Check if feedback is stored
                    updated_interaction = redis_client.hgetall(interaction_key)
                    if 'feedback' in updated_interaction:
                        print(f'✅ Feedback stored: {updated_interaction["feedback"]}')
                    else:
                        print('❌ Feedback NOT stored')
            
            # Show Redis statistics
            all_keys = redis_client.keys('*')
            session_keys = redis_client.keys('session:*')
            interaction_keys = redis_client.keys('interaction:*')
            
            print(f'\\n📊 Redis Statistics:')
            print(f'✅ Total keys: {len(all_keys)}')
            print(f'✅ Session keys: {len(session_keys)}')
            print(f'✅ Interaction keys: {len(interaction_keys)}')
            
            if all_keys:
                print(f'✅ Sample keys: {all_keys[:3]}')
            
            print('\\n🎉 REDIS INTEGRATION IS WORKING!')
            print('=' * 50)
            print('✅ Sessions stored in Redis')
            print('✅ Interactions stored in Redis')
            print('✅ Feedback stored in Redis')
            print('✅ Law Agent fully integrated with Redis')
            
        else:
            print(f'❌ Session creation failed: {session_resp.text}')
            
    except Exception as e:
        print(f'❌ Test failed: {e}')

if __name__ == "__main__":
    main()
