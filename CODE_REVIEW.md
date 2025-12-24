# Code Review & Analysis

## 1. Architecture Overview
The application has successfully migrated to a more robust architecture using **ChromaDB** for vector storage. This replaces the previous "Naive RAG" approach of storing JSON embeddings in MySQL.

### Key Improvements:
- **Scalability**: Vector search is now handled by a dedicated engine (ChromaDB) rather than in-memory cosine similarity of all rows.
- **Performance**: HNSW indexing in ChromaDB provides much faster retrieval times as the dataset grows.
- **Maintainability**: Separation of concerns - MySQL for relational data, ChromaDB for semantic data.

## 2. Code Quality Findings

### ✅ Strengths
- **Service-Oriented**: Clear separation of logic into `UserService`, `ProductService`, `ConversationService`, and `RAGEngine`.
- **Lazy Loading**: The `RAGEngine` lazy loads heavy models (SentenceTransformer) and database clients, improving startup time.
- **Configuration**: Use of environment variables and a central `config.py` for database connections.
- **Security**: Password hashing using PBKDF2 is implemented correctly.

### ⚠️ Areas for Improvement

#### 1. Dead Code
- **File**: `backend/product_service.py`
- **Method**: `get_products_with_embeddings()`
- **Issue**: This method queries `WHERE embedding IS NOT NULL` from MySQL. Since we migrated to ChromaDB, this column is likely obsolete or secondary. The method appears unused in the current codebase.
- **Recommendation**: Remove this method to avoid confusion.

#### 2. Error Handling in Chat
- **File**: `backend/conversation_service.py`
- **Method**: `save_message`
- **Issue**: Exceptions are caught and printed to `stdout` (`print(f"Failed to save message: {e}")`).
- **Recommendation**: Use the configured `logger` instead of `print` to ensure errors are captured in production logs.

#### 3. Hardcoded Negotiation Defaults
- **File**: `backend/conversation_service.py`
- **Method**: `calculate_offer`
- **Issue**: Default thresholds (e.g., `high_stock_threshold=15`) are hardcoded in the function signature.
- **Recommendation**: While these can be overridden, consider moving these defaults to `config.py` or a database settings table to allow changing defaults without code deployment.

#### 4. Frontend/Backend Coupling
- **File**: `streamlit_app.py`
- **Issue**: The frontend directly imports backend service classes.
- **Recommendation**: This is acceptable for a Streamlit app, but as the app grows, consider exposing backend logic via a REST API (FastAPI/Flask) to decouple the UI completely.

## 3. Next Steps
1.  **Cleanup**: Remove the unused `embedding` column from MySQL `products` table in a future migration to save space.
2.  **Logging**: Standardize logging across all services (replace `print` with `logger`).
3.  **Testing**: Add unit tests for `RAGEngine` to verify ChromaDB interactions without needing the full app running.
