import { useEffect, useState } from "react";
import axios from "axios";

export default function Products({ user, onSelectProduct, onLogout }) {
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState("");
  const [filtered, setFiltered] = useState([]);

  // ✅ Fetch products from backend
  useEffect(() => {
    axios
      .get("http://127.0.0.1:8080/products")
      .then((res) => {
        setProducts(res.data.products);
        setFiltered(res.data.products);
      })
      .catch((err) => console.error("❌ Product fetch error:", err));
  }, []);

  // 🔍 Search Filter
  useEffect(() => {
    const term = search.toLowerCase();
    const f = products.filter(
      (p) =>
        p.name.toLowerCase().includes(term) ||
        p.description.toLowerCase().includes(term)
    );
    setFiltered(f);
  }, [search, products]);

  // 🛒 Add to Cart
  const addToCart = async (p) => {
    try {
      await axios.post("http://127.0.0.1:8080/add_to_cart", {
        user_email: user.email,
        product_id: p.id,
        product_name: p.name,
        price: p.price,
        quantity: 1,
      });
      alert(`✅ ${p.name} added to cart!`);
    } catch (err) {
      console.error(err);
      alert("⚠️ Failed to add to cart");
    }
  };

  // 💳 Buy Now
  const buyNow = (p) => {
    alert(`🛍️ Proceeding to buy ${p.name} for ₹${p.price}`);
    // 👉 You can redirect to checkout page here
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "linear-gradient(135deg, rgba(30,58,138,0.9), rgba(56,189,248,0.9))",
        backdropFilter: "blur(10px)",
        padding: "0",
        margin: "0",
        fontFamily: "Poppins, sans-serif",
      }}
    >
      {/* 🌟 Header Bar */}
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "15px 30px",
          background: "rgba(255,255,255,0.15)",
          color: "white",
          position: "sticky",
          top: 0,
          zIndex: 100,
          backdropFilter: "blur(15px)",
          borderBottom: "1px solid rgba(255,255,255,0.2)",
        }}
      >
        <h2 style={{ fontWeight: "600", letterSpacing: "1px" }}>🛍️ SmartDealz</h2>

        {/* 🔍 Search Bar */}
        <div
          style={{
            flex: 1,
            display: "flex",
            justifyContent: "center",
            margin: "0 30px",
          }}
        >
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search products..."
            style={{
              width: "60%",
              padding: "10px 15px",
              borderRadius: "20px",
              border: "none",
              outline: "none",
              fontSize: "15px",
            }}
          />
        </div>

        {/* 👤 Account / Wishlist / Logout */}
        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <span style={{ cursor: "pointer" }}>❤️ Wishlist</span>
          <span style={{ cursor: "pointer" }}>👤 {user.first_name || user.username}</span>
          <button
            onClick={onLogout}
            style={{
              background: "#ef4444",
              color: "white",
              border: "none",
              padding: "8px 15px",
              borderRadius: "10px",
              cursor: "pointer",
              fontWeight: "bold",
            }}
          >
            Logout
          </button>
        </div>
      </header>

      {/* 🌈 Welcome Text */}
      <h2
        style={{
          textAlign: "center",
          color: "white",
          margin: "25px 0 10px",
          fontSize: "26px",
        }}
      >
        Welcome {user.first_name || user.username}! Explore amazing deals 🎉
      </h2>

      {/* 🛒 Product Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "25px",
          padding: "30px",
        }}
      >
        {filtered.length > 0 ? (
          filtered.map((p) => (
            <div
              key={p.id}
              style={{
                background: "rgba(255,255,255,0.15)",
                borderRadius: "15px",
                boxShadow: "0 8px 25px rgba(0,0,0,0.2)",
                padding: "15px",
                textAlign: "center",
                backdropFilter: "blur(20px)",
                color: "white",
                transition: "all 0.3s ease-in-out",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-8px)";
                e.currentTarget.style.boxShadow = "0 10px 30px rgba(0,0,0,0.3)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 8px 25px rgba(0,0,0,0.2)";
              }}
            >
              <img
                src={p.image || "https://via.placeholder.com/250x200?text=No+Image"}
                alt={p.name}
                style={{
                  width: "100%",
                  height: "200px",
                  objectFit: "contain",
                  borderRadius: "10px",
                  background: "rgba(255,255,255,0.1)",
                }}
              />
              <h3 style={{ margin: "10px 0 5px" }}>{p.name}</h3>
              <p style={{ color: "#d1d5db", fontSize: "14px", minHeight: "40px" }}>
                {p.description}
              </p>
              <h4 style={{ color: "#22c55e", marginTop: "5px" }}>₹{p.price}</h4>

              <div style={{ display: "flex", justifyContent: "center", gap: "10px" }}>
                <button
                  style={{
                    background: "#16a34a",
                    color: "white",
                    border: "none",
                    borderRadius: "8px",
                    padding: "8px 14px",
                    cursor: "pointer",
                    fontWeight: "bold",
                  }}
                  onClick={() => buyNow(p)}
                >
                  Buy Now 🛒
                </button>
                <button
                  style={{
                    background: "#2563eb",
                    color: "white",
                    border: "none",
                    borderRadius: "8px",
                    padding: "8px 14px",
                    cursor: "pointer",
                    fontWeight: "bold",
                  }}
                  onClick={() => addToCart(p)}
                >
                  Add to Cart ➕
                </button>
                <button
                  style={{
                    background: "#9333ea",
                    color: "white",
                    border: "none",
                    borderRadius: "8px",
                    padding: "8px 14px",
                    cursor: "pointer",
                    fontWeight: "bold",
                  }}
                  onClick={() => onSelectProduct(p)}
                >
                  Negotiate 💬
                </button>
              </div>
            </div>
          ))
        ) : (
          <p style={{ textAlign: "center", color: "white", gridColumn: "1 / -1" }}>
            😕 No products found
          </p>
        )}
      </div>

      {/* Footer */}
      <footer
        style={{
          marginTop: "30px",
          textAlign: "center",
          color: "rgba(255,255,255,0.8)",
          fontSize: "14px",
          paddingBottom: "20px",
        }}
      >
        © 2025 SmartDealz – Crafted with 💙 by Dinesh
      </footer>
    </div>
  );
}
