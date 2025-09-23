/**
 * API Service for Law Agent
 * Handles communication with the backend API
 */

// Use the direct backend URL instead of proxy
const API_BASE_URL = 'https://law-agent-by-grok-1.onrender.com/api';

export interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

export interface QueryRequest {
  query: string;
}

export interface QueryResponse {
  query: string;
  domain: string;
  domain_confidence: number;
  domain_confidence_percentage: string;
  formatted_response: string;
  response?: string;
  result?: string;
  // Add other properties as needed based on actual backend response
  [key: string]: any; // Allow additional properties
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
    console.log('API Service initialized with backend URL:', this.baseUrl);
  }

  /**
   * Send a message to the AI and get a response
   */
  async sendMessage(message: string): Promise<QueryResponse> {
    try {
      const queryRequest: QueryRequest = {
        query: message
      };

      console.log('Sending message with request:', queryRequest);
      const fullUrl = `${this.baseUrl}/ultimate-analysis`;
      console.log('Sending POST request to:', fullUrl);
      
      // Log the full request details
      console.log('Request details:', {
        url: fullUrl,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(queryRequest)
      });
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(queryRequest),
      });

      console.log('Message sending response status:', response.status);
      
      // Check if the response is HTML (which indicates an error page)
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('text/html')) {
        const errorText = await response.text();
        console.error('Received HTML response instead of JSON:', errorText);
        throw new Error(`Backend returned HTML instead of JSON. This usually means the endpoint was not found. Response: ${errorText.substring(0, 200)}...`);
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Message sending failed with status:', response.status, 'Response:', errorText);
        
        // Try to parse the error as JSON to get more details
        try {
          const errorJson = JSON.parse(errorText);
          if (errorJson.available_endpoints) {
            console.log('Available endpoints:', errorJson.available_endpoints);
          }
          if (errorJson.error) {
            console.log('Error message from backend:', errorJson.error);
          }
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        } catch (e) {
          // If we can't parse as JSON, just throw the original error
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
      }

      const data = await response.json();
      console.log('Message sending successful, received data:', data);
      
      // Validate that we have the expected domain information
      if (!data.hasOwnProperty('domain')) {
        console.warn('Response missing domain property:', data);
      }
      
      if (!data.hasOwnProperty('domain_confidence')) {
        console.warn('Response missing domain_confidence property:', data);
      }
      
      return data;
    } catch (error) {
      console.error('Error sending message:', error);
      // Re-throw the error so it can be handled by the calling function
      throw error;
    }
  }

  /**
   * Get domain classification for a query
   */
  async getDomainInfo(query: string): Promise<{domain: string, confidence: number, confidence_percentage: string}> {
    try {
      console.log('Getting domain info for query:', query);
      const fullUrl = `${this.baseUrl}/ultimate-analysis`;
      console.log('Sending domain info request to:', fullUrl);
      
      const queryRequest: QueryRequest = {
        query: query
      };
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(queryRequest),
      });

      console.log('Domain info response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Domain info request failed with status:', response.status, 'Response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data = await response.json();
      console.log('Domain info request successful, received data:', data);
      
      // Return domain information with proper structure
      return {
        domain: data.domain || 'unknown',
        confidence: data.domain_confidence !== undefined ? data.domain_confidence : 0,
        confidence_percentage: data.domain_confidence_percentage || '0%'
      };
    } catch (error) {
      console.error('Error getting domain info:', error);
      throw error;
    }
  }

  /**
   * Test the API connection and get sample domain information
   */
  async testDomainInfo(): Promise<any> {
    try {
      console.log('Testing domain info retrieval...');
      const fullUrl = `${this.baseUrl}/ultimate-analysis`;
      console.log('Sending test POST request to:', fullUrl);
      
      // Send a simple test query
      const testQuery = "What are my rights in a contract dispute?";
      const queryRequest: QueryRequest = {
        query: testQuery
      };
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(queryRequest),
      });

      console.log('Test response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Test failed with status:', response.status, 'Response:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const data = await response.json();
      console.log('Test successful, received domain data:', data);
      return data;
    } catch (error) {
      console.error('Error testing domain info:', error);
      throw error;
    }
  }

  /**
   * Submit feedback for an interaction
   */
  async submitFeedback(query: string, domain: string, confidence: number, feedback: string, rating: number): Promise<void> {
    try {
      console.log('Submitting feedback:', { query, domain, confidence, feedback, rating });
      const fullUrl = `${this.baseUrl}/feedback`;
      console.log('Sending POST request to:', fullUrl);
      
      const response = await fetch(fullUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          domain,
          confidence,
          feedback,
          rating
        }),
      });

      console.log('Feedback submission response status:', response.status);
      
      // Check if the response is HTML (which indicates an error page)
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('text/html')) {
        const errorText = await response.text();
        console.error('Received HTML response instead of JSON:', errorText);
        throw new Error(`Backend returned HTML instead of JSON. This usually means the endpoint was not found. Response: ${errorText.substring(0, 200)}...`);
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Feedback submission failed with status:', response.status, 'Response:', errorText);
        
        // Try to parse the error as JSON to get more details
        try {
          const errorJson = JSON.parse(errorText);
          if (errorJson.available_endpoints) {
            console.log('Available endpoints:', errorJson.available_endpoints);
          }
          if (errorJson.error) {
            console.log('Error message from backend:', errorJson.error);
          }
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        } catch (e) {
          // If we can't parse as JSON, just throw the original error
          throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }
      }

      const data = await response.json();
      console.log('Feedback submission successful, received data:', data);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  }
}

// Create and export singleton instance
export const apiService = new ApiService();