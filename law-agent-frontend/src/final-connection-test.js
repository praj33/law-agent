// Final test to verify the connection is working correctly
async function finalConnectionTest() {
  console.log('=== Final Connection Test ===');
  
  try {
    // Test 1: Verify we're using the proxy correctly
    console.log('\n1. Testing proxy configuration...');
    console.log('Requests to /api/* should be proxied to https://law-agent-by-grok-1.onrender.com');
    
    // Test 2: Test the ultimate-analysis endpoint through the proxy
    console.log('\n2. Testing /api/ultimate-analysis endpoint through proxy...');
    const response = await fetch('/api/ultimate-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: 'What are my rights in a contract dispute?'
      })
    });
    
    console.log('Response status:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('Success! Received data:', data);
    } else {
      const errorText = await response.text();
      console.log('Error response:', errorText);
      
      // Try to parse as JSON
      try {
        const errorJson = JSON.parse(errorText);
        console.log('Parsed error JSON:', errorJson);
        
        if (errorJson.available_endpoints) {
          console.log('Available endpoints:', errorJson.available_endpoints);
        }
        
        if (errorJson.error) {
          console.log('Error message:', errorJson.error);
        }
      } catch (e) {
        console.log('Could not parse error as JSON');
      }
    }
  } catch (error) {
    console.error('Final connection test failed:', error);
  }
  
  console.log('\n=== Final Test Complete ===');
}

// Run the test
finalConnectionTest();