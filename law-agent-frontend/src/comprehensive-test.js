// Comprehensive test to debug the connection issue
async function comprehensiveTest() {
  console.log('=== Comprehensive Connection Test ===');
  
  try {
    // Test 1: Check if we can reach the backend at all
    console.log('\n1. Testing basic connectivity to backend...');
    const healthResponse = await fetch('/api/health');
    console.log('Health check status:', healthResponse.status);
    
    if (healthResponse.ok) {
      const healthData = await healthResponse.json();
      console.log('Health check data:', healthData);
    } else {
      console.log('Health check failed with status:', healthResponse.status);
      const healthText = await healthResponse.text();
      console.log('Health check response:', healthText);
    }
    
    // Test 2: Test the ultimate-analysis endpoint
    console.log('\n2. Testing /api/ultimate-analysis endpoint...');
    const analysisResponse = await fetch('/api/ultimate-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: 'What are my rights in a contract dispute?'
      })
    });
    
    console.log('Analysis endpoint status:', analysisResponse.status);
    
    // Check content type
    const contentType = analysisResponse.headers.get('content-type');
    console.log('Content type:', contentType);
    
    if (analysisResponse.ok) {
      if (contentType && contentType.includes('application/json')) {
        const data = await analysisResponse.json();
        console.log('Success! Response data:', data);
      } else {
        const text = await analysisResponse.text();
        console.log('Non-JSON response:', text);
      }
    } else {
      const errorText = await analysisResponse.text();
      console.log('Error response text:', errorText);
      
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
    
    // Test 3: Check what endpoints are available
    console.log('\n3. Checking available endpoints...');
    const statsResponse = await fetch('/api/stats');
    console.log('Stats endpoint status:', statsResponse.status);
    
    if (statsResponse.ok) {
      const statsData = await statsResponse.json();
      console.log('Stats data:', statsData);
    }
    
  } catch (error) {
    console.error('Comprehensive test failed with error:', error);
  }
  
  console.log('\n=== Test Complete ===');
}

// Run the test
comprehensiveTest();