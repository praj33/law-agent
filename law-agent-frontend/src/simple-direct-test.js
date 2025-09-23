// Simple direct test
console.log('Checking if we can make a direct request to the backend');

// This will likely fail due to CORS, but let's see what happens
fetch('https://law-agent-by-grok-1.onrender.com/api/ultimate-analysis', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'Test'
  })
}).then(response => {
  console.log('Direct request status:', response.status);
  return response.text();
}).then(data => {
  console.log('Direct request response:', data);
}).catch(error => {
  console.error('Direct request failed:', error);
});