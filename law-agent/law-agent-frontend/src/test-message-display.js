// Test component to verify message display functionality
import React, { useState } from 'react';

const TestMessageDisplay = () => {
  const [messages, setMessages] = useState([
    {
      id: '1',
      type: 'user',
      content: 'Test message',
      timestamp: new Date()
    }
  ]);

  // Simulate adding an AI response
  const addAIResponse = () => {
    const mockResponse = {
      formatted_response: "This is a test response from the backend with formatted content.",
      domain: "Test Domain",
      legal_guidance: {
        legal_procedures: ["Step 1", "Step 2", "Step 3"]
      },
      analysis: {
        key_points: ["Point A", "Point B"]
      }
    };

    const aiMessage = {
      id: Date.now().toString() + '-ai',
      type: 'ai',
      content: mockResponse.formatted_response || mockResponse.response || 'No response content',
      timestamp: new Date(),
      structuredData: {
        domain: mockResponse.domain || 'General',
        legal_route: mockResponse.legal_guidance?.legal_procedures?.join(', ') || mockResponse.analysis?.summary || 'Legal guidance provided',
        timeline: mockResponse.legal_guidance?.timeline || 'Varies by case',
        outcome: mockResponse.analysis?.key_points?.join(', ') || 'Case-specific outcome',
        process_steps: mockResponse.legal_guidance?.legal_procedures?.join(', ') || 'Standard legal process',
        glossary: {}
      },
      rawData: mockResponse
    };

    setMessages(prev => [...prev, aiMessage]);
  };

  const formatTimestamp = (date) => 
    date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Test Message Display</h1>
      <button onClick={addAIResponse} style={{ marginBottom: '20px', padding: '10px' }}>
        Add AI Response
      </button>
      
      <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            style={{ 
              marginBottom: '10px', 
              textAlign: msg.type === 'user' ? 'right' : 'left' 
            }}
          >
            {msg.type === 'user' ? (
              <div style={{ 
                display: 'inline-block', 
                maxWidth: '80%', 
                padding: '10px', 
                borderRadius: '10px', 
                backgroundColor: '#007bff', 
                color: 'white' 
              }}>
                {msg.content}
                <div style={{ fontSize: '0.8em', color: '#e0e0e0', marginTop: '5px', textAlign: 'right' }}>
                  {formatTimestamp(msg.timestamp)}
                </div>
              </div>
            ) : msg.structuredData ? (
              <div style={{ 
                display: 'inline-block', 
                maxWidth: '80%', 
                backgroundColor: '#f0f0f0', 
                padding: '10px', 
                borderRadius: '10px' 
              }}>
                <div><strong>Domain:</strong> {msg.structuredData.domain}</div>
                <div><strong>Legal Route:</strong> {msg.structuredData.legal_route}</div>
                <div><strong>Timeline:</strong> {msg.structuredData.timeline}</div>
                <div><strong>Outcome:</strong> {msg.structuredData.outcome}</div>
                <div><strong>Process Steps:</strong> {msg.structuredData.process_steps}</div>
                <div style={{ fontSize: '0.8em', color: '#666', marginTop: '5px', textAlign: 'right' }}>
                  {formatTimestamp(msg.timestamp)}
                </div>
              </div>
            ) : (
              <div style={{ 
                display: 'inline-block', 
                maxWidth: '80%', 
                backgroundColor: '#f0f0f0', 
                padding: '10px', 
                borderRadius: '10px' 
              }}>
                {msg.content}
                <div style={{ fontSize: '0.8em', color: '#666', marginTop: '5px', textAlign: 'right' }}>
                  {formatTimestamp(msg.timestamp)}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default TestMessageDisplay;