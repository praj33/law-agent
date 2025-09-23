// Test file to verify backend connection
// Export to make it a module
export {};

async function testBackendConnection() {
  console.log('=== Testing Backend Connection ===');
  
  try {
    // Test the direct backend endpoint
    console.log('\n1. Testing direct backend connection...');
    console.log('URL: https://law-agent-by-grok-1.onrender.com/api/ultimate-analysis');
    
    const startTime = Date.now();
    const response = await fetch('https://law-agent-by-grok-1.onrender.com/api/ultimate-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: 'What are my rights in a contract dispute?'
      })
    });
    
    const endTime = Date.now();
    console.log('Request took:', endTime - startTime, 'ms');
    console.log('Response status:', response.status);
    
    // Check content type
    const contentType = response.headers.get('content-type');
    console.log('Content type:', contentType);
    
    if (response.ok) {
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        console.log('✅ SUCCESS! Received JSON data:', data);
      } else {
        const text = await response.text();
        console.log('✅ SUCCESS! Received non-JSON response:', text);
      }
    } else {
      const errorText = await response.text();
      console.log('❌ ERROR! Response status:', response.status);
      console.log('❌ ERROR! Response text:', errorText);
      
      // Try to parse as JSON
      try {
        const errorJson = JSON.parse(errorText);
        console.log('❌ ERROR! Parsed JSON error:', errorJson);
        
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
    console.error('❌ Test failed with error:', error);
    
    // Check if it's a CORS error
    if (error instanceof TypeError && error.message.includes('fetch')) {
      console.log('This might be a CORS error. The backend might not be accepting requests from localhost.');
    }
  }
  
  console.log('\n=== Test Complete ===');
}

// Run the test
testBackendConnection();