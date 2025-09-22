import { useState } from "react";
import { sendMessage } from "../api";

function Chatbot() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;
    try {
      const data = await sendMessage(input);
      setResponse(data.answer || "No answer from backend");
    } catch (err) {
      setResponse("⚠️ " + err.message);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>⚖️ Law Agent Chatbot</h2>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask your question..."
        style={{ padding: "8px", width: "300px" }}
      />
      <button onClick={handleSend} style={{ marginLeft: "10px", padding: "8px" }}>
        Send
      </button>
      <div style={{ marginTop: "20px" }}>
        <strong>Response:</strong>
        <p>{response}</p>
      </div>
    </div>
  );
}

export default Chatbot;
