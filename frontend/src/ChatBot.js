import { useState } from "react";
import axios from "axios";

export default function ChatBot({ user, product, onBack }) {
  const [msg, setMsg] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!msg.trim()) return;

    setChat((prev) => [...prev, { role: "user", text: msg }]);
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8080/chat", {
        message: msg,
        user_email: user.email,
        product_id: product?.id || null,
      });

      setChat((prev) => [...prev, { role: "bot", text: res.data.reply }]);
    } catch (err) {
      console.error(err);
      setChat((prev) => [
        ...prev,
        { role: "bot", text: "⚠️ Model not reachable or server error. Please try again later." },
      ]);
    }

    setMsg("");
    setLoading(false);
  };

  return (
    <div
      style={{
        background: "linear-gradient(135deg, #0f172a, #2563eb, #38bdf8)",
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "Poppins, sans-serif",
        color: "#111827",
      }}
    >
      <div
        style={{
          width: "420px",
          height: "85vh",
          background: "rgba(255, 255, 255, 0.92)",
          backdropFilter: "blur(18px)",
          borderRadius: "25px",
          boxShadow: "0 10px 25px rgba(0,0,0,0.25)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            background: "linear-gradient(90deg, #2563eb, #1e40af)",
            color: "white",
            padding: "15px 20px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <h3 style={{ margin: 0 }}>💙 Kiki Bot</h3>
            <small>Welcome, {user.first_name || user.username || user.email}</small>
          </div>
          <button
            onClick={onBack}
            style={{
              background: "white",
              color: "#2563eb",
              fontWeight: "bold",
              border: "none",
              borderRadius: "8px",
              padding: "5px 10px",
              cursor: "pointer",
            }}
          >
            ← Back
          </button>
        </div>

        {/* Product Info */}
        {product && (
          <div
            style={{
              background: "#f1f5f9",
              padding: "10px",
              textAlign: "center",
              borderBottom: "1px solid #ddd",
            }}
          >
            <img
              src={product.image_url}
              alt={product.name}
              style={{
                width: "100px",
                borderRadius: "10px",
                marginBottom: "5px",
                boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
              }}
            />
            <div style={{ fontWeight: "600" }}>{product.name}</div>
            <div style={{ color: "#2563eb", fontWeight: "bold" }}>₹{product.price}</div>
            <p
              style={{
                color: "gray",
                fontSize: "13px",
                margin: 0,
              }}
            >
              🛍️ You are negotiating about: {product.name}
            </p>
          </div>
        )}

        {/* Chat Messages */}
        <div
          style={{
            flex: 1,
            padding: "15px",
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            background: "rgba(255,255,255,0.5)",
          }}
        >
          {chat.map((c, i) => (
            <div
              key={i}
              style={{
                alignSelf: c.role === "user" ? "flex-end" : "flex-start",
                marginBottom: "12px",
                maxWidth: "80%",
                background:
                  c.role === "user"
                    ? "linear-gradient(135deg, #93c5fd, #2563eb)"
                    : "linear-gradient(135deg, #bbf7d0, #22c55e)",
                color: c.role === "user" ? "white" : "#065f46",
                padding: "10px 14px",
                borderRadius: "14px",
                boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
                wordWrap: "break-word",
                fontSize: "15px",
              }}
            >
              {c.text}
            </div>
          ))}

          {loading && (
            <div
              style={{
                alignSelf: "flex-start",
                background: "rgba(209, 250, 229, 0.8)",
                color: "#166534",
                padding: "8px 14px",
                borderRadius: "14px",
                fontSize: "14px",
              }}
            >
              💬 Kiki is typing...
            </div>
          )}
        </div>

        {/* Input Section */}
        <div
          style={{
            display: "flex",
            padding: "12px",
            borderTop: "1px solid #ddd",
            background: "#f9fafb",
          }}
        >
          <input
            value={msg}
            onChange={(e) => setMsg(e.target.value)}
            placeholder="Type your message..."
            style={{
              flex: 1,
              padding: "10px 14px",
              borderRadius: "12px",
              border: "1px solid #ccc",
              outline: "none",
              fontSize: "15px",
            }}
            onKeyDown={(e) => e.key === "Enter" && send()}
          />
          <button
            onClick={send}
            style={{
              marginLeft: "8px",
              padding: "10px 18px",
              background: loading ? "gray" : "#2563eb",
              color: "white",
              border: "none",
              borderRadius: "12px",
              cursor: loading ? "not-allowed" : "pointer",
              fontWeight: "bold",
              transition: "0.2s",
            }}
            disabled={loading}
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
