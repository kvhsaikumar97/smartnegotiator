import { useState } from "react";
import axios from "axios";

export default function Login({ onLogin, goRegister }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // ---- Function called when user clicks "Login" ----
  const handleLogin = async () => {
    if (!email || !password) {
      alert("⚠️ Please enter both email and password.");
      return;
    }

    try {
      // ✅ Correct backend port (8080)
      const res = await axios.post("http://127.0.0.1:8080/login", {
        email,
        password,
      });

      if (res.status === 200) {
        alert("✅ Login successful!");
        console.log("🟢 Backend Response:", res.data);

        // Send user data to App.js
        onLogin(res.data.user);
      }
    } catch (err) {
      console.error("❌ Login error:", err);
      if (err.response && err.response.status === 401) {
        alert("❌ Invalid credentials. Please try again.");
      } else if (err.code === "ERR_NETWORK") {
        alert("⚠️ Cannot connect to backend. Make sure backend is running on port 8080.");
      } else {
        alert("⚠️ Server error. Check console for details.");
      }
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: 350,
        margin: "auto",
        marginTop: 100,
        padding: 20,
        borderRadius: 10,
        backgroundColor: "#f5f5f5",
        boxShadow: "0 0 10px rgba(0,0,0,0.1)",
      }}
    >
      <h2 style={{ textAlign: "center", color: "#2563eb" }}>Login</h2>

      {/* Email input */}
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={{
          marginBottom: 10,
          padding: 10,
          borderRadius: 8,
          border: "1px solid #ccc",
        }}
      />

      {/* Password input */}
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{
          marginBottom: 10,
          padding: 10,
          borderRadius: 8,
          border: "1px solid #ccc",
        }}
      />

      {/* Login button */}
      <button
        onClick={handleLogin}
        style={{
          background: "#2563eb",
          color: "white",
          padding: 10,
          border: "none",
          borderRadius: 8,
          cursor: "pointer",
          fontWeight: "bold",
        }}
      >
        Login
      </button>

      {/* Register link */}
      <p style={{ marginTop: 10, textAlign: "center" }}>
        Don’t have an account?{" "}
        <span
          onClick={goRegister}
          style={{
            color: "#2563eb",
            cursor: "pointer",
            textDecoration: "underline",
          }}
        >
          Register
        </span>
      </p>
    </div>
  );
}
