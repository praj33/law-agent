// Comprehensive debug test to see what's happening with the connection
async function debugConnection() {
  console.log('=== Debug Connection Test ===');
  
  try {
    // Test 1: Check what environment variables are available
    console.log('\n1. Environment variables:');
    console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
    console.log('Window location:', window.location.href);
    
    // Test 2: Test the exact endpoint that should work
    console.log('\n2. Testing /api/ultimate-analysis endpoint...');
    console.log('This should be proxied to: https://law-agent-by-grok-1.onrender.com/api/ultimate-analysis');
    
    const startTime = Date.now();
    const response = await fetch('/api/ultimate-analysis', {
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
    console.log('Response headers:', [...response.headers.entries()]);
    
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
    
    // Test 3: Try a health check endpoint
    console.log('\n3. Testing health endpoint...');
    try {
      const healthResponse = await fetch('/api/health');
      console.log('Health check status:', healthResponse.status);
      
      if (healthResponse.ok) {
        const healthData = await healthResponse.json();
        console.log('Health check data:', healthData);
      } else {
        const healthError = await healthResponse.text();
        console.log('Health check error:', healthError);
      }
    } catch (healthError) {
      console.log('Health check failed:', healthError);
    }
    
  } catch (error) {
    console.error('❌ Debug test failed with error:', error);
    
    // Check if it's a CORS error
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      console.log('This might be a CORS error. The backend might not be accepting requests from localhost.');
    }
  }
  
  console.log('\n=== Debug Test Complete ===');
}

// Run the test
debugConnection();

// Also try a direct fetch to see if that works
console.log('\n=== Trying Direct Fetch ===');
fetch('https://law-agent-by-grok-1.onrender.com/api/ultimate-analysis', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'Direct test'
  })
}).then(response => {
  console.log('Direct fetch status:', response.status);
  return response.text();
}).then(data => {
  console.log('Direct fetch response:', data);
}).catch(error => {
  console.error('Direct fetch failed:', error);
  console.log('This is expected due to CORS restrictions');
});