import React, { useState, useRef, useEffect } from "react";
import { Send, BookOpen, FileText, Clock, GraduationCap, PlusCircle } from "lucide-react";
import "./App.css";

const BACKEND_URL = "https://chatbotcmc-production.up.railway.app";

const WELCOME_MESSAGE = {
  role: "bot",
  text: "👋 Welcome to the CMC Fellows Virtual Hub! I can answer questions about OPT, international student FAQs, and CBS resources. How can I help you today?",
  sources: [],
};

function App() {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const startNewChat = () => {
    setMessages([WELCOME_MESSAGE]);
    setInput("");
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userMessage }),
      });
      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data.answer, sources: data.sources },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          text: "Sorry, I couldn't connect to the server. Please make sure the backend is running.",
          sources: [],
        },
      ]);
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const suggestedQuestions = [
    "What is the OPT process?",
    "When should I apply for OPT?",
    "What is STEM OPT extension?",
    "Who do I contact for visa questions?",
  ];

  return (
    <div className="app">
      {/* Top Banner */}
      <div className="top-banner">
        <div className="banner-content">
          <GraduationCap size={28} color="white" />
          <div>
            <h1 className="banner-title">CMC FELLOWS VIRTUAL HUB</h1>
            <p className="banner-subtitle">2025 - 2026 AI Assistant</p>
          </div>
        </div>
      </div>

      <div className="main-layout">
        {/* Left Sidebar */}
        <div className="sidebar">

          {/* New Chat Button */}
          <div className="new-chat-btn" onClick={startNewChat}>
            <PlusCircle size={15} />
            New Chat
          </div>

          <nav className="nav">
            <div className="nav-item active">
              <BookOpen size={18} />
              <span>Home</span>
            </div>
            <div className="nav-item">
              <FileText size={18} />
              <span>OPT Resources</span>
            </div>
            <div className="nav-item">
              <FileText size={18} />
              <span>International FAQs</span>
            </div>
            <div className="nav-item">
              <Clock size={18} />
              <span>Important Dates</span>
            </div>
          </nav>

          <div className="sidebar-divider" />

          <div className="sidebar-section">
            <p className="sidebar-section-title">SUGGESTED QUESTIONS</p>
            {suggestedQuestions.map((q, i) => (
              <div key={i} className="suggestion" onClick={() => setInput(q)}>
                {q}
              </div>
            ))}
          </div>

          <div className="sidebar-divider" />

          <div className="sidebar-section">
            <p className="sidebar-section-title">KNOWLEDGE BASE</p>
            <div className="kb-item">
              <FileText size={12} />
              <span>OPT Process Letter</span>
            </div>
            <div className="kb-item">
              <FileText size={12} />
              <span>International FAQs</span>
            </div>
            <div className="kb-item">
              <FileText size={12} />
              <span>CBS ACE Book</span>
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="chat-area">
          <div className="chat-header">
            <h2>AI Assistant</h2>
            <span className="status-badge">● Online</span>
          </div>

          <div className="messages">
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.role}`}>
                {msg.role === "bot" && (
                  <div className="avatar bot-avatar">AI</div>
                )}
                <div className="message-content">
                  <div className="bubble">{msg.text}</div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="sources">
                      <span className="sources-label">📄 Sources: </span>
                      {msg.sources.map((s, j) => (
                        <span key={j} className="source-tag">
                          {s.replace(".pdf", "").substring(0, 40)}...
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                {msg.role === "user" && (
                  <div className="avatar user-avatar">You</div>
                )}
              </div>
            ))}

            {/* Typing animation */}
            {loading && (
              <div className="message bot">
                <div className="avatar bot-avatar">AI</div>
                <div className="message-content">
                  <div className="bubble typing">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="input-area">
            <textarea
              className="input-box"
              placeholder="Ask a question about OPT, international student resources, or CBS programs..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={2}
            />
            <button
              className="send-btn"
              onClick={sendMessage}
              disabled={loading || !input.trim()}
            >
              <Send size={18} />
            </button>
          </div>
          <p className="input-hint">Press Enter to send · Shift+Enter for new line</p>
        </div>
      </div>
    </div>
  );
}

export default App;