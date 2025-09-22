# Backend Integration Documentation

## Overview
This document explains how the frontend LawAgentApp.tsx component has been integrated with the backend API deployed at https://law-agent-by-grok-1.onrender.com.

## Changes Made

### 1. API Configuration
The frontend is configured to communicate with the backend through the following environment variables in `.env`:
```
REACT_APP_API_URL=https://law-agent-by-grok-1.onrender.com
REACT_APP_ANALYTICS_URL=https://law-agent-by-grok-1.onrender.com
REACT_APP_DOCUMENT_URL=https://law-agent-by-grok-1.onrender.com
```

### 2. API Integration in LawAgentApp.tsx
The chat functionality in LawAgentApp.tsx has been updated to use the actual backend API instead of mock responses:

1. **Import Statements**: Added imports for the API function and Message type
2. **Message Handling**: Modified `handleSendMessage` to:
   - Send user messages to the backend API
   - Process backend responses with proper formatting
   - Handle errors gracefully
3. **Welcome Message**: Updated the initial welcome message to reflect the real capabilities

### 3. API Endpoint
The frontend communicates with the backend using the `/api/ultimate-analysis` endpoint:
```
POST https://law-agent-by-grok-1.onrender.com/api/ultimate-analysis
Content-Type: application/json
{
  "query": "User's legal question"
}
```

### 4. Response Handling
The backend returns a structured response with:
- `formatted_response`: The formatted legal analysis
- `domain`: Legal domain classification
- `legal_guidance`: Legal procedures and guidance
- Additional metadata

## Testing
To verify the integration:
1. Start the frontend: `npm start`
2. Navigate to the Chat view
3. Enter a legal question
4. Observe the response from the backend

## Troubleshooting
If the integration isn't working:
1. Check that the backend URL is correct in `.env`
2. Verify the backend is accessible: `curl https://law-agent-by-grok-1.onrender.com/api/health`
3. Check browser console for CORS or network errors
4. Ensure the backend is properly configured to accept requests from the frontend origin