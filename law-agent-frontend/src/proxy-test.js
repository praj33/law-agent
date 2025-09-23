// Test to verify that the proxy is working correctly
async function proxyTest() {
  console.log('=== Proxy Test ===');
  
  try {
    // Test 1: Check if the proxy is working by calling a simple endpoint
    console.log('\n1. Testing proxy with health endpoint...');
    const healthResponse = await fetch('/api/health');
    console.log('Health endpoint status:', healthResponse.status);
    
    if (healthResponse.ok) {
      const healthData = await healthResponse.json();
      console.log('Health endpoint response:', healthData);
    } else {
      const errorText = await healthResponse.text();
      console.log('Health endpoint error:', errorText);
      
      // Try to parse as JSON
      try {
        const errorJson = JSON.parse(errorText);
        console.log('Parsed health error JSON:', errorJson);
      } catch (e) {
        console.log('Could not parse health error as JSON');
      }
    }
    
    // Test 2: Test the ultimate-analysis endpoint
    console.log('\n2. Testing proxy with ultimate-analysis endpoint...');
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
    
    if (analysisResponse.ok) {
      const data = await analysisResponse.json();
      console.log('Analysis endpoint success:', data);
    } else {
      const errorText = await analysisResponse.text();
      console.log('Analysis endpoint error text:', errorText);
      
      // Try to parse as JSON
      try {
        const errorJson = JSON.parse(errorText);
        console.log('Parsed analysis error JSON:', errorJson);
        
        if (errorJson.available_endpoints) {
          console.log('Available endpoints according to backend:', errorJson.available_endpoints);
        }
        
        if (errorJson.error) {
          console.log('Error message from backend:', errorJson.error);
        }
      } catch (e) {
        console.log('Could not parse analysis error as JSON');
      }
    }
  } catch (error) {
    console.error('Proxy test failed:', error);
  }
  
  console.log('\n=== Proxy Test Complete ===');
}

// Run the test
proxyTest();