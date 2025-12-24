# rag_engine.py using LangGraph with improved architecture and ChromaDB
import json
import numpy as np
import os
from typing import TypedDict, List, Any, Optional, Dict
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END
import logging
import chromadb
from chromadb.config import Settings

# Configure logging
logger = logging.getLogger(__name__)

# Define the state schema for LangGraph
class RAGState(TypedDict):
    query: str
    k: int
    q_emb: Optional[List[float]]
    results: Optional[Dict[str, Any]]
    answer: Optional[str]
    best_product_id: Optional[int]

class RAGEngine:
    """Enhanced RAG Engine with ChromaDB vector storage"""

    def __init__(self):
        self._model = None
        self._db_manager = None
        self._chroma_client = None
        self._collection = None
        
        # Ensure vectordb directory exists
        self.persist_directory = os.path.join(os.path.dirname(__file__), '..', 'vectordb')
        os.makedirs(self.persist_directory, exist_ok=True)

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

    @property
    def chroma_client(self):
        """Lazy load ChromaDB client"""
        if self._chroma_client is None:
            try:
                logger.info(f"Initializing ChromaDB client at {self.persist_directory}")
                self._chroma_client = chromadb.PersistentClient(path=self.persist_directory)
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB client: {e}")
                raise
        return self._chroma_client

    @property
    def collection(self):
        """Lazy load ChromaDB collection"""
        if self._collection is None:
            try:
                self._collection = self.chroma_client.get_or_create_collection(
                    name="products",
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                logger.error(f"Failed to get/create collection: {e}")
                raise
        return self._collection

    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text"""
        try:
            return self.model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Failed to create embedding: {e}")
            raise

    def query_vector_db(self, state):
        """Query ChromaDB for similar products"""
        try:
            query_text = state["query"]
            k = state.get("k", 3)
            
            # Generate embedding for the query
            query_embedding = self.create_embedding(query_text)
            state["q_emb"] = query_embedding
            
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=["metadatas", "documents", "distances"]
            )
            
            state["results"] = results
            return state
        except Exception as e:
            logger.error(f"Error querying vector DB: {e}")
            state["results"] = None
            return state

    def format_answer(self, state):
        """Format the final answer from vector DB results"""
        results = state["results"]
        
        if not results or not results['ids'] or len(results['ids'][0]) == 0:
            state["answer"] = "No matching products found 😔"
            state["best_product_id"] = None
        else:
            # Get the best match (first item)
            best_id = results['ids'][0][0]
            best_metadata = results['metadatas'][0][0]
            best_doc = results['documents'][0][0]
            
            state["answer"] = f"{best_metadata['name']} price ₹{best_metadata['price']} — {best_metadata['description']}"
            state["best_product_id"] = int(best_id)
            
        return state

    def rebuild_all_product_embeddings(self) -> int:
        """Rebuild embeddings for all products and store in ChromaDB"""
        try:
            logger.info("Starting to rebuild product embeddings in ChromaDB...")
            
            # Fetch all products from MySQL
            query = "SELECT id, name, description, price, image, stock FROM products"
            rows = self.db_manager.execute_query(query, fetch=True) or []

            if not rows:
                logger.warning("No products found in database to index.")
                return 0

            ids = []
            embeddings = []
            metadatas = []
            documents = []

            for r in rows:
                try:
                    # Create text representation for embedding
                    text = f"{r['name']} Price {r['price']} Description {r['description']}"
                    emb = self.create_embedding(text)
                    
                    ids.append(str(r['id']))
                    embeddings.append(emb)
                    metadatas.append({
                        "name": r['name'],
                        "price": float(r['price']),
                        "description": r['description'],
                        "image": r['image'] or "",
                        "stock": int(r['stock'])
                    })
                    documents.append(text)

                except Exception as e:
                    logger.error(f"Failed to process product {r['id']}: {e}")
                    continue

            # Add to ChromaDB (upsert handles updates)
            if ids:
                self.collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents
                )
                logger.info(f"Successfully indexed {len(ids)} products in ChromaDB")
                return len(ids)
            
            return 0

        except Exception as e:
            logger.error(f"Failed to rebuild embeddings: {e}")
            raise

    def rag_answer(self, query: str, k: int = 3) -> Dict[str, str]:
        """Main RAG pipeline"""
        try:
            # LangGraph pipeline
            sg = StateGraph(RAGState)
            sg.add_node("query_db", self.query_vector_db)
            sg.add_node("format", self.format_answer)

            sg.add_edge("query_db", "format")
            sg.add_edge("format", END)
            sg.set_entry_point("query_db")

            graph = sg.compile()
            state: RAGState = {
                "query": query,
                "k": k,
                "q_emb": None,
                "results": None,
                "answer": None,
                "best_product_id": None
            }

            result = graph.invoke(state)
            return {
                "answer": result["answer"],
                "product_id": result.get("best_product_id")
            }

        except Exception as e:
            logger.error(f"RAG pipeline failed: {e}")
            return {"answer": "Sorry, I'm having trouble processing your request right now. Please try again later."}

# Global RAG engine instance
rag_engine = RAGEngine()

# Backward compatibility functions
def create_embedding(text: str):
    return rag_engine.create_embedding(text)

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
                    cost_price = float(row['cost_price'])
                    min_margin = float(row['min_margin_pct'])
                    
                    # Calculate minimum acceptable price (Cost + Margin)
                    min_price = cost_price * (1 + min_margin / 100)
                    
                    description = f"High-quality {name.lower()} with excellent features. MRP: ₹{row['mrp']}, Current Price: ₹{price}"
                    stock = int(row['stock'])
                    image = row.get('image', '')

                    # Insert product
                    insert_query = """
                        INSERT INTO products (name, price, min_price, description, stock, image)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        name=VALUES(name), price=VALUES(price), min_price=VALUES(min_price),
                        description=VALUES(description), stock=VALUES(stock), image=VALUES(image)
                    """
                    rag_engine.db_manager.execute_query(insert_query, (name, price, min_price, description, stock, image))
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

        # If all LLMs fail, fall back to basic RAG result
        logger.warning("All LLM providers failed or no keys found. Falling back to basic RAG.")
        return rag_result

    # Fallback to basic RAG
    return rag_answer(query, k)

def analyze_intent_with_llm(query: str, context_product: str = None) -> Dict[str, Any]:
    """
    Analyze user intent using LLM
    Returns: {
        "intent": "negotiate" | "add_to_cart" | "greeting" | "info" | "unknown",
        "price": float | None,
        "confidence": float
    }
    """
    providers = [
        ("openai", "OPENAI_API_KEY"),
        ("gemini", "GEMINI_API_KEY"),
        ("anthropic", "ANTHROPIC_API_KEY")
    ]

    for provider_name, env_var in providers:
        api_key = os.getenv(env_var)
        if api_key:
            try:
                prompt = f"""
                Analyze the following user message in the context of an e-commerce chat.
                Context Product: {context_product or 'None'}
                User Message: "{query}"

                Determine the user's intent and extract any price offers.
                Possible intents:
                - negotiate: User wants to buy for a lower price, asks for discount, or proposes a price.
                - add_to_cart: User wants to buy the item, add to cart, or checkout.
                - check_stock: User asks about stock availability, low stock, or what's left.
                - check_deals: User asks for best prices, deals, promotions, or cheap items.
                - check_cart: User asks to see their cart or what they have added.
                - greeting: User is saying hello/hi.
                - info: User is asking for product details or general questions.
                - unknown: Unclear intent.

                Return ONLY a JSON object in this format:
                {{
                    "intent": "string",
                    "price": float or null (if user proposed a price),
                    "confidence": float (0.0 to 1.0)
                }}
                """
                
                response_text = ""
                if provider_name == "openai":
                    from openai import OpenAI
                    client = OpenAI(api_key=api_key)
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0,
                        response_format={"type": "json_object"}
                    )
                    response_text = response.choices[0].message.content
                    
                elif provider_name == "gemini":
                    import google.generativeai as genai
                    genai.configure(api_key=api_key)
                    
                    # Try models in order of preference/quota availability
                    gemini_models = ['gemini-2.0-flash', 'gemini-flash-latest', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro-latest', 'gemini-pro']
                    response = None
                    last_error = None
                    
                    for model_name in gemini_models:
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(prompt)
                            break # Success
                        except Exception as e:
                            last_error = e
                            continue
                    
                    if not response:
                        raise last_error or Exception("All Gemini models failed")

                    response_text = response.text
                    # Clean up markdown code blocks if present
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0]
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0]

                elif provider_name == "anthropic":
                    import anthropic
                    client = anthropic.Anthropic(api_key=api_key)
                    response = client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=300,
                        temperature=0,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    response_text = response.content[0].text

                # Parse JSON
                try:
                    return json.loads(response_text.strip())
                except:
                    logger.error(f"Failed to parse LLM JSON response: {response_text}")
                    continue

            except Exception as e:
                logger.warning(f"LLM intent analysis failed with {provider_name}: {e}")
                continue

    return None

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
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            return {"answer": response.choices[0].message.content.strip()}

        elif provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            
            # Try models in order of preference/quota availability
            gemini_models = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            response = None
            last_error = None
            
            for model_name in gemini_models:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    break # Success
                except Exception as e:
                    last_error = e
                    continue
            
            if not response:
                raise last_error or Exception("All Gemini models failed")
                
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
