// Simple test script to verify API endpoints
async function testEndpoints() {
  console.log('Testing API endpoints...');
  
  try {
    // Test session creation
    console.log('Creating session...');
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
    
    console.log('Session response status:', sessionResponse.status);
    
    if (!sessionResponse.ok) {
      const errorText = await sessionResponse.text();
      console.error('Session creation failed:', errorText);
      return;
    }
    
    const sessionData = await sessionResponse.json();
    const sessionId = sessionData.session_id;
    console.log('Session created successfully:', sessionId);
    
    // Test query endpoint
    console.log('Sending test query...');
    const queryResponse = await fetch('/api/v1/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        query: 'What are my rights in a contract dispute?',
        interaction_type: 'query'
      })
    });
    
    console.log('Query response status:', queryResponse.status);
    
    if (!queryResponse.ok) {
      const errorText = await queryResponse.text();
      console.error('Query failed:', errorText);
      return;
    }
    
    const queryData = await queryResponse.json();
    console.log('Query successful:', JSON.stringify(queryData, null, 2));
    
  } catch (error) {
    console.error('Test failed with error:', error);
  }
}

// Run the test
testEndpoints();