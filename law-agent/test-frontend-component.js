// Test script to simulate the ChatInterface component behavior
const API_URL = "https://law-agent-by-grok.onrender.com";

async function testChatInterface() {
  console.log("Testing ChatInterface component behavior...");
  
  try {
    // Simulate sending a message
    const message = "What are my rights in a contract dispute?";
    console.log("Sending message:", message);
    
    const response = await fetch(`${API_URL}/api/ultimate-analysis`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: message }),
    });
    
    if (!response.ok) {
      throw new Error("Backend error: " + response.status);
    }
    
    const responseData = await response.json();
    console.log("Received response:", JSON.stringify(responseData, null, 2));
    
    // Simulate how the ChatInterface would process this response
    const aiMessage = {
      id: Date.now().toString() + '-ai',
      type: 'ai',
      content: responseData.formatted_response || responseData.response || 'No response content',
      timestamp: new Date(),
      structuredData: {
        domain: responseData.domain || 'General',
        legal_route: responseData.legal_guidance?.legal_procedures?.join(', ') || responseData.analysis?.summary || 'Legal guidance provided',
        timeline: responseData.legal_guidance?.timeline || 'Varies by case',
        outcome: responseData.analysis?.key_points?.join(', ') || 'Case-specific outcome',
        process_steps: responseData.legal_guidance?.legal_procedures?.join(', ') || 'Standard legal process',
        glossary: {} // Will be populated if available
      },
      rawData: responseData // Keep full data for feedback
    };
    
    console.log("Processed AI message:", JSON.stringify(aiMessage, null, 2));
    console.log("Content to display:", aiMessage.content);
    
    if (aiMessage.structuredData) {
      console.log("Structured data:");
      console.log("- Domain:", aiMessage.structuredData.domain);
      console.log("- Legal Route:", aiMessage.structuredData.legal_route);
      console.log("- Timeline:", aiMessage.structuredData.timeline);
      console.log("- Outcome:", aiMessage.structuredData.outcome);
      console.log("- Process Steps:", aiMessage.structuredData.process_steps);
    }
    
    console.log("Test completed successfully!");
  } catch (error) {
    console.error("Test failed:", error);
  }
}

// Run the test
testChatInterface();