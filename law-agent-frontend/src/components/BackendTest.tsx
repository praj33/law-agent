import React, { useState } from 'react';
import { apiService } from '../services/apiService';

const BackendTest: React.FC = () => {
  const [testResult, setTestResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runTest = async () => {
    setLoading(true);
    setError(null);
    setTestResult(null);
    
    try {
      const result = await apiService.testDomainInfo();
      setTestResult(result);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      console.error('Test error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-gray-800/50 rounded-2xl border border-white/20">
      <h2 className="text-2xl font-bold text-white mb-6">Backend API Test</h2>
      
      <button
        onClick={runTest}
        disabled={loading}
        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors mb-6"
      >
        {loading ? 'Testing...' : 'Test Domain Information'}
      </button>
      
      {error && (
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-4 mb-6">
          <h3 className="text-red-400 font-semibold mb-2">Error:</h3>
          <p className="text-red-200">{error}</p>
        </div>
      )}
      
      {testResult && (
        <div className="bg-green-900/50 border border-green-500 rounded-lg p-4">
          <h3 className="text-green-400 font-semibold mb-2">Test Results:</h3>
          <div className="text-green-200">
            <p><strong>Query:</strong> {testResult.query}</p>
            <p><strong>Domain:</strong> {testResult.domain}</p>
            <p><strong>Confidence:</strong> {testResult.domain_confidence} ({testResult.domain_confidence_percentage})</p>
            <div className="mt-4">
              <p><strong>Response Preview:</strong></p>
              <div className="bg-gray-900/50 p-3 rounded mt-2 max-h-40 overflow-y-auto">
                <p className="text-sm">{testResult.formatted_response?.substring(0, 200)}...</p>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div className="mt-6 text-gray-400 text-sm">
        <p>This test verifies that the backend is correctly returning domain information.</p>
        <p>Check the browser console for detailed logs.</p>
      </div>
    </div>
  );
};

export default BackendTest;