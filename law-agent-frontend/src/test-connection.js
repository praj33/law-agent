// Simple test to verify the connection to the backend
async function testConnection() {
  console.log('Testing connection to backend...');
  
  try {
    // Test the direct endpoint first
    console.log('Testing /api/ultimate-analysis endpoint...');
    const response1 = await fetch('/api/ultimate-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: 'What are my rights in a contract dispute?'
      })
    });
    
    console.log('Direct endpoint status:', response1.status);
    
    if (response1.ok) {
      const data1 = await response1.json();
      console.log('Direct endpoint success:', data1);
      return;
    }
    
    // If direct endpoint fails, try the v1 endpoint
    console.log('Testing /api/v1/query endpoint...');
    
    // First create a session
    const sessionResponse = await fetch('/api/v1/sessions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: 'test_user_' + Date.now(),
        user_type: 'common_person'
      })
    });
    
    console.log('Session creation status:', sessionResponse.status);
    
    let sessionId = null;
    if (sessionResponse.ok) {
      const sessionData = await sessionResponse.json();
      sessionId = sessionData.session_id;
      console.log('Session created:', sessionId);
    }
    
    // Now test the query endpoint
    const queryData = {
      query: 'What are my rights in a contract dispute?',
      interaction_type: 'query'
    };
    
    if (sessionId) {
      queryData.session_id = sessionId;
    }
    
    const response2 = await fetch('/api/v1/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(queryData)
    });
    
    console.log('V1 endpoint status:', response2.status);
    
    if (response2.ok) {
      const data2 = await response2.json();
      console.log('V1 endpoint success:', data2);
    } else {
      const errorText = await response2.text();
      console.error('V1 endpoint failed:', errorText);
    }
  } catch (error) {
    console.error('Connection test failed:', error);
  }
}

// Run the test
testConnection();