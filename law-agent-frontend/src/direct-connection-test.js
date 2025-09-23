// Test direct connection to the backend
async function testDirectConnection() {
  console.log('Testing direct connection to backend...');
  
  try {
    // Test the ultimate-analysis endpoint directly
    console.log('Sending request to: https://law-agent-by-grok-1.onrender.com/api/ultimate-analysis');
    const response = await fetch('https://law-agent-by-grok-1.onrender.com/api/ultimate-analysis', {
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
      } catch (e) {
        console.log('Could not parse error as JSON');
      }
    }
  } catch (error) {
    console.error('Direct connection test failed:', error);
    console.log('This might be due to CORS restrictions when testing from the browser');
  }
}

// Run the test
testDirectConnection();