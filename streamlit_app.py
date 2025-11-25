import streamlit as st
import hashlib
import mysql.connector
from deep_translator import GoogleTranslator
from backend.rag_engine import rag_answer, rag_answer_with_llm, rebuild_all_product_embeddings

# ------------ CONFIG ------------
import os
DB_CFG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "smartnegotiator")
}

# ------------ DB UTIL ------------
def get_db():
    try:
        return mysql.connector.connect(**DB_CFG)
    except mysql.connector.Error as err:
        st.error(f"Database connection failed: {err}")
        st.stop()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ------------ TRANSLATION ------------
def detect_language(text: str):
    if any("\u0C00" <= ch <= "\u0C7F" for ch in text):
        return "te"
    return "en"

def translate_text(text: str, src: str, dest: str):
    if src == dest:
        return text
    try:
        return GoogleTranslator(source=src, target=dest).translate(text)
    except Exception:
        return text

# ------------ HELPER FUNCTIONS ------------
def get_products():
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT id,name FROM products")
        products = cur.fetchall()
        cur.close()
        db.close()
        return products
    except Exception:
        return []

def save_message(user_email: str, product_id: int | None, role: str, message: str):
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO conversations(user_email,product_id,role,message) VALUES(%s,%s,%s,%s)",
                    (user_email, product_id, role, message))
        db.commit()
        cur.close()
        db.close()
    except Exception:
        pass  # Silently fail for now

# ------------ SESSION STATE ------------
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# ------------ SIDEBAR NAVIGATION ------------
st.sidebar.title("Smart Negotiator")
if st.session_state.user:
    st.sidebar.write(f"Logged in as: {st.session_state.user['email']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.page = 'login'
        st.rerun()
    pages = ['Products', 'Chat', 'Cart', 'Orders']
    page = st.sidebar.selectbox("Navigate", pages)
    st.session_state.page = page.lower()
else:
    st.session_state.page = 'login'

# ------------ LOGIN PAGE ------------
if st.session_state.page == 'login':
    st.title("Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                db = get_db()
                cur = db.cursor(dictionary=True)
                cur.execute("SELECT id,first_name,last_name,username,email,phone,address,pincode FROM users WHERE email=%s AND password=%s", (email, hash_pw(password)))
                user = cur.fetchone()
                cur.close()
                db.close()
                if user:
                    st.session_state.user = user
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    with tab2:
        with st.form("register_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            address = st.text_area("Address")
            pincode = st.text_input("Pincode")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Register")
            if submitted:
                db = get_db()
                cur = db.cursor()
                cur.execute("SELECT 1 FROM users WHERE email=%s OR username=%s", (email, username))
                if cur.fetchone():
                    st.error("User already exists")
                else:
                    cur.execute("""INSERT INTO users(first_name,last_name,username,email,phone,address,pincode,password)
                                   VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""",
                                (first_name, last_name, username, email, phone, address, pincode, hash_pw(password)))
                    db.commit()
                    st.success("Registration successful! Please login.")
                cur.close()
                db.close()

# ------------ PRODUCTS PAGE ------------
elif st.session_state.page == 'products':
    st.title("Products")
    if st.button("Rebuild Embeddings"):
        with st.spinner("Rebuilding..."):
            count = rebuild_all_product_embeddings()
            st.success(f"Rebuilt embeddings for {count} products")

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT id,name,description,price,image,stock FROM products")
    products = cur.fetchall()
    cur.close()
    db.close()

    for p in products:
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if p['image']:
                    st.image(p['image'], width=100)
            with col2:
                st.subheader(p['name'])
                st.write(f"Price: ₹{p['price']}")
                st.write(p['description'])
                st.write(f"Stock: {p['stock']}")
            with col3:
                if st.button(f"Add to Cart {p['id']}", key=f"add_{p['id']}"):
                    db = get_db()
                    cur = db.cursor()
                    cur.execute("INSERT INTO cart(user_email,product_id,product_name,price,quantity) VALUES(%s,%s,%s,%s,%s)",
                                (st.session_state.user['email'], p['id'], p['name'], p['price'], 1))
                    db.commit()
                    cur.close()
                    db.close()
                    st.success("Added to cart!")

# ------------ CHAT PAGE ------------
elif st.session_state.page == 'chat':
    st.title("Chat with Kiki Bot")
    product_id = st.selectbox("Select Product (optional)", [None] + [p['id'] for p in get_products()], format_func=lambda x: f"Product {x}" if x else "General Chat")

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg['role']):
            st.write(msg['content'])

    if prompt := st.chat_input("Say something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Save user message
        save_message(st.session_state.user['email'], product_id, "user", prompt)

        # Process response
        lm = prompt.lower()
        gset = ["hi","hello","hey","good morning","good evening","hai","namaste"]
        if any(g in lm for g in gset):
            response = f"Kiki Bot 🤖: Hey {st.session_state.user['email']}! 👋 Ela unna? Nenu miku help chestha."
        elif product_id and any(x in lm for x in ["discount","offer","cheap","less","taggesthava","reduce","price","negotiate","nego"]):
            # Negotiation logic
            db = get_db()
            cur = db.cursor(dictionary=True)
            cur.execute("SELECT name,price,stock,description FROM products WHERE id=%s", (product_id,))
            product = cur.fetchone()
            cur.close()
            db.close()
            if product:
                price = float(product["price"])
                stock = int(product["stock"] or 0)
                if stock > 15:
                    offer = round(price * 0.9, 2)
                    response = f"Kiki Bot 🤖: Stock baaga undi 😄 — I can give ₹{offer} final."
                elif 5 < stock <= 15:
                    offer = round(price * 0.95, 2)
                    response = f"Kiki Bot 🤖: Stock limited 😅 — ok ₹{offer} final."
                else:
                    response = "Kiki Bot 🤖: Stock chala takkuva 😬 — cannot reduce price."
            else:
                response = "Kiki Bot 🤖: Product not found."
        else:
            try:
                # Check if any LLM API key is available for enhanced responses
                available_keys = [
                    os.getenv("OPENAI_API_KEY"),
                    os.getenv("GEMINI_API_KEY"),
                    os.getenv("ANTHROPIC_API_KEY")
                ]
                use_llm = any(key for key in available_keys if key)

                if use_llm:
                    rag_out = rag_answer_with_llm(prompt, k=3, use_llm=True)
                else:
                    rag_out = rag_answer(prompt, k=3)

                if "error" in rag_out:
                    response = f"Kiki Bot 🤖: {rag_out['error']}"
                else:
                    response = rag_out["answer"]
            except Exception as e:
                response = f"Kiki Bot 🤖: Sorry, AI not reachable right now. Error: {str(e)}"

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

        # Save bot message
        save_message(st.session_state.user['email'], product_id, "bot", response)

# ------------ CART PAGE ------------
elif st.session_state.page == 'cart':
    st.title("Your Cart")
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM cart WHERE user_email=%s", (st.session_state.user['email'],))
    cart = cur.fetchall()
    cur.close()
    db.close()

    if cart:
        total = sum(float(i["price"]) * int(i.get("quantity", 1)) for i in cart)
        st.write(f"Total: ₹{total}")
        for item in cart:
            st.write(f"{item['product_name']} - ₹{item['price']} x {item['quantity']}")
        if st.button("Place Order"):
            db = get_db()
            cur = db.cursor()
            cur.execute("INSERT INTO orders(user_email,total) VALUES(%s,%s)", (st.session_state.user['email'], total))
            db.commit()
            cur.execute("DELETE FROM cart WHERE user_email=%s", (st.session_state.user['email'],))
            db.commit()
            cur.close()
            db.close()
            st.success("Order placed!")
            st.rerun()
    else:
        st.write("Your cart is empty.")

# ------------ HELPER FUNCTIONS ------------
def get_products():
    try:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT id,name FROM products")
        products = cur.fetchall()
        cur.close()
        db.close()
        return products
    except Exception:
        return []

def save_message(user_email: str, product_id: int | None, role: str, message: str):
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("INSERT INTO conversations(user_email,product_id,role,message) VALUES(%s,%s,%s,%s)",
                    (user_email, product_id, role, message))
        db.commit()
        cur.close()
        db.close()
    except Exception:
        pass  # Silently fail for now
