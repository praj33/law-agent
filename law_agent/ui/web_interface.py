"""Web interface for the Law Agent system."""

from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from typing import Optional

from ..core.state import UserType, FeedbackType
from ..api.routes import law_agent


def create_web_app() -> FastAPI:
    """Create web interface application."""
    
    app = FastAPI(title="Law Agent Web Interface")
    
    # Setup templates and static files
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    templates = Jinja2Templates(directory=templates_dir)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        """Home page."""
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/chat", response_class=HTMLResponse)
    async def chat_interface(request: Request, session_id: Optional[str] = None):
        """Chat interface."""
        return templates.TemplateResponse("chat.html", {
            "request": request,
            "session_id": session_id
        })
    
    @app.post("/create-session")
    async def create_session_web(
        user_id: str = Form(...),
        user_type: str = Form(...)
    ):
        """Create session from web form."""
        try:
            session_id = await law_agent.create_session(
                user_id=user_id,
                user_type=UserType(user_type)
            )
            return RedirectResponse(
                url=f"/chat?session_id={session_id}",
                status_code=303
            )
        except Exception as e:
            return HTMLResponse(f"Error creating session: {str(e)}", status_code=500)
    
    return app


# HTML Templates (would normally be in separate files)
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Law Agent - Legal AI Assistant</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #34495e; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        button { background: #3498db; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; width: 100%; }
        button:hover { background: #2980b9; }
        .features { margin-top: 30px; }
        .feature { margin-bottom: 15px; padding: 15px; background: #ecf0f1; border-radius: 5px; }
        .feature h3 { margin: 0 0 10px 0; color: #2c3e50; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏛️ Law Agent - Your AI Legal Assistant</h1>
        
        <form action="/create-session" method="post">
            <div class="form-group">
                <label for="user_id">Your Name or ID:</label>
                <input type="text" id="user_id" name="user_id" required placeholder="Enter your name or unique ID">
            </div>
            
            <div class="form-group">
                <label for="user_type">I am a:</label>
                <select id="user_type" name="user_type" required>
                    <option value="">Select your role</option>
                    <option value="common_person">Individual seeking legal help</option>
                    <option value="law_firm">Law firm professional</option>
                    <option value="legal_professional">Legal professional</option>
                </select>
            </div>
            
            <button type="submit">Start Legal Consultation</button>
        </form>
        
        <div class="features">
            <div class="feature">
                <h3>🤖 AI-Powered Legal Guidance</h3>
                <p>Get intelligent legal advice powered by advanced AI that learns from your interactions.</p>
            </div>
            
            <div class="feature">
                <h3>📚 Comprehensive Legal Knowledge</h3>
                <p>Access extensive legal glossary and domain-specific guidance across multiple areas of law.</p>
            </div>
            
            <div class="feature">
                <h3>🎯 Personalized Experience</h3>
                <p>Adaptive interface that learns your preferences and provides tailored recommendations.</p>
            </div>
            
            <div class="feature">
                <h3>⚖️ Multiple Legal Domains</h3>
                <p>Family Law, Criminal Law, Corporate Law, Property Law, Employment Law, and more.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

CHAT_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Law Agent Chat</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f5f5f5; height: 100vh; display: flex; flex-direction: column; }
        .header { background: #2c3e50; color: white; padding: 15px; text-align: center; }
        .chat-container { flex: 1; display: flex; flex-direction: column; max-width: 1000px; margin: 0 auto; width: 100%; }
        .messages { flex: 1; padding: 20px; overflow-y: auto; background: white; }
        .message { margin-bottom: 20px; padding: 15px; border-radius: 10px; }
        .user-message { background: #3498db; color: white; margin-left: 20%; }
        .agent-message { background: #ecf0f1; margin-right: 20%; }
        .input-area { padding: 20px; background: white; border-top: 1px solid #ddd; }
        .input-group { display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 5px; font-size: 16px; }
        button { padding: 12px 20px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #2980b9; }
        .feedback-buttons { margin-top: 10px; }
        .feedback-btn { padding: 5px 10px; margin-right: 10px; font-size: 12px; }
        .upvote { background: #27ae60; }
        .downvote { background: #e74c3c; }
        .domain-info { font-size: 12px; color: #7f8c8d; margin-top: 5px; }
        .glossary-terms { margin-top: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; }
        .term { display: inline-block; margin: 2px; padding: 4px 8px; background: #e9ecef; border-radius: 3px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h2>🏛️ Law Agent Chat</h2>
        <p>Session: {{ session_id or 'Not connected' }}</p>
    </div>
    
    <div class="chat-container">
        <div class="messages" id="messages">
            <div class="message agent-message">
                <strong>Law Agent:</strong> Hello! I'm your AI legal assistant. I can help you with various legal questions and guide you through legal procedures. What legal matter can I assist you with today?
            </div>
        </div>
        
        <div class="input-area">
            <div class="input-group">
                <input type="text" id="messageInput" placeholder="Type your legal question here..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        const sessionId = "{{ session_id }}";
        let currentInteractionId = null;
        let messageStartTime = null;

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message || !sessionId) return;
            
            // Add user message to chat
            addMessage(message, 'user');
            input.value = '';
            messageStartTime = Date.now();
            
            try {
                // Send to API
                const response = await fetch('/api/api/v1/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        query: message
                    })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    currentInteractionId = result.interaction_id;
                    addAgentMessage(result);
                } else {
                    addMessage('Error: ' + result.detail, 'agent');
                }
            } catch (error) {
                addMessage('Error: Failed to send message', 'agent');
            }
        }

        function addMessage(text, sender) {
            const messages = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.innerHTML = `<strong>${sender === 'user' ? 'You' : 'Law Agent'}:</strong> ${text}`;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }

        function addAgentMessage(result) {
            const messages = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message agent-message';
            
            let html = `<strong>Law Agent:</strong> ${result.response.text}`;
            
            // Add domain info
            html += `<div class="domain-info">Domain: ${result.domain} (${(result.confidence * 100).toFixed(1)}% confidence)</div>`;
            
            // Add glossary terms
            if (result.glossary_terms && result.glossary_terms.length > 0) {
                html += '<div class="glossary-terms"><strong>Related Terms:</strong><br>';
                result.glossary_terms.forEach(term => {
                    html += `<span class="term" title="${term.definition}">${term.term}</span>`;
                });
                html += '</div>';
            }
            
            // Add feedback buttons
            html += `
                <div class="feedback-buttons">
                    <button class="feedback-btn upvote" onclick="submitFeedback('upvote')">👍 Helpful</button>
                    <button class="feedback-btn downvote" onclick="submitFeedback('downvote')">👎 Not Helpful</button>
                </div>
            `;
            
            messageDiv.innerHTML = html;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }

        async function submitFeedback(feedbackType) {
            if (!currentInteractionId || !sessionId) return;
            
            const timeSpent = messageStartTime ? (Date.now() - messageStartTime) / 1000 : null;
            
            try {
                const response = await fetch('/api/api/v1/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: sessionId,
                        interaction_id: currentInteractionId,
                        feedback: feedbackType,
                        time_spent: timeSpent
                    })
                });
                
                if (response.ok) {
                    // Disable feedback buttons
                    const buttons = document.querySelectorAll('.feedback-btn');
                    buttons.forEach(btn => {
                        btn.disabled = true;
                        btn.style.opacity = '0.5';
                    });
                }
            } catch (error) {
                console.error('Failed to submit feedback:', error);
            }
        }

        // Auto-focus input
        document.getElementById('messageInput').focus();
    </script>
</body>
</html>
"""

# Create template files
def create_template_files():
    """Create HTML template files."""
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    os.makedirs(templates_dir, exist_ok=True)
    
    with open(os.path.join(templates_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(INDEX_HTML)

    with open(os.path.join(templates_dir, "chat.html"), "w", encoding="utf-8") as f:
        f.write(CHAT_HTML)

# Create templates when module is imported
create_template_files()
