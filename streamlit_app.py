import streamlit as st
import os
from typing import Optional, List, Dict, Any

# Import our service classes
from backend.user_service import UserService
from backend.product_service import ProductService
from backend.conversation_service import ConversationService, NegotiationService
from backend.rag_engine import rag_answer, rag_answer_with_llm, rebuild_all_product_embeddings, load_products_from_csv
from backend.config import Config

# ------------ PAGE CONFIG ------------
st.set_page_config(
    page_title="Smart Negotiator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------ SESSION STATE INITIALIZATION ------------
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'messages' not in st.session_state:
    st.session_state.messages = []

# ------------ UTILITY FUNCTIONS ------------
def switch_page(page_name: str):
    """Safely switch pages"""
    st.session_state.page = page_name.lower()
    st.rerun()

def clear_messages():
    """Clear chat messages"""
    st.session_state.messages = []

def show_loading_spinner(text: str = "Processing..."):
    """Show a loading spinner"""
    return st.spinner(text)

# ------------ SIDEBAR NAVIGATION ------------
st.sidebar.title("🤖 Smart Negotiator")

if st.session_state.user:
    st.sidebar.write(f"👤 Logged in as: **{st.session_state.user['email']}**")

    # Navigation menu
    pages = ['🏠 Products', '💬 Chat', '🛒 Cart', '📦 Orders']
    page_map = {
        '🏠 Products': 'products',
        '💬 Chat': 'chat',
        '🛒 Cart': 'cart',
        '📦 Orders': 'orders'
    }

    selected_page = st.sidebar.radio("Navigate", pages, label_visibility="collapsed")
    st.session_state.page = page_map[selected_page]

    # Admin actions (if user is admin - you can extend this)
    st.sidebar.divider()
    if st.sidebar.button("🔄 Rebuild Embeddings", help="Rebuild product embeddings for better search"):
        with show_loading_spinner("Rebuilding embeddings..."):
            count = rebuild_all_product_embeddings()
            st.sidebar.success(f"✅ Rebuilt embeddings for {count} products")

    if st.sidebar.button("📥 Load Products", help="Load products from CSV file"):
        with show_loading_spinner("Loading products..."):
            count = load_products_from_csv()
            st.sidebar.success(f"✅ Loaded {count} products from CSV")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.page = 'login'
        clear_messages()
        st.rerun()
else:
    st.session_state.page = 'login'

# ------------ LOGIN PAGE ------------
if st.session_state.page == 'login':
    st.title("🔐 Welcome to Smart Negotiator")
    st.markdown("Your AI-powered shopping assistant for smart negotiations! 🛍️🤖")

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        st.subheader("Login to your account")
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="your@email.com")
            password = st.text_input("🔒 Password", type="password", placeholder="Your password")

            col1, col2 = st.columns([1, 4])
            with col1:
                submitted = st.form_submit_button("🚀 Login", use_container_width=True)

            if submitted:
                if not email or not password:
                    st.error("❌ Please fill in all fields")
                else:
                    with show_loading_spinner("Logging in..."):
                        user = UserService.authenticate_user(email, password)
                        if user:
                            st.session_state.user = user
                            st.success(f"✅ Welcome back, {user['first_name']}!")
                            switch_page('products')
                        else:
                            st.error("❌ Invalid email or password")

    with tab2:
        st.subheader("Create your account")
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("👤 First Name")
                username = st.text_input("🔖 Username")
                phone = st.text_input("📱 Phone", placeholder="+91XXXXXXXXXX")
            with col2:
                last_name = st.text_input("👤 Last Name")
                email = st.text_input("📧 Email", placeholder="your@email.com")
                address = st.text_area("🏠 Address", height=100)

            password = st.text_input("🔒 Password", type="password")
            pincode = st.text_input("📍 Pincode")

            submitted = st.form_submit_button("📝 Register", use_container_width=True)

            if submitted:
                user_data = {
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'address': address,
                    'pincode': pincode,
                    'password': password
                }

                with show_loading_spinner("Creating account..."):
                    success = UserService.register_user(user_data)
                    if success:
                        switch_page('login')

# ------------ PRODUCTS PAGE ------------
elif st.session_state.page == 'products':
    st.title("🏪 Our Products")
    st.markdown("Discover amazing products with AI-powered recommendations!")

    # Load products
    with show_loading_spinner("Loading products..."):
        products = ProductService.get_all_products()

    if not products:
        st.warning("⚠️ No products available. Please load products from CSV first.")
    else:
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Search products", placeholder="Type to search...")
        with col2:
            sort_by = st.selectbox("Sort by", ["Name", "Price: Low to High", "Price: High to Low"])

        # Filter products
        filtered_products = products
        if search_term:
            filtered_products = [
                p for p in products
                if search_term.lower() in p['name'].lower() or search_term.lower() in p['description'].lower()
            ]

        # Sort products
        if sort_by == "Price: Low to High":
            filtered_products.sort(key=lambda x: x['price'])
        elif sort_by == "Price: High to Low":
            filtered_products.sort(key=lambda x: x['price'], reverse=True)

        st.markdown(f"📊 Showing {len(filtered_products)} of {len(products)} products")

        # Display products in a grid
        cols = st.columns(3)
        for i, product in enumerate(filtered_products):
            with cols[i % 3]:
                with st.container():
                    # Product image placeholder
                    if product.get('image'):
                        st.image(product['image'], use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x200?text=Product", use_column_width=True)

                    st.subheader(f"📦 {product['name']}")
                    st.markdown(f"**₹{product['price']}**")
                    st.caption(product['description'][:100] + "..." if len(product['description']) > 100 else product['description'])
                    st.caption(f"📦 Stock: {product['stock']}")

                    if st.button(f"🛒 Add to Cart", key=f"add_{product['id']}", use_container_width=True):
                        with show_loading_spinner("Adding to cart..."):
                            success = ProductService.add_to_cart(
                                st.session_state.user['email'],
                                product['id']
                            )
                            if success:
                                st.success("✅ Added to cart!")
                                st.rerun()

# ------------ CHAT PAGE ------------
elif st.session_state.page == 'chat':
    st.title("💬 Chat with Kiki Bot")
    st.markdown("Your AI shopping assistant - ask anything about our products!")

    # Product selection
    products = ProductService.get_all_products()
    product_options = {None: "💬 General Chat"} | {p['id']: f"📦 {p['name']}" for p in products}
    selected_product = st.selectbox(
        "Select a product to discuss (optional)",
        options=list(product_options.keys()),
        format_func=lambda x: product_options[x]
    )

    # Display chat history
    chat_container = st.container(height=400)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

    # Chat input
    if prompt := st.chat_input("💭 Ask me anything about our products..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)

        # Save user message
        ConversationService.save_message(
            st.session_state.user['email'],
            selected_product,
            "user",
            prompt
        )

        # Process response
        with chat_container:
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    response = process_chat_message(prompt, selected_product)

                st.write(response)

        # Save bot message
        st.session_state.messages.append({"role": "assistant", "content": response})
        ConversationService.save_message(
            st.session_state.user['email'],
            selected_product,
            "bot",
            response
        )

    # Clear chat button
    if st.button("🗑️ Clear Chat"):
        clear_messages()
        st.rerun()

# ------------ CART PAGE ------------
elif st.session_state.page == 'cart':
    st.title("🛒 Your Shopping Cart")

    # Load cart items
    with show_loading_spinner("Loading cart..."):
        cart_items = ProductService.get_cart_items(st.session_state.user['email'])

    if not cart_items:
        st.info("🛒 Your cart is empty. Browse our products to add items!")
        if st.button("🏪 Browse Products"):
            switch_page('products')
    else:
        total = ProductService.calculate_cart_total(cart_items)

        # Cart summary
        st.subheader("📋 Cart Summary")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{len(cart_items)} items**")
        with col2:
            st.markdown(f"**Total: ₹{total:.2f}**")

        # Display cart items
        for item in cart_items:
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.markdown(f"**📦 {item['product_name']}**")
                with col2:
                    st.markdown(f"₹{item['price']}")
                with col3:
                    st.markdown(f"Qty: {item['quantity']}")
                with col4:
                    if st.button("❌ Remove", key=f"remove_{item['id']}"):
                        with show_loading_spinner("Removing..."):
                            success = ProductService.remove_from_cart(item['id'], st.session_state.user['email'])
                            if success:
                                st.success("✅ Removed from cart!")
                                st.rerun()

        st.divider()

        # Checkout
        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            if st.button("🗑️ Clear Cart", use_container_width=True):
                if st.confirm("Are you sure you want to clear your cart?"):
                    with show_loading_spinner("Clearing cart..."):
                        success = ProductService.clear_cart(st.session_state.user['email'])
                        if success:
                            st.success("✅ Cart cleared!")
                            st.rerun()

        with col3:
            if st.button("💳 Place Order", use_container_width=True, type="primary"):
                with show_loading_spinner("Placing order..."):
                    success = ProductService.place_order(st.session_state.user['email'], cart_items)
                    if success:
                        st.balloons()
                        st.success("🎉 Order placed successfully!")
                        st.rerun()

# ------------ ORDERS PAGE ------------
elif st.session_state.page == 'orders':
    st.title("📦 Your Orders")

    # Load orders
    with show_loading_spinner("Loading orders..."):
        orders = ProductService.get_user_orders(st.session_state.user['email'])

    if not orders:
        st.info("📭 No orders yet. Start shopping to place your first order!")
        if st.button("🏪 Start Shopping"):
            switch_page('products')
    else:
        for order in orders:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Order #{order['id']}**")
                    st.caption(f"📅 {order['created_at']}")
                with col2:
                    st.markdown(f"**₹{order['total']:.2f}**")
                st.divider()

# ------------ CHAT PROCESSING FUNCTION ------------
def process_chat_message(message: str, product_id: Optional[int]) -> str:
    """Process chat messages and generate responses"""
    try:
        # Check for greetings
        if NegotiationService.is_greeting(message):
            return NegotiationService.generate_greeting_response(st.session_state.user['email'])

        # Check for negotiation requests
        if product_id and NegotiationService.is_negotiation_request(message):
            return NegotiationService.process_negotiation_request(product_id, st.session_state.user['email'])

        # Use AI for general queries
        available_llms = Config.get_available_llm_providers()
        if available_llms:
            result = rag_answer_with_llm(message, k=3, use_llm=True)
            if "error" in result:
                # Fallback to basic RAG
                result = rag_answer(message, k=3)
        else:
            result = rag_answer(message, k=3)

        return result.get("answer", "Sorry, I couldn't process your request.")

    except Exception as e:
        st.error(f"Chat processing error: {str(e)}")
        return "🤖 Sorry, I'm having trouble processing your message right now. Please try again!"

# ------------ FOOTER ------------
st.divider()
st.caption("🤖 Powered by AI • Built with Streamlit • © 2025 Smart Negotiator")

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
