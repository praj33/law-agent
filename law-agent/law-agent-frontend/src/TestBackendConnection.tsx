// Test component to verify backend connection
import React, { useEffect, useState } from 'react';
import { sendMessage } from './api';

const TestBackendConnection: React.FC = () => {
  const [testResult, setTestResult] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const testConnection = async () => {
    setIsLoading(true);
    setTestResult('Testing connection...');
    
    try {
      const response = await sendMessage('What are my rights in a contract dispute?');
      setTestResult(`Success! Received response with domain: ${response.domain}`);
      console.log('Full response:', response);
    } catch (error) {
      setTestResult(`Error: ${error.message}`);
      console.error('Test failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>Backend Connection Test</h2>
      <button 
        onClick={testConnection} 
        disabled={isLoading}
        style={{ 
          padding: '10px 20px', 
          backgroundColor: '#007bff', 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px',
          cursor: isLoading ? 'not-allowed' : 'pointer'
        }}
      >
        {isLoading ? 'Testing...' : 'Test Backend Connection'}
      </button>
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
        <strong>Result:</strong> {testResult}
      </div>
    </div>
  );
};

export default TestBackendConnection;