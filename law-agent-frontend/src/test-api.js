// Simple test to check API connectivity
async function testApi() {
  try {
    console.log('Testing API connection...');
    console.log('Making request to: /api/ultimate-analysis');
    
    const response = await fetch('/api/ultimate-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: 'Test query'
      })
    });
    
    console.log('Response status:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('Success:', data);
    } else {
      const errorText = await response.text();
      console.log('Error response:', errorText);
    }
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

// Run the test
testApi();