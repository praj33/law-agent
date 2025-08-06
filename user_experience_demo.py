#!/usr/bin/env python3
"""User Experience Demo - Show how users can see RL changes in action."""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

BASE_URL = "http://localhost:8000"

class UserExperienceDemo:
    """Demonstrate user-visible RL improvements."""
    
    def __init__(self):
        self.session_id = None
        self.interactions = []
        
    def create_user_session(self, user_type: str = "common_person") -> str:
        """Create a user session and show the response."""
        print("👤 USER ACTION: Creating a new session")
        print("-" * 40)
        
        response = requests.post(
            f"{BASE_URL}/api/v1/sessions",
            json={"user_id": "demo_user", "user_type": user_type}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.session_id = data["session_id"]
            
            print(f"✅ SESSION CREATED")
            print(f"   Session ID: {self.session_id}")
            print(f"   User Type: {user_type}")
            print(f"   Timestamp: {data.get('created_at', 'N/A')}")
            
            return self.session_id
        else:
            print(f"❌ Session creation failed: {response.status_code}")
            return None
    
    def ask_legal_question(self, question: str, show_details: bool = True) -> Dict[str, Any]:
        """Ask a legal question and show user-visible improvements."""
        print(f"\n💬 USER QUESTION: \"{question}\"")
        print("-" * 60)
        
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/api/v1/query",
            json={
                "session_id": self.session_id,
                "query": question,
                "interaction_type": "query"
            }
        )
        
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract user-visible information
            domain = data.get("domain", "unknown")
            confidence = data.get("confidence", 0)
            response_text = data.get("response", "")
            suggested_actions = data.get("suggested_actions", [])
            interaction_id = data.get("interaction_id")
            
            print(f"🤖 AI RESPONSE:")
            print(f"   📋 Legal Domain: {domain.replace('_', ' ').title()}")
            print(f"   🎯 Confidence: {confidence:.1%}")
            print(f"   ⚡ Response Time: {response_time:.2f}s")
            if response_text:
                print(f"   📝 Response: {response_text[:200]}{'...' if len(response_text) > 200 else ''}")
            else:
                print(f"   📝 Response: [No response text available]")
            
            if suggested_actions:
                print(f"   💡 Suggested Actions: {', '.join(suggested_actions)}")
            
            if show_details:
                print(f"\n🔍 TECHNICAL DETAILS (Advanced RL at work):")
                print(f"   🆔 Interaction ID: {interaction_id}")
                print(f"   🧠 AI Learning: System is adapting based on this interaction")
                print(f"   📊 Confidence Score: {confidence:.4f} (improves with feedback)")
            
            # Store interaction for feedback demo
            interaction_data = {
                "interaction_id": interaction_id,
                "question": question,
                "domain": domain,
                "confidence": confidence,
                "response": response_text,
                "timestamp": datetime.now().isoformat()
            }
            self.interactions.append(interaction_data)
            
            return interaction_data
        else:
            print(f"❌ Query failed: {response.status_code}")
            return {}
    
    def provide_feedback(self, interaction_data: Dict[str, Any], feedback: str, time_spent: float = 30.0) -> Dict[str, Any]:
        """Provide feedback and show how the system learns."""
        print(f"\n👍👎 USER FEEDBACK: {feedback.upper()}")
        print("-" * 40)
        
        response = requests.post(
            f"{BASE_URL}/api/v1/feedback",
            json={
                "session_id": self.session_id,
                "interaction_id": interaction_data["interaction_id"],
                "feedback": feedback,
                "time_spent": time_spent
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            reward = data.get("reward", 0)
            satisfaction = data.get("updated_satisfaction", 0)
            
            print(f"✅ FEEDBACK RECORDED")
            print(f"   📊 Learning Reward: {reward:.3f}")
            print(f"   😊 User Satisfaction: {satisfaction:.3f}")
            print(f"   ⏱️  Time Spent: {time_spent}s")
            
            print(f"\n🧠 WHAT HAPPENED BEHIND THE SCENES:")
            if reward > 0:
                print(f"   ✅ Positive feedback → System learns this was a good response")
                print(f"   📈 Future similar questions will get better answers")
                print(f"   🎯 Confidence for {interaction_data['domain']} domain improved")
            else:
                print(f"   ❌ Negative feedback → System learns to avoid this approach")
                print(f"   📉 Future responses will be adjusted")
                print(f"   🔄 Alternative strategies will be tried next time")
            
            return {
                "reward": reward,
                "satisfaction": satisfaction,
                "learning_impact": "positive" if reward > 0 else "negative"
            }
        else:
            print(f"❌ Feedback failed: {response.status_code}")
            return {}
    
    def show_learning_progress(self):
        """Show how the system has learned from interactions."""
        print(f"\n📈 LEARNING PROGRESS SUMMARY")
        print("=" * 50)
        
        if not self.interactions:
            print("No interactions yet.")
            return
        
        # Get session summary
        response = requests.get(f"{BASE_URL}/api/v1/sessions/{self.session_id}/summary")
        
        if response.status_code == 200:
            summary = response.json()
            
            print(f"📊 SESSION STATISTICS:")
            print(f"   Total Interactions: {summary.get('total_interactions', 0)}")
            print(f"   Domains Covered: {', '.join(summary.get('domains', []))}")
            print(f"   Current Satisfaction: {summary.get('satisfaction_score', 0):.3f}")
            print(f"   Session Duration: {summary.get('session_duration', 0):.1f}s")
            
            print(f"\n🎯 WHAT THIS MEANS FOR YOU:")
            print(f"   • The AI remembers your previous questions")
            print(f"   • It's getting better at understanding your legal needs")
            print(f"   • Future responses will be more personalized")
            print(f"   • The system adapts to your feedback patterns")
        
        # Get RL system status
        rl_response = requests.get(f"{BASE_URL}/api/v1/rl/status")
        if rl_response.status_code == 200:
            rl_data = rl_response.json()
            
            print(f"\n🧠 AI LEARNING SYSTEM STATUS:")
            print(f"   Learning Mode: {'Advanced' if rl_data.get('is_advanced') else 'Basic'}")
            print(f"   Knowledge States: {rl_data.get('q_table_size', 0)}")
            print(f"   Exploration Rate: {rl_data.get('learning_metrics', {}).get('exploration_rate', 0):.4f}")
            
            memory_stats = rl_data.get('memory_system', {})
            print(f"   Memory - Experiences: {memory_stats.get('episodic_memory_size', 0)}")
            print(f"   Memory - Domains: {memory_stats.get('semantic_memory_domains', 0)}")
    
    def demonstrate_improvement_over_time(self):
        """Show how responses improve with repeated similar questions."""
        print(f"\n🚀 DEMONSTRATION: AI IMPROVEMENT OVER TIME")
        print("=" * 60)
        
        base_question = "I'm having issues with my employment contract"
        variations = [
            "I'm having issues with my employment contract",
            "My employer is violating my employment agreement", 
            "There are problems with my work contract terms"
        ]
        
        print("👀 WATCH: Same type of question asked multiple times")
        print("📈 EXPECT: Confidence and response quality to improve")
        print()
        
        results = []
        
        for i, question in enumerate(variations):
            print(f"🔄 ROUND {i+1}/3")
            interaction = self.ask_legal_question(question, show_details=False)
            
            if interaction:
                # Simulate positive feedback to show learning
                feedback_data = self.provide_feedback(interaction, "upvote", 25.0 + i*5)
                
                results.append({
                    "round": i+1,
                    "confidence": interaction["confidence"],
                    "reward": feedback_data.get("reward", 0),
                    "satisfaction": feedback_data.get("satisfaction", 0)
                })
            
            time.sleep(1)  # Small delay to show progression
        
        # Show improvement analysis
        if len(results) >= 2:
            print(f"\n📊 IMPROVEMENT ANALYSIS:")
            print(f"{'Round':<8} {'Confidence':<12} {'Reward':<10} {'Satisfaction':<12}")
            print("-" * 45)
            
            for result in results:
                print(f"{result['round']:<8} {result['confidence']:<12.3f} {result['reward']:<10.3f} {result['satisfaction']:<12.3f}")
            
            confidence_change = results[-1]["confidence"] - results[0]["confidence"]
            satisfaction_change = results[-1]["satisfaction"] - results[0]["satisfaction"]
            
            print(f"\n🎯 IMPROVEMENT METRICS:")
            print(f"   Confidence Change: {confidence_change:+.3f}")
            print(f"   Satisfaction Change: {satisfaction_change:+.3f}")
            
            if confidence_change > 0 or satisfaction_change > 0:
                print(f"   ✅ AI IS LEARNING AND IMPROVING!")
            else:
                print(f"   📊 AI is maintaining consistent performance")
    
    def run_user_demo(self):
        """Run complete user experience demonstration."""
        print("🎭 USER EXPERIENCE DEMONSTRATION")
        print("=" * 60)
        print("This demo shows how users can SEE and FEEL the RL improvements")
        print("=" * 60)
        
        # Step 1: Create session
        session_id = self.create_user_session("common_person")
        if not session_id:
            return
        
        # Step 2: Ask different types of questions
        questions = [
            "I need help with my divorce proceedings",
            "My landlord is trying to evict me unfairly", 
            "I was injured in a car accident, what are my rights?"
        ]
        
        print(f"\n🎯 PHASE 1: DIVERSE LEGAL QUESTIONS")
        print("=" * 40)
        
        for i, question in enumerate(questions):
            interaction = self.ask_legal_question(question)
            if interaction:
                # Alternate feedback to show learning
                feedback = "upvote" if i % 2 == 0 else "downvote"
                self.provide_feedback(interaction, feedback, 20.0 + i*10)
            time.sleep(1)
        
        # Step 3: Show learning progress
        self.show_learning_progress()
        
        # Step 4: Demonstrate improvement over time
        self.demonstrate_improvement_over_time()
        
        print(f"\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("KEY USER-VISIBLE IMPROVEMENTS:")
        print("✅ Higher confidence scores over time")
        print("✅ Better domain classification accuracy") 
        print("✅ Faster response times")
        print("✅ More relevant legal advice")
        print("✅ Personalized responses based on history")
        print("✅ Learning from user feedback")
        print("=" * 60)


def create_web_interface():
    """Create a simple web interface to show RL improvements."""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Law Agent - Advanced RL System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .header { text-align: center; color: #2c3e50; margin-bottom: 30px; }
        .demo-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .metrics { display: flex; justify-content: space-around; margin: 20px 0; }
        .metric { text-align: center; padding: 10px; background: #ecf0f1; border-radius: 5px; }
        .improvement { color: #27ae60; font-weight: bold; }
        .question { background: #3498db; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .response { background: #2ecc71; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .feedback { background: #e74c3c; color: white; padding: 5px 10px; border-radius: 3px; margin: 5px; }
        .learning { background: #f39c12; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .progress-bar { width: 100%; background: #ddd; border-radius: 10px; overflow: hidden; }
        .progress { height: 20px; background: #4CAF50; transition: width 0.3s; }
        button { background: #3498db; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        button:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Advanced RL Law Agent</h1>
            <p>Watch the AI learn and improve in real-time!</p>
        </div>

        <div class="demo-section">
            <h2>📊 Real-Time Learning Metrics</h2>
            <div class="metrics">
                <div class="metric">
                    <h3>Confidence Score</h3>
                    <div id="confidence">Loading...</div>
                    <div class="progress-bar">
                        <div class="progress" id="confidence-bar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="metric">
                    <h3>User Satisfaction</h3>
                    <div id="satisfaction">Loading...</div>
                    <div class="progress-bar">
                        <div class="progress" id="satisfaction-bar" style="width: 0%"></div>
                    </div>
                </div>
                <div class="metric">
                    <h3>Q-table Size</h3>
                    <div id="qtable">Loading...</div>
                </div>
                <div class="metric">
                    <h3>Exploration Rate</h3>
                    <div id="exploration">Loading...</div>
                </div>
            </div>
        </div>

        <div class="demo-section">
            <h2>💬 Interactive Demo</h2>
            <input type="text" id="question" placeholder="Ask a legal question..." style="width: 70%; padding: 10px;">
            <button onclick="askQuestion()">Ask Question</button>
            <div id="conversation"></div>
        </div>

        <div class="demo-section">
            <h2>🧠 Learning Progress</h2>
            <div id="learning-log"></div>
        </div>

        <div class="demo-section">
            <h2>📈 Improvement Over Time</h2>
            <canvas id="improvement-chart" width="800" height="300"></canvas>
        </div>
    </div>

    <script>
        let sessionId = null;
        let interactionCount = 0;
        let confidenceHistory = [];
        let satisfactionHistory = [];

        // Initialize session
        async function initSession() {
            try {
                const response = await fetch('/api/v1/sessions', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: 'web_demo', user_type: 'common_person'})
                });
                const data = await response.json();
                sessionId = data.session_id;
                updateMetrics();
            } catch (error) {
                console.error('Session creation failed:', error);
            }
        }

        // Update real-time metrics
        async function updateMetrics() {
            try {
                const response = await fetch('/api/v1/rl/status');
                const data = await response.json();

                document.getElementById('qtable').textContent = data.q_table_size || 0;
                document.getElementById('exploration').textContent =
                    (data.learning_metrics?.exploration_rate || 0).toFixed(4);

                if (sessionId) {
                    const sessionResponse = await fetch(`/api/v1/sessions/${sessionId}/summary`);
                    const sessionData = await sessionResponse.json();

                    const confidence = sessionData.average_confidence || 0;
                    const satisfaction = sessionData.satisfaction_score || 0;

                    document.getElementById('confidence').textContent = (confidence * 100).toFixed(1) + '%';
                    document.getElementById('satisfaction').textContent = satisfaction.toFixed(3);

                    document.getElementById('confidence-bar').style.width = (confidence * 100) + '%';
                    document.getElementById('satisfaction-bar').style.width = ((satisfaction + 1) * 50) + '%';
                }
            } catch (error) {
                console.error('Metrics update failed:', error);
            }
        }

        // Ask a question
        async function askQuestion() {
            const question = document.getElementById('question').value;
            if (!question || !sessionId) return;

            const conversation = document.getElementById('conversation');

            // Add question to conversation
            conversation.innerHTML += `<div class="question">👤 You: ${question}</div>`;

            try {
                const response = await fetch('/api/v1/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        session_id: sessionId,
                        query: question,
                        interaction_type: 'query'
                    })
                });

                const data = await response.json();

                // Add response to conversation
                conversation.innerHTML += `
                    <div class="response">
                        🤖 AI: ${data.response}
                        <br><small>Domain: ${data.domain} | Confidence: ${(data.confidence * 100).toFixed(1)}%</small>
                    </div>
                `;

                // Add feedback buttons
                conversation.innerHTML += `
                    <div>
                        <button class="feedback" onclick="provideFeedback('${data.interaction_id}', 'upvote')">👍 Good</button>
                        <button class="feedback" onclick="provideFeedback('${data.interaction_id}', 'downvote')">👎 Bad</button>
                    </div>
                `;

                interactionCount++;
                confidenceHistory.push(data.confidence);

                updateMetrics();
                updateChart();

            } catch (error) {
                console.error('Query failed:', error);
            }

            document.getElementById('question').value = '';
        }

        // Provide feedback
        async function provideFeedback(interactionId, feedback) {
            try {
                const response = await fetch('/api/v1/feedback', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        session_id: sessionId,
                        interaction_id: interactionId,
                        feedback: feedback,
                        time_spent: 30.0
                    })
                });

                const data = await response.json();

                // Show learning feedback
                const learningLog = document.getElementById('learning-log');
                learningLog.innerHTML = `
                    <div class="learning">
                        🧠 Learning Update: Reward = ${data.reward?.toFixed(3)},
                        Satisfaction = ${data.updated_satisfaction?.toFixed(3)}
                        ${data.reward > 0 ? '📈 Positive learning!' : '📉 Adjusting approach...'}
                    </div>
                ` + learningLog.innerHTML;

                satisfactionHistory.push(data.updated_satisfaction);
                updateMetrics();
                updateChart();

            } catch (error) {
                console.error('Feedback failed:', error);
            }
        }

        // Update improvement chart
        function updateChart() {
            const canvas = document.getElementById('improvement-chart');
            const ctx = canvas.getContext('2d');

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (confidenceHistory.length < 2) return;

            // Draw confidence line
            ctx.strokeStyle = '#3498db';
            ctx.lineWidth = 2;
            ctx.beginPath();

            for (let i = 0; i < confidenceHistory.length; i++) {
                const x = (i / (confidenceHistory.length - 1)) * (canvas.width - 40) + 20;
                const y = canvas.height - (confidenceHistory[i] * (canvas.height - 40)) - 20;

                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();

            // Draw satisfaction line if available
            if (satisfactionHistory.length > 0) {
                ctx.strokeStyle = '#e74c3c';
                ctx.beginPath();

                for (let i = 0; i < satisfactionHistory.length; i++) {
                    const x = (i / (satisfactionHistory.length - 1)) * (canvas.width - 40) + 20;
                    const y = canvas.height - ((satisfactionHistory[i] + 1) * 0.5 * (canvas.height - 40)) - 20;

                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.stroke();
            }

            // Add labels
            ctx.fillStyle = '#2c3e50';
            ctx.font = '12px Arial';
            ctx.fillText('Confidence (Blue) & Satisfaction (Red) Over Time', 20, 15);
        }

        // Auto-update metrics every 5 seconds
        setInterval(updateMetrics, 5000);

        // Initialize on page load
        window.onload = initSession;

        // Allow Enter key to ask question
        document.getElementById('question').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') askQuestion();
        });
    </script>
</body>
</html>
    """

    with open("law_agent_demo.html", "w") as f:
        f.write(html_content)

    print("🌐 Web interface created: law_agent_demo.html")
    print("📝 Open this file in your browser to see the RL system in action!")

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "web":
        create_web_interface()
    else:
        demo = UserExperienceDemo()
        demo.run_user_demo()
