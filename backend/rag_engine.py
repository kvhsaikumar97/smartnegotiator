# rag_engine.py using LangGraph
import json
import numpy as np
import mysql.connector
import os
from typing import TypedDict, List, Any, Optional
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END

# Define the state schema for LangGraph
class RAGState(TypedDict):
    query: str
    k: int
    q_emb: Optional[List[float]]
    rows: Optional[List[dict]]
    scored: Optional[List[tuple]]
    top: Optional[List[tuple]]
    answer: Optional[str]

# Load API keys from environment
def get_api_key(service_name: str, required: bool = False):
    """Safely get API key from environment variables"""
    key = os.getenv(f"{service_name.upper()}_API_KEY")
    if required and not key:
        raise ValueError(f"{service_name.upper()}_API_KEY environment variable is required but not set")
    return key

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
DB_CFG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "smartnegotiator")
}

def get_db():
    return mysql.connector.connect(**DB_CFG)

def create_embedding(text: str):
    return model.encode(text).tolist()

def cosine_sim(a, b):
    a = np.array(a)
    b = np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def fetch_products_with_embeddings():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM products WHERE embedding IS NOT NULL")
    rows = cur.fetchall()
    cur.close()
    db.close()
    return rows

def score_products(state):
    q_emb = state["q_emb"]
    rows = state["rows"]
    scored = []
    for r in rows:
        try:
            emb = json.loads(r["embedding"])
            score = cosine_sim(q_emb, emb)
            scored.append((score, r))
        except Exception:
            continue
    scored.sort(key=lambda x: x[0], reverse=True)
    state["scored"] = scored
    return state

def select_top_k(state):
    k = state.get("k", 3)
    scored = state["scored"]
    top = scored[:k]
    state["top"] = top
    return state

def format_answer(state):
    top = state["top"]
    if not top:
        state["answer"] = "No matching products found 😔"
    else:
        best = top[0][1]
        state["answer"] = f"{best['name']} price ₹{best['price']} — {best['description']}"
    return state

def rebuild_all_product_embeddings():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id,name,description,price FROM products")
    rows = cur.fetchall()
    updated = 0

    for r in rows:
        text = f"{r['name']} Price {r['price']} Description {r['description']}"
        emb = create_embedding(text)
        emb_json = json.dumps(emb)

        cur2 = db.cursor()
        cur2.execute("UPDATE products SET embedding=%s WHERE id=%s", (emb_json, r["id"]))
        cur2.close()
        updated += 1

    db.commit()
    cur.close()
    db.close()
    return updated

def load_products_from_csv():
    """Load products from CSV file into database"""
    import csv
    import os

    db = get_db()
    cur = db.cursor()

    # Get the path to the CSV file
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'products.csv')

    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return 0

    loaded = 0
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Map CSV columns to database columns
                name = row['name']
                price = float(row['mrp'])  # Use MRP as the selling price
                description = f"High-quality {name.lower()} with excellent features. MRP: ₹{row['mrp']}, Current Price: ₹{price}"
                stock = int(row['stock'])

                # Insert product
                cur.execute("""
                    INSERT INTO products (name, price, description, stock)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    name=VALUES(name), price=VALUES(price),
                    description=VALUES(description), stock=VALUES(stock)
                """, (name, price, description, stock))
                loaded += 1

        db.commit()
        print(f"Loaded {loaded} products from CSV")

    except Exception as e:
        print(f"Error loading products: {e}")
        db.rollback()
        loaded = 0

    finally:
        cur.close()
        db.close()

    return loaded

def rag_answer(query: str, k: int = 3):
    # LangGraph pipeline
    sg = StateGraph(RAGState)
    sg.add_node("embed_query", lambda state: {**state, "q_emb": create_embedding(state["query"])})
    sg.add_node("fetch_products", lambda state: {**state, "rows": fetch_products_with_embeddings()})
    sg.add_node("score", score_products)
    sg.add_node("topk", select_top_k)
    sg.add_node("format", format_answer)

    # Set the entry point
    sg.add_edge("embed_query", "fetch_products")
    sg.add_edge("fetch_products", "score")
    sg.add_edge("score", "topk")
    sg.add_edge("topk", "format")
    sg.add_edge("format", END)
    sg.set_entry_point("embed_query")  # Set the starting node

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
    result = graph.invoke(state)  # Use invoke() instead of calling graph directly
    # Always return a dict with 'answer' key for FastAPI compatibility
    return {"answer": result["answer"]}

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
            api_key = get_api_key(env_var.lower().replace("_api_key", ""))
            if api_key:
                try:
                    return _call_llm_provider(provider_name, api_key, base_answer, query)
                except Exception:
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
    """

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
