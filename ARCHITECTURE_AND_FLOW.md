# 🏗️ Smart Negotiator - Architecture & Process Flow

This document outlines the technical architecture, component interactions, and detailed process flows of the Smart Negotiator application.

## 1. System Architecture

The application follows a **Service-Oriented Architecture (SOA)** pattern, built primarily with Python and Streamlit, containerized with Docker.

```mermaid
graph TD
    User[User Interface] -->|Interacts| Streamlit[Streamlit App]
    
    subgraph "Frontend Layer"
        Streamlit -->|Render| Pages[Pages: Login, Products, Chat, Cart, Orders]
        Streamlit -->|Admin| AdminTools[Admin Sidebar]
    end
    
    subgraph "Backend Services Layer"
        Streamlit -->|Calls| UserService[User Service]
        Streamlit -->|Calls| ProductService[Product Service]
        Streamlit -->|Calls| NegService[Negotiation Service]
        Streamlit -->|Calls| RAGEngine[RAG Engine]
    end
    
    subgraph "Data Layer"
        UserService -->|SQL| DB[(MySQL Database)]
        ProductService -->|SQL| DB
        NegService -->|SQL| DB
        RAGEngine -->|Vector Search| Chroma[(ChromaDB)]
    end
    
    subgraph "AI Layer"
        RAGEngine -->|API| LLM[LLM Provider (Gemini/OpenAI)]
        RAGEngine -->|Fallback| RuleEngine[Rule-Based Logic]
    end
```

## 2. Component Breakdown

### **A. Frontend (Streamlit)**
*   **`streamlit_app.py`**: The main entry point. It handles routing, session state management, and UI rendering.
*   **Session State**: Manages user login status (`st.session_state.user`), cart contents, chat history, and admin configuration (`st.session_state.admin_thresholds`).
*   **UI Components**:
    *   **Modern Design**: Uses custom CSS for a clean, e-commerce look (no emojis, professional color palette).
    *   **Dynamic Sidebar**: Context-aware sidebar showing cart count and admin tools.

### **B. Backend Services**
*   **`user_service.py`**: Handles authentication (Login/Register) and password hashing (PBKDF2).
*   **`product_service.py`**: Manages product catalog, cart operations (Add/Remove), and order processing.
    *   *Recent Update*: `get_cart_items` now performs a SQL JOIN to fetch real-time product details (image, description) alongside cart quantities.
*   **`conversation_service.py`**: Manages chat history and the core negotiation logic.
    *   *Recent Update*: `calculate_offer` now accepts dynamic thresholds for stock and discount rates, allowing admin configuration.
*   **`rag_engine.py`**: The brain of the chatbot.
    *   **Intent Analysis**: Uses LLM to determine if the user wants to buy, negotiate, or check stock.
    *   **RAG (Retrieval Augmented Generation)**: 
        *   **Embeddings**: Generated using `sentence-transformers/all-MiniLM-L6-v2`.
        *   **Storage**: Embeddings are stored in **ChromaDB** (Vector Database) for efficient similarity search.
        *   **Search**: Performs vector similarity search using ChromaDB's HNSW index.
    *   **Fallback Mechanism**: If the LLM API fails (Quota/Key errors), it gracefully falls back to keyword matching and SQL queries.

### **C. Database**
*   **MySQL**: Stores relational data (Users, Products, Cart, Orders).
*   **ChromaDB**: Stores vector embeddings for products to enable semantic search.

---

## 3. Step-by-Step Process Flows

### **Flow 1: User Login & Session Initialization**
1.  **User Input**: User enters email/password on the Login tab.
2.  **Authentication**: `UserService.authenticate_user` hashes the input password and compares it with the stored hash in MySQL.
3.  **Session Setup**: On success, `st.session_state.user` is populated.
4.  **Config Load**: The app initializes `st.session_state.admin_thresholds` with default values (e.g., High Stock > 15, Max Discount 15%).

### **Flow 2: Product Discovery (RAG & Search)**
1.  **User Action**: User types "Show me cheap headphones" in the Chat or Search bar.
2.  **Intent Analysis**:
    *   **Attempt 1 (LLM)**: `rag_engine.py` sends the prompt to Gemini/OpenAI to classify intent.
    *   **Fallback**: If LLM fails, regex checks for keywords like "cheap", "headphones".
3.  **Retrieval**:
    *   **Vector Search**: The query is embedded using `sentence-transformers`. The system queries **ChromaDB** to find the most similar products based on semantic meaning.
    *   **SQL Search**: Alternatively, keyword search is performed on the MySQL `products` table.
4.  **Response**: The system returns a list of matching products or a conversational answer.

### **Flow 3: The Negotiation Loop**
This is the core "Smart" feature.

1.  **Initiation**: User says "Can I get a discount on the Sony headphones?" or "I'll pay ₹20,000".
2.  **Context Check**: The system identifies the `context_product_id` (the product currently being discussed).
3.  **Offer Calculation (`NegotiationService.calculate_offer`)**:
    *   **Inputs**: Product Price, Current Stock, Admin Thresholds (High/Low Stock limits).
    *   **Logic**:
        *   If Stock > `High Stock Threshold`: Allow aggressive discount (e.g., up to 15%).
        *   If Stock < `Low Stock Threshold`: Allow minimal/no discount (e.g., 5%).
        *   **Floor Price**: Never go below `Min Price Floor` (default 85% of MRP).
4.  **Decision**:
    *   **Accept**: If User Offer >= Calculated Minimum Acceptable Price.
    *   **Counter-Offer**: If User Offer < Minimum, the system proposes the Minimum Acceptable Price.
    *   **Reject**: If the user refuses the counter-offer.

### **Flow 4: Admin Configuration (Dynamic Rules)**
1.  **Access**: Admin expands "⚙️ Admin Tools" in the sidebar.
2.  **Modification**: Admin changes "High Stock Discount" from 15% to 20%.
3.  **Update**: Clicking "Update Rules" updates `st.session_state.admin_thresholds`.
4.  **Effect**: The *next* negotiation calculation immediately uses the new 20% limit without restarting the server.

### **Flow 5: Cart & Checkout**
1.  **Add to Cart**: User clicks "Add to Cart" or asks the bot.
2.  **Validation**: `ProductService` checks stock availability in MySQL.
3.  **Update**: Item is added to the `cart` table.
4.  **View Cart**: `ProductService.get_cart_items` performs a JOIN query:
    ```sql
    SELECT c.*, p.name, p.image, p.description 
    FROM cart c JOIN products p ON c.product_id = p.id
    ```
    This ensures the UI always shows the latest product details.
5.  **Checkout**: Order is created in `orders` table, cart is cleared, and stock is deducted (logic to be implemented).

## 4. Key Technical Improvements

### **Resilience (The "Safety Net")**
The system is designed to never crash, even if the AI brain is lobotomized.
*   **Scenario**: Gemini API Key expires.
*   **Result**: The app switches to "Rule-Based Mode". It uses regex to detect "buy", "price", "stock" keywords and queries the database directly. The user still gets an answer, just less conversational.

### **Dynamic Configuration**
Hardcoded values (like "15% discount") have been moved to Session State. This allows business users (Admins) to tweak the negotiation strategy in real-time based on inventory pressure, without needing a developer to deploy code changes.
