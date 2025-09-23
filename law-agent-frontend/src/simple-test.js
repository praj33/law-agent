// Simple test to verify the connection to the backend
async function testConnection() {
  console.log('Testing connection to backend...');
  
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
    
    console.log('Endpoint status:', response.status);
    
    if (response.ok) {
      const data = await response.json();
      console.log('Success:', data);
    } else {
      const errorText = await response.text();
      console.error('Failed:', errorText);
    }
  } catch (error) {
    console.error('Connection test failed:', error);
  }
}

// Run the test
testConnection();