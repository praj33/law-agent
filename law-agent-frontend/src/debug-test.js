// Debug test to see what the backend is actually returning
async function debugTest() {
  console.log('Debug test - checking what the backend returns...');
  
  try {
    // Test the ultimate-analysis endpoint
    console.log('Testing /api/ultimate-analysis endpoint...');
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
    console.log('Response headers:', [...response.headers.entries()]);
    
    // Check content type
    const contentType = response.headers.get('content-type');
    console.log('Content type:', contentType);
    
    if (contentType && contentType.includes('application/json')) {
      const data = await response.json();
      console.log('JSON Response data:', data);
    } else {
      const text = await response.text();
      console.log('Text Response data:', text);
    }
  } catch (error) {
    console.error('Debug test failed:', error);
  }
}

// Run the test
debugTest();