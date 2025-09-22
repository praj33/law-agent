// Test API connection
import { sendMessage } from './api';

async function testApiConnection() {
  try {
    console.log('Testing API connection to:', process.env.REACT_APP_API_URL);
    
    const response = await sendMessage('Test message');
    console.log('API connection successful:', response);
    
    return true;
  } catch (error) {
    console.error('API connection failed:', error);
    return false;
  }
}

// Run the test
testApiConnection();

export default testApiConnection;