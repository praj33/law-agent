const https = require('https');

const data = JSON.stringify({
  query: 'What are my rights in a contract dispute?'
});

const options = {
  hostname: 'law-agent-by-grok-1.onrender.com',
  port: 443,
  path: '/api/ultimate-analysis',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': data.length
  }
};

const req = https.request(options, (res) => {
  console.log(`Status Code: ${res.statusCode}`);
  
  let responseData = '';
  
  res.on('data', (chunk) => {
    responseData += chunk;
  });
  
  res.on('end', () => {
    try {
      const jsonData = JSON.parse(responseData);
      console.log('Response:', JSON.stringify(jsonData, null, 2));
    } catch (error) {
      console.log('Response (raw):', responseData);
    }
  });
});

req.on('error', (error) => {
  console.error('Error:', error);
});

req.write(data);
req.end();