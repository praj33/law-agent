// Test to see the actual backend response format
import { sendMessage } from './api';

async function testBackendResponse() {
  try {
    console.log('Testing backend response format...');
    
    const response = await sendMessage('What are my rights in a contract dispute?');
    console.log('Full response:', JSON.stringify(response, null, 2));
    
    // Check if formatted_response exists and what it contains
    if (response.formatted_response) {
      console.log('Formatted response exists and contains:', response.formatted_response.substring(0, 500) + '...');
    } else {
      console.log('No formatted_response found');
    }
    
    return response;
  } catch (error) {
    console.error('Test failed:', error);
    return null;
  }
}

// Run the test
testBackendResponse();

export default testBackendResponse;