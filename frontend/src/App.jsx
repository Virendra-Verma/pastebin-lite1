import { useState } from "react";
import "./App.css";

const API_BASE_URL = "https://backend-lilac-nu-84.vercel.app";

function App() {
  const [content, setContent] = useState("");
  const [url, setUrl] = useState("");
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState(""); // "success" or "error"

  async function createPaste() {
    try {
      const res = await fetch(`${API_BASE_URL}/pastes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content })
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to create paste");
      }

      const data = await res.json();
      const shareBaseUrl = API_BASE_URL || window.location.origin;
      setUrl(`${shareBaseUrl}${data.url}`);
      setMessage("✅ Paste created successfully!");
      setMessageType("success");
      
      // Clear message after 3 seconds
      setTimeout(() => {
        setMessage("");
        setMessageType("");
      }, 3000);
      
    } catch (error) {
      setMessage(`❌ Error: ${error.message}`);
      setMessageType("error");
      
      // Clear message after 5 seconds
      setTimeout(() => {
        setMessage("");
        setMessageType("");
      }, 5000);
    }
  }

  return (
    <div className="page">
      <div className="card">
        <h1>🔥 Pastebin Lite</h1>

        {message && (
          <div className={`alert ${messageType}`}>
            {message}
          </div>
        )}

        <textarea
          placeholder="Paste your text here..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />

        <button onClick={createPaste}>Create Paste</button>

        {url && (
          <p className="result">
            Share link:
            <a href={url} target="_blank">{url}</a>
          </p>
        )}
      </div>
    </div>
  );
}

export default App;
