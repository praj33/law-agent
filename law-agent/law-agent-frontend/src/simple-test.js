// Simple test to verify frontend-backend connection
async function testConnection() {
  const API_URL = "https://law-agent-by-grok.onrender.com";
  console.log("Testing connection to backend at:", API_URL);
  
  try {
    // Test health endpoint
    const healthResponse = await fetch(`${API_URL}/api/health`);
    console.log("Health check status:", healthResponse.status);
    
    if (healthResponse.ok) {
      const healthData = await healthResponse.json();
      console.log("Health data:", healthData);
    } else {
      console.error("Health check failed with status:", healthResponse.status);
    }
    
    // Test query endpoint
    const queryResponse = await fetch(`${API_URL}/api/ultimate-analysis`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: "What are my rights in a contract dispute?" })
    });
    
    console.log("Query endpoint status:", queryResponse.status);
    
    if (queryResponse.ok) {
      const queryData = await queryResponse.json();
      console.log("Query response:", JSON.stringify(queryData, null, 2));
    } else {
      console.error("Query failed with status:", queryResponse.status);
      const errorText = await queryResponse.text();
      console.error("Error details:", errorText);
    }
  } catch (error) {
    console.error("Connection test failed with error:", error);
  }
}

// Run the test
testConnection();