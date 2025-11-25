import { useState } from "react";
import axios from "axios";

export default function Register({ onRegister }) {
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    username: "",
    email: "",
    phone: "",
    address: "",
    pincode: "",
    password: "",
    re_password: "",
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleRegister = async () => {
    if (form.password !== form.re_password) {
      alert("⚠️ Passwords do not match!");
      return;
    }

    try {
      // ✅ Correct backend port: 8080
      const res = await axios.post("http://127.0.0.1:8080/register", {
        first_name: form.first_name,
        last_name: form.last_name,
        username: form.username,
        email: form.email,
        phone: form.phone,
        address: form.address,
        pincode: form.pincode,
        password: form.password,
      });

      if (res.status === 200) {
        alert("✅ Registration successful! Please login.");
        onRegister();
      }
    } catch (err) {
      console.error("❌ Registration Error:", err);
      if (err.response) {
        alert(`Registration failed: ${err.response.data.detail || "Unknown error"}`);
      } else {
        alert("⚠️ Could not connect to the backend. Please check if the server is running on port 8080.");
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
        marginTop: 50,
        padding: 20,
        borderRadius: 10,
        backgroundColor: "#f5f5f5",
        boxShadow: "0 0 10px rgba(0,0,0,0.1)",
      }}
    >
      <h2 style={{ textAlign: "center", color: "#16a34a" }}>Create Account</h2>

      {[
        ["First Name", "first_name"],
        ["Last Name", "last_name"],
        ["Username", "username"],
        ["Email", "email"],
        ["Phone", "phone"],
        ["Address", "address"],
        ["Pincode", "pincode"],
        ["Password", "password"],
        ["Re-enter Password", "re_password"],
      ].map(([label, name], idx) => (
        <input
          key={idx}
          name={name}
          placeholder={label}
          type={name.includes("password") ? "password" : "text"}
          value={form[name]}
          onChange={handleChange}
          style={{
            marginBottom: 10,
            padding: 10,
            borderRadius: 8,
            border: "1px solid #ccc",
          }}
        />
      ))}

      <button
        onClick={handleRegister}
        style={{
          background: "#16a34a",
          color: "white",
          padding: 10,
          border: "none",
          borderRadius: 8,
          cursor: "pointer",
          fontWeight: "bold",
        }}
      >
        Register
      </button>

      <p style={{ marginTop: 10, textAlign: "center" }}>
        Already have an account?{" "}
        <span
          onClick={onRegister}
          style={{ color: "#16a34a", cursor: "pointer", textDecoration: "underline" }}
        >
          Login
        </span>
      </p>
    </div>
  );
}
