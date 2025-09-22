#!/usr/bin/env python3
"""
Test Fixed Endpoints
===================

Tests the 3 previously failing endpoints to verify they are now working.
"""

import requests
import json

def test_fixes():
    """Test all the fixes"""
    print('🧪 TESTING FIXED ENDPOINTS...')
    print('=' * 50)
    
    # Test 1: Create session and test GET session endpoint
    print('\n1️⃣ Testing Session Management...')
    session_resp = requests.post('http://localhost:8000/api/v1/sessions', 
                                json={'user_id': 'test_user', 'user_type': 'common_person'})
    
    if session_resp.status_code == 200:
        session_id = session_resp.json()['session_id']
        print(f'✅ Session created: {session_id[:8]}...')
        
        # Test GET session (previously failing)
        get_resp = requests.get(f'http://localhost:8000/api/v1/sessions/{session_id}')
        if get_resp.status_code == 200:
            print(f'✅ GET Session: {get_resp.status_code} - FIXED! ✨')
            session_data = get_resp.json()
            print(f'   📋 Session data: user_id={session_data.get("user_id")}, status={session_data.get("status")}')
        else:
            print(f'❌ GET Session: {get_resp.status_code} - STILL FAILING')
    else:
        print('❌ Failed to create session')
        return False
    
    # Test 2: Analytics endpoint (previously 500 error)
    print('\n2️⃣ Testing Analytics...')
    analytics_resp = requests.post('http://localhost:8000/api/v1/analytics/summary', json={})
    if analytics_resp.status_code == 200:
        print(f'✅ Analytics: {analytics_resp.status_code} - FIXED! ✨')
        analytics_data = analytics_resp.json()
        print(f'   📊 Total sessions: {analytics_data.get("total_sessions", 0)}')
        print(f'   📈 Total queries: {analytics_data.get("total_queries", 0)}')
    else:
        print(f'❌ Analytics: {analytics_resp.status_code} - STILL FAILING')
    
    # Test 3: Feedback with test interaction (previously 404)
    print('\n3️⃣ Testing Feedback...')
    feedback_resp = requests.post('http://localhost:8000/api/v1/feedback', json={
        'session_id': session_id,
        'interaction_id': 'test-interaction-123',
        'feedback': 'upvote',
        'time_spent': 30.0
    })
    if feedback_resp.status_code == 200:
        print(f'✅ Feedback: {feedback_resp.status_code} - FIXED! ✨')
        feedback_data = feedback_resp.json()
        print(f'   🎯 Reward: {feedback_data.get("reward", 0.0)}')
        print(f'   😊 Satisfaction: {feedback_data.get("updated_satisfaction", 0.0)}')
    else:
        print(f'❌ Feedback: {feedback_resp.status_code} - STILL FAILING')
    
    # Test 4: Constitutional articles count (expanded database)
    print('\n4️⃣ Testing Expanded Constitutional Database...')
    const_resp = requests.post('http://localhost:8000/api/v1/constitutional/search', 
                              json={'query': 'equality', 'limit': 10})
    if const_resp.status_code == 200:
        articles = const_resp.json().get('articles', [])
        print(f'✅ Constitutional Search: {const_resp.status_code} - WORKING! ✨')
        print(f'   📜 Articles found: {len(articles)}')
        if articles:
            print(f'   📋 Sample: Article {articles[0].get("article_number")} - {articles[0].get("title", "")[:50]}...')
    else:
        print(f'❌ Constitutional Search: {const_resp.status_code} - FAILING')
    
    # Test 5: Enhanced features status
    print('\n5️⃣ Testing Enhanced Features...')
    features_resp = requests.get('http://localhost:8000/api/v1/system/enhanced-features')
    if features_resp.status_code == 200:
        features_data = features_resp.json()
        print(f'✅ Enhanced Features: {features_resp.status_code} - WORKING! ✨')
        print(f'   🤖 ML Classification: {features_data.get("enhanced_classification", False)}')
        print(f'   🏛️ Constitutional Support: {features_data.get("constitutional_support", False)}')
        const_stats = features_data.get("constitutional_stats", {})
        print(f'   📜 Total Articles: {const_stats.get("total_articles", 0)}')
    else:
        print(f'❌ Enhanced Features: {features_resp.status_code} - FAILING')
    
    print('\n' + '=' * 50)
    print('🎉 ENDPOINT FIXES TEST COMPLETE!')
    print('✨ All previously failing endpoints should now be working!')

if __name__ == "__main__":
    test_fixes()
