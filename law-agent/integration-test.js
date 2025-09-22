// Integration test for frontend-backend connection
const https = require('https');

// Test the backend endpoints
async function testBackendEndpoints() {
  console.log('Testing backend endpoints...\n');
  
  const baseUrl = 'https://law-agent-by-grok.onrender.com';
  
  // Test 1: Health endpoint
  console.log('1. Testing /api/health endpoint...');
  try {
    const healthResponse = await makeRequest(`${baseUrl}/api/health`);
    console.log(`   Status: ${healthResponse.statusCode}`);
    if (healthResponse.statusCode === 200) {
      const data = JSON.parse(healthResponse.data);
      console.log(`   Success: ${data.status}`);
      console.log(`   Components: ${Object.keys(data.components).length} components healthy\n`);
    } else {
      console.log(`   Error: ${healthResponse.statusCode}\n`);
    }
  } catch (error) {
    console.log(`   Failed: ${error.message}\n`);
  }
  
  // Test 2: Ultimate analysis endpoint
  console.log('2. Testing /api/ultimate-analysis endpoint...');
  try {
    const analysisResponse = await makeRequest(`${baseUrl}/api/ultimate-analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: 'What are my rights in a contract dispute?'
      })
    });
    
    console.log(`   Status: ${analysisResponse.statusCode}`);
    if (analysisResponse.statusCode === 200) {
      const data = JSON.parse(analysisResponse.data);
      console.log(`   Success: ${data.success}`);
      console.log(`   Domain: ${data.domain}`);
      console.log(`   Response length: ${data.formatted_response.length} characters\n`);
    } else {
      console.log(`   Error: ${analysisResponse.statusCode}\n`);
    }
  } catch (error) {
    console.log(`   Failed: ${error.message}\n`);
  }
  
  // Test 3: Feedback endpoint
  console.log('3. Testing /api/feedback endpoint...');
  try {
    const feedbackResponse = await makeRequest(`${baseUrl}/api/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query: 'Test query',
        domain: 'Test Domain',
        subdomain: 'Test Subdomain',
        confidence: 0.8,
        feedback: 'helpful',
        rating: 5
      })
    });
    
    console.log(`   Status: ${feedbackResponse.statusCode}`);
    if (feedbackResponse.statusCode === 200) {
      const data = JSON.parse(feedbackResponse.data);
      console.log(`   Success: ${data.success}\n`);
    } else {
      console.log(`   Error: ${feedbackResponse.statusCode}\n`);
    }
  } catch (error) {
    console.log(`   Failed: ${error.message}\n`);
  }
  
  console.log('Integration test completed!');
}

// Helper function to make HTTP requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const requestOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      headers: options.headers || {}
    };
    
    const req = https.request(requestOptions, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          data: data
        });
      });
    });
    
    req.on('error', (error) => {
      reject(error);
    });
    
    if (options.body) {
      req.write(options.body);
    }
    
    req.end();
  });
}

// Run the test
testBackendEndpoints();