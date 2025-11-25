import { useState } from "react";
import Login from "./Login";
import Register from "./Register";
import Products from "./Products";
import ChatBot from "./ChatBot";

export default function App() {
  const [page, setPage] = useState("login");
  const [user, setUser] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);

  console.log("✅ Current Page:", page);
  console.log("✅ User Data:", user);

  // Step 1 — Handle login success
  if (!user && page === "login") {
    return <Login onLogin={(data) => setUser(data)} goRegister={() => setPage("register")} />;
  }

  // Step 2 — Handle register navigation
  if (!user && page === "register") {
    return <Register onRegister={() => setPage("login")} />;
  }

  // Step 3 — Show products if user logged in
  if (user && !selectedProduct) {
    return <Products user={user} onSelectProduct={setSelectedProduct} />;
  }

  // Step 4 — If product selected, open chat
  if (selectedProduct) {
    return (
      <ChatBot
        user={user}
        product={selectedProduct}
        onBack={() => setSelectedProduct(null)}
      />
    );
  }

  // Fallback
  return <div>Loading...</div>;
}
