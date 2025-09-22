# Frontend-Backend Integration Guide

This document explains how the frontend connects to the Render backend and the API endpoints used.

## Backend URL

The backend is hosted on Render at: `https://law-agent-by-grok.onrender.com`

## API Endpoints

### 1. Health Check
- **Endpoint**: `/api/health`
- **Method**: GET
- **Purpose**: Check if the backend is running and healthy

### 2. Legal Query Processing
- **Endpoint**: `/api/ultimate-analysis`
- **Method**: POST
- **Purpose**: Process legal queries and return analysis
- **Request Body**:
  ```json
  {
    "query": "Your legal question here"
  }
  ```
- **Response**:
  ```json
  {
    "query": "The original query",
    "domain": "Legal domain classification",
    "domain_confidence": 0.85,
    "domain_confidence_percentage": "85%",
    "analysis": {
      "summary": "Brief summary of the legal situation",
      "key_points": ["Point 1", "Point 2", "..."]
    },
    "legal_guidance": {
      "legal_procedures": ["Step 1", "Step 2", "..."],
      "timeline": "Estimated timeline",
      "required_documents": ["Document 1", "..."],
      "cost_estimates": "Cost information"
    }
  }
  ```

### 3. Feedback Submission
- **Endpoint**: `/api/feedback`
- **Method**: POST
- **Purpose**: Submit user feedback to improve the system
- **Request Body**:
  ```json
  {
    "query": "The original query",
    "domain": "Classified domain",
    "subdomain": "Classified subdomain",
    "confidence": 0.85,
    "feedback": "helpful|not_helpful",
    "rating": 1-5
  }
  ```

## Frontend Configuration

The frontend is configured to use the Render backend URL through environment variables:

### Environment Variables
- `REACT_APP_API_URL`: Set to `https://law-agent-by-grok.onrender.com`

### API Functions
Located in `src/api.ts`:
- `sendMessage(message)`: Sends a legal query to the backend
- `submitFeedback(...)`: Submits feedback for a response

### Chat Interface
The main chat interface in `src/components/ChatInterface.tsx` uses these API functions to:
1. Send user queries to the backend
2. Display structured responses
3. Allow users to provide feedback on responses

## Testing the Integration

To test the integration, you can run:
```bash
python test_frontend_integration.py
```

This script will:
1. Check the backend health
2. Send a test query
3. Submit feedback for the response

## Troubleshooting

If the frontend cannot connect to the backend:

1. **Check the backend status**: Visit `https://law-agent-by-grok.onrender.com/api/health`
2. **Verify environment variables**: Ensure `REACT_APP_API_URL` is set correctly
3. **Check network connectivity**: Ensure there are no firewall issues
4. **Review browser console**: Look for CORS or network errors

## CORS Configuration

The backend is configured to allow requests from all origins (`*`), so CORS should not be an issue.

## Deployment Notes

When deploying the frontend:
1. Ensure the `REACT_APP_API_URL` environment variable is set to the Render backend URL
2. The frontend can be deployed independently of the backend
3. The backend must be running and accessible for the frontend to work properly