# rag_engine.py using LangGraph with improved architecture
import json
import numpy as np
import os
from typing import TypedDict, List, Any, Optional
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define the state schema for LangGraph
class RAGState(TypedDict):
    query: str
    k: int
    q_emb: Optional[List[float]]
    rows: Optional[List[dict]]
    scored: Optional[List[tuple]]
    top: Optional[List[tuple]]
    answer: Optional[str]

class RAGEngine:
    """Enhanced RAG Engine with lazy loading and better error handling"""

    def __init__(self):
        self._model = None
        self._db_manager = None

    @property
    def model(self):
        """Lazy load the sentence transformer model"""
        if self._model is None:
            try:
                logger.info("Loading sentence transformer model...")
                self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
        return self._model

    @property
    def db_manager(self):
        """Lazy load database manager"""
        if self._db_manager is None:
            from backend.config import db_manager
            self._db_manager = db_manager
        return self._db_manager

    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        try:
            return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise

    def cosine_similarity(self, a, b):
        """Calculate cosine similarity between two vectors"""
        try:
            a = np.array(a)
            b = np.array(b)
            if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
                return 0.0
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0

    def fetch_products_with_embeddings(self) -> List[dict]:
        """Fetch products that have embeddings"""
        try:
            query = "SELECT * FROM products WHERE embedding IS NOT NULL"
            return self.db_manager.execute_query(query, fetch=True) or []
        except Exception as e:
            logger.error(f"Failed to fetch products with embeddings: {e}")
            return []

    def score_products(self, state):
        """Score products based on query embedding"""
        try:
            q_emb = state["q_emb"]
            rows = state["rows"]
            scored = []

            for r in rows:
                try:
                    emb = json.loads(r["embedding"])
                    score = self.cosine_similarity(q_emb, emb)
                    scored.append((score, r))
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Skipping product {r.get('id', 'unknown')} due to embedding error: {e}")
                    continue

            scored.sort(key=lambda x: x[0], reverse=True)
            state["scored"] = scored
            return state
        except Exception as e:
            logger.error(f"Error scoring products: {e}")
            state["scored"] = []
            return state

    def select_top_k(self, state):
        """Select top K products"""
        k = state.get("k", 3)
        scored = state["scored"]
        top = scored[:k] if scored else []
        state["top"] = top
        return state

    def format_answer(self, state):
        """Format the final answer"""
        top = state["top"]
        if not top:
            state["answer"] = "No matching products found 😔"
        else:
            best = top[0][1]
            state["answer"] = f"{best['name']} price ₹{best['price']} — {best['description']}"
        return state

    def rebuild_all_product_embeddings(self) -> int:
        """Rebuild embeddings for all products"""
        try:
            query = "SELECT id, name, description, price FROM products"
            rows = self.db_manager.execute_query(query, fetch=True) or []

            updated = 0
            for r in rows:
                try:
                    text = f"{r['name']} Price {r['price']} Description {r['description']}"
                    emb = self.create_embedding(text)
                    emb_json = json.dumps(emb)

                    update_query = "UPDATE products SET embedding = %s WHERE id = %s"
                    self.db_manager.execute_query(update_query, (emb_json, r["id"]))
                    updated += 1

                    if updated % 10 == 0:
                        logger.info(f"Processed {updated} products...")

                except Exception as e:
                    logger.error(f"Failed to process product {r['id']}: {e}")
                    continue

            logger.info(f"Successfully rebuilt embeddings for {updated} products")
            return updated

        except Exception as e:
            logger.error(f"Failed to rebuild embeddings: {e}")
            raise

    def rag_answer(self, query: str, k: int = 3) -> Dict[str, str]:
        """Main RAG pipeline"""
        try:
            # LangGraph pipeline
            sg = StateGraph(RAGState)
            sg.add_node("embed_query", lambda state: {**state, "q_emb": self.create_embedding(state["query"])})
            sg.add_node("fetch_products", lambda state: {**state, "rows": self.fetch_products_with_embeddings()})
            sg.add_node("score", self.score_products)
            sg.add_node("topk", self.select_top_k)
            sg.add_node("format", self.format_answer)

            sg.add_edge("embed_query", "fetch_products")
            sg.add_edge("fetch_products", "score")
            sg.add_edge("score", "topk")
            sg.add_edge("topk", "format")
            sg.add_edge("format", END)
            sg.set_entry_point("embed_query")

            graph = sg.compile()
            state: RAGState = {
                "query": query,
                "k": k,
                "q_emb": None,
                "rows": None,
                "scored": None,
                "top": None,
                "answer": None
            }

            result = graph.invoke(state)
            return {"answer": result["answer"]}

        except Exception as e:
            logger.error(f"RAG pipeline failed: {e}")
            return {"answer": "Sorry, I'm having trouble processing your request right now. Please try again later."}

# Global RAG engine instance
rag_engine = RAGEngine()

# Backward compatibility functions
def create_embedding(text: str):
    return rag_engine.create_embedding(text)

def cosine_sim(a, b):
    return rag_engine.cosine_similarity(a, b)

def fetch_products_with_embeddings():
    return rag_engine.fetch_products_with_embeddings()

def score_products(state):
    return rag_engine.score_products(state)

def select_top_k(state):
    return rag_engine.select_top_k(state)

def format_answer(state):
    return rag_engine.format_answer(state)

def rebuild_all_product_embeddings():
    return rag_engine.rebuild_all_product_embeddings()

def rag_answer(query: str, k: int = 3):
    return rag_engine.rag_answer(query, k)

def load_products_from_csv():
    """Load products from CSV file into database"""
    import csv
    import os

    try:
        # Get the path to the CSV file
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.csv')

        if not os.path.exists(csv_path):
            logger.error(f"CSV file not found: {csv_path}")
            return 0

        loaded = 0
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Map CSV columns to database columns
                    name = row['name']
                    price = float(row['mrp'])  # Use MRP as the selling price
                    description = f"High-quality {name.lower()} with excellent features. MRP: ₹{row['mrp']}, Current Price: ₹{price}"
                    stock = int(row['stock'])

                    # Insert product
                    insert_query = """
                        INSERT INTO products (name, price, description, stock)
                        VALUES (%s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        name=VALUES(name), price=VALUES(price),
                        description=VALUES(description), stock=VALUES(stock)
                    """
                    rag_engine.db_manager.execute_query(insert_query, (name, price, description, stock))
                    loaded += 1

                except Exception as e:
                    logger.error(f"Error processing row {row}: {e}")
                    continue

        logger.info(f"Loaded {loaded} products from CSV")
        return loaded

    except Exception as e:
        logger.error(f"Error loading products: {e}")
        return 0

# Optional: Enhanced RAG with LLM (supports multiple providers)
def rag_answer_with_llm(query: str, k: int = 3, use_llm: bool = False):
    """
    Enhanced RAG that can optionally use LLM for better responses
    Supports OpenAI, Google Gemini, and Anthropic Claude
    Set use_llm=True and provide the appropriate API key in environment
    """
    if use_llm:
        # Get basic RAG answer
        rag_result = rag_answer(query, k)
        base_answer = rag_result["answer"]

        # Try different LLM providers in order of preference
        providers = [
            ("openai", "OPENAI_API_KEY"),
            ("gemini", "GEMINI_API_KEY"),
            ("anthropic", "ANTHROPIC_API_KEY")
        ]

        for provider_name, env_var in providers:
            api_key = os.getenv(env_var)
            if api_key:
                try:
                    return _call_llm_provider(provider_name, api_key, base_answer, query)
                except Exception as e:
                    logger.warning(f"LLM provider {provider_name} failed: {e}")
                    continue  # Try next provider

        return {"error": "No supported LLM API key found. Please set OPENAI_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY"}

    # Fallback to basic RAG
    return rag_answer(query, k)

def _call_llm_provider(provider: str, api_key: str, base_answer: str, query: str):
    """Call the specified LLM provider"""
    prompt = f"""
    Based on the following product information, provide a helpful negotiation response:

    Product Context: {base_answer}

    User Query: {query}

    Provide a natural, persuasive response that helps with price negotiation while being helpful and professional.
    Keep the response conversational and friendly.
    """

    try:
        if provider == "openai":
            import openai
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            return {"answer": response.choices[0].message.content.strip()}

        elif provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')  # Using the latest stable flash model
            response = model.generate_content(prompt)
            return {"answer": response.text.strip()}

        elif provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            return {"answer": response.content[0].text.strip()}

        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

    except Exception as e:
        logger.error(f"Error calling {provider}: {e}")
        raise
