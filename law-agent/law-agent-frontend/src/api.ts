// src/api.js
import API_URL from "./config";

// Function to send a message to backend
export async function sendMessage(message: string) {
  const res = await fetch(`${API_URL}/api/ultimate-analysis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: message }),
  });

  if (!res.ok) {
    throw new Error("Backend error: " + res.status);
  }

  return res.json();
}

// Function to submit feedback
export async function submitFeedback(query: string, domain: string, subdomain: string, confidence: number, feedback: string, rating: number) {
  const res = await fetch(`${API_URL}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ 
      query,
      domain,
      subdomain,
      confidence,
      feedback,
      rating
    }),
  });

  if (!res.ok) {
    throw new Error("Feedback error: " + res.status);
  }

  return res.json();
}