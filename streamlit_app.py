import streamlit as st
import os
import time
from typing import Optional, List, Dict, Any

# Import our service classes
from backend.user_service import UserService
from backend.product_service import ProductService
from backend.conversation_service import ConversationService, NegotiationService
from backend.rag_engine import rag_answer, rag_answer_with_llm, rebuild_all_product_embeddings, load_products_from_csv, analyze_intent_with_llm
from backend.config import Config

# ------------ PAGE CONFIG ------------
st.set_page_config(
    page_title="Smart Negotiator",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------ CUSTOM CSS ------------
st.markdown("""
    <style>
    :root {
        --primary-color: #2563EB;
        --background-color: #F8FAFC;
        --secondary-background-color: #FFFFFF;
        --text-color: #1E293B;
        --font: "Inter", sans-serif;
    }
    
    /* Main Container */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1E293B;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    h1 {
        font-size: 2.2rem;
        margin-bottom: 1.5rem;
    }
    
    /* Card Styling */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
        background-color: transparent;
    }
    
    /* Buttons */
    .stButton button {
        width: 100%;
        border-radius: 6px;
        font-weight: 500;
        border: 1px solid #E2E8F0;
        background-color: white;
        color: #1E293B;
        transition: all 0.2s ease;
    }
    
    .stButton button:hover {
        border-color: #2563EB;
        color: #2563EB;
        background-color: #F8FAFC;
        transform: translateY(-1px);
    }
    
    /* Primary Buttons (using type="primary") */
    .stButton button[kind="primary"] {
        background-color: #2563EB;
        color: white;
        border: none;
    }
    
    .stButton button[kind="primary"]:hover {
        background-color: #1D4ED8;
        color: white;
    }
    
    /* Inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        border-radius: 6px;
        border-color: #E2E8F0;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E2E8F0;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #64748B;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        color: #2563EB;
        border-bottom: 2px solid #2563EB;
    }
    
    /* Product Card Improvements */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        background-color: white;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-color: #CBD5E1;
    }
    
    /* Featured Banner */
    .featured-banner {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ------------ SESSION STATE INITIALIZATION ------------
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'admin_thresholds' not in st.session_state:
    st.session_state.admin_thresholds = {
        'high_stock_threshold': 15,
        'low_stock_threshold': 5,
        'high_discount_rate': 0.15,
        'medium_discount_rate': 0.10,
        'low_discount_rate': 0.05,
        'default_min_price_pct': 0.85
    }

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

def process_chat_message(prompt: str, selected_product_id: Optional[int] = None) -> str:
    """Process user chat message and generate response"""
    
    # 0. Determine context product
    context_product_id = selected_product_id
    if not context_product_id:
        context_product_id = st.session_state.get('last_product_id')
    
    context_product_name = None
    if context_product_id:
        p = ProductService.get_product_by_id(context_product_id)
        if p:
            context_product_name = p['name']

    # 1. Try LLM Intent Analysis (if available)
    llm_intent = analyze_intent_with_llm(prompt, context_product_name)
    
    if llm_intent:
        intent = llm_intent.get('intent')
        user_price = llm_intent.get('price')
        
        if intent == 'greeting':
            return NegotiationService.generate_greeting_response(st.session_state.user['email'])
            
        elif intent == 'add_to_cart':
            if context_product_id:
                product = ProductService.get_product_by_id(context_product_id)
                if product:
                    success = ProductService.add_to_cart(st.session_state.user['email'], context_product_id)
                    if success:
                        return f"✅ I've added {product['name']} to your cart! You can proceed to checkout in the Cart tab."
                    else:
                        return "❌ I couldn't add the item to your cart. Please try again or check the stock."
            else:
                return "Which product would you like to add to your cart?"
                
        elif intent == 'negotiate' and context_product_id:
            product = ProductService.get_product_by_id(context_product_id)
            if product:
                system_offer = NegotiationService.calculate_offer(
                    product['price'], 
                    product['stock'], 
                    product.get('min_price'),
                    **st.session_state.admin_thresholds
                )
                min_acceptable_price = system_offer['offer_price']
                
                if user_price:
                    if user_price >= min_acceptable_price:
                        return f"Regarding {product['name']}: Deal! 🤝 I can accept your offer of ₹{user_price}. You've got a great price!"
                    else:
                        return f"Regarding {product['name']}: I'm afraid ₹{user_price} is too low. The best I can do is ₹{min_acceptable_price} ({(system_offer['discount_percent'])}% off)."
                else:
                    return f"Regarding {product['name']}: {system_offer['message']}"

        elif intent == 'check_stock':
            products = ProductService.get_all_products()
            low_stock_items = [p for p in products if 0 < p['stock'] < 20]
            if low_stock_items:
                items_str = "\n".join([f"- {p['name']} ({p['stock']} left) - ₹{p['price']}" for p in low_stock_items[:5]])
                return f"⚠️ These items are running low on stock:\n{items_str}\n\nGrab them before they're gone!"
            else:
                return "Good news! All our products are well-stocked right now."

        elif intent == 'check_deals':
            products = ProductService.get_all_products()
            # Sort by price for now as a proxy for "deal"
            sorted_products = sorted(products, key=lambda x: x['price'])[:3]
            items_str = "\n".join([f"- {p['name']} - ₹{p['price']}" for p in sorted_products])
            return f"💰 Here are some of our most affordable options:\n{items_str}"

        elif intent == 'check_cart':
            cart_items = ProductService.get_cart_items(st.session_state.user['email'])
            if cart_items:
                items_str = "\n".join([f"- {item['name']} (x{item['quantity']})" for item in cart_items])
                return f"🛒 You have the following items in your cart:\n{items_str}"
            else:
                return "🛒 Your cart is currently empty."

    # --- FALLBACK TO RULE-BASED LOGIC (if LLM unavailable or intent unknown) ---

    # 1. Check for greetings
    if NegotiationService.is_greeting(prompt):
        return NegotiationService.generate_greeting_response(st.session_state.user['email'])

    # 2. Handle negotiation if we have a context product
    # Check if message looks like a price offer (contains numbers) or negotiation keywords
    import re
    # Find all numbers in the prompt
    numbers = re.findall(r'\d+', prompt)
    has_numbers = bool(numbers)
    is_negotiation = NegotiationService.is_negotiation_request(prompt) or (has_numbers and context_product_id)

    if context_product_id and is_negotiation:
        product = ProductService.get_product_by_id(context_product_id)
        if product:
            # Calculate the best offer the system can give, respecting the min_price threshold
            system_offer = NegotiationService.calculate_offer(
                product['price'], 
                product['stock'], 
                product.get('min_price'),
                **st.session_state.admin_thresholds
            )
            min_acceptable_price = system_offer['offer_price']
            
            # Check for walk-away/rejection intent
            walk_away_phrases = ["don't want", "not interested", "keep it", "bye", "cancel", "no thanks", "not giving"]
            if any(phrase in prompt.lower() for phrase in walk_away_phrases):
                 return f"Regarding {product['name']}: I understand. I'm sorry we couldn't reach a deal. The offer of ₹{min_acceptable_price} stands if you change your mind."

            # If user proposed a price, check it
            user_price = None
            if numbers:
                # Assume the largest number is the price (heuristic)
                try:
                    user_price = float(max(numbers, key=lambda x: float(x)))
                except ValueError:
                    pass

            if user_price:
                if user_price >= min_acceptable_price:
                    return f"Regarding {product['name']}: Deal! 🤝 I can accept your offer of ₹{user_price}. You've got a great price!"
                else:
                    return f"Regarding {product['name']}: I'm afraid ₹{user_price} is too low. The best I can do is ₹{min_acceptable_price} ({(system_offer['discount_percent'])}% off)."
            else:
                # Generic negotiation request
                return f"Regarding {product['name']}: {system_offer['message']}"

    # 3. Check for "Add to Cart" intent
    prompt_lower = prompt.lower()
    is_add_to_cart = (
        ("add" in prompt_lower and ("cart" in prompt_lower or "bag" in prompt_lower)) or
        ("buy" in prompt_lower and ("it" in prompt_lower or "this" in prompt_lower or "that" in prompt_lower)) or
        "add it" in prompt_lower or
        "add that" in prompt_lower
    )
    
    if is_add_to_cart:
        if context_product_id:
            product = ProductService.get_product_by_id(context_product_id)
            if product:
                # Add to cart
                # Note: Currently adding at MRP/Listed price. 
                # To support negotiated price, we'd need to pass the negotiated amount here.
                success = ProductService.add_to_cart(st.session_state.user['email'], context_product_id)
                if success:
                    return f"✅ I've added {product['name']} to your cart! You can proceed to checkout in the Cart tab."
                else:
                    return "❌ I couldn't add the item to your cart. Please try again or check the stock."
        else:
            return "Which product would you like to add to your cart?"

    # 4. Handle Special Queries (Fallback if LLM fails)
    # This ensures the app works even if API keys are missing or rate limited
    if ("low" in prompt_lower and "stock" in prompt_lower) or "running out" in prompt_lower:
        products = ProductService.get_all_products()
        low_stock_items = [p for p in products if 0 < p['stock'] < 20]
        if low_stock_items:
            items_str = "\n".join([f"- {p['name']} ({p['stock']} left) - ₹{p['price']}" for p in low_stock_items[:5]])
            return f"⚠️ These items are running low on stock:\n{items_str}\n\nGrab them before they're gone!"
        else:
            return "Good news! All our products are well-stocked right now."

    if "deal" in prompt_lower or "cheap" in prompt_lower or "promotion" in prompt_lower or "offer" in prompt_lower:
        products = ProductService.get_all_products()
        sorted_products = sorted(products, key=lambda x: x['price'])[:3]
        items_str = "\n".join([f"- {p['name']} - ₹{p['price']}" for p in sorted_products])
        return f"💰 Here are some of our most affordable options:\n{items_str}"

    if "cart" in prompt_lower and ("my" in prompt_lower or "in" in prompt_lower or "show" in prompt_lower or "view" in prompt_lower or "what" in prompt_lower):
        cart_items = ProductService.get_cart_items(st.session_state.user['email'])
        if cart_items:
            items_str = "\n".join([f"- {item['name']} (x{item['quantity']})" for item in cart_items])
            return f"🛒 You have the following items in your cart:\n{items_str}"
        else:
            return "🛒 Your cart is currently empty."

    if "help" in prompt_lower or "what can you do" in prompt_lower or "capabilities" in prompt_lower or "assist" in prompt_lower:
        return """👋 I'm Kiki, your AI shopping assistant! Here's what I can do:
        
1. **Find Products**: Ask me about "headphones", "laptops", or "best deals".
2. **Check Stock**: Ask "what is low on stock?"
3. **Negotiate**: I can negotiate prices! Try making an offer on a product.
4. **Manage Cart**: Ask to "show my cart" or "add this to cart".
5. **Product Details**: Ask specific questions about any item.

How can I help you today?"""

    # 5. Use RAG for general queries or product questions
    query_context = prompt
    if context_product_id:
        product = ProductService.get_product_by_id(context_product_id)
        if product:
            # If the prompt is very short/ambiguous, add product context
            # But if it's a full search query, let it be
            if len(prompt.split()) < 5:
                query_context = f"Regarding {product['name']}: {prompt}"

    # Use RAG engine with LLM enhancement
    result = rag_answer_with_llm(query_context, use_llm=True)
    
    if result and result.get('answer'):
        # Update context if a product was found
        if result.get('product_id'):
            st.session_state['last_product_id'] = result['product_id']
        return result['answer']
    
    return "I'm not sure about that. Could you please be more specific?"

# ------------ SIDEBAR NAVIGATION ------------
st.sidebar.title("Smart Negotiator")

if st.session_state.user:
    st.sidebar.write(f"Logged in as: **{st.session_state.user['email']}**")
    
    # Cart Summary in Sidebar
    cart_count = len(ProductService.get_cart_items(st.session_state.user['email']))
    st.sidebar.metric("Items in Cart", cart_count)

    # Navigation menu
    pages = ['Products', 'Chat', 'Cart', 'Orders']
    page_map = {
        'Products': 'products',
        'Chat': 'chat',
        'Cart': 'cart',
        'Orders': 'orders'
    }

    selected_page = st.sidebar.radio("Navigate", pages, label_visibility="collapsed")
    st.session_state.page = page_map[selected_page]

    # Admin actions (if user is admin - you can extend this)
    st.sidebar.divider()
    with st.sidebar.expander("Admin Tools"):
        if st.button("Rebuild Embeddings", help="Rebuild product embeddings for better search"):
            with show_loading_spinner("Rebuilding embeddings..."):
                count = rebuild_all_product_embeddings()
                st.success(f"Rebuilt embeddings for {count} products")

        if st.button("Load Products", help="Load products from CSV file"):
            with show_loading_spinner("Loading products..."):
                count = load_products_from_csv()
                st.success(f"Loaded {count} products from CSV")

        st.markdown("---")
        st.markdown("### Negotiation Rules")
        
        with st.form("threshold_config"):
            high_stock = st.number_input("High Stock Level (>)", value=st.session_state.admin_thresholds['high_stock_threshold'])
            low_stock = st.number_input("Low Stock Level (<=)", value=st.session_state.admin_thresholds['low_stock_threshold'])
            
            high_disc = st.slider("High Stock Discount", 0.0, 0.5, st.session_state.admin_thresholds['high_discount_rate'])
            med_disc = st.slider("Med Stock Discount", 0.0, 0.5, st.session_state.admin_thresholds['medium_discount_rate'])
            low_disc = st.slider("Low Stock Discount", 0.0, 0.5, st.session_state.admin_thresholds['low_discount_rate'])
            
            min_price = st.slider("Min Price Floor (% of MRP)", 0.5, 1.0, st.session_state.admin_thresholds['default_min_price_pct'])
            
            if st.form_submit_button("Update Rules"):
                st.session_state.admin_thresholds.update({
                    'high_stock_threshold': high_stock,
                    'low_stock_threshold': low_stock,
                    'high_discount_rate': high_disc,
                    'medium_discount_rate': med_disc,
                    'low_discount_rate': low_disc,
                    'default_min_price_pct': min_price
                })
                st.success("Rules updated!")

    if st.sidebar.button("Logout", type="primary"):
        st.session_state.user = None
        st.session_state.page = 'login'
        clear_messages()
        st.rerun()
else:
    st.session_state.page = 'login'

# ------------ LOGIN PAGE ------------
if st.session_state.page == 'login':
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>Smart Negotiator</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748B;'>Your AI-powered shopping assistant</p>", unsafe_allow_html=True)
        st.divider()

        # Show success message if redirected from registration
        if st.session_state.get('registration_success'):
            st.success("Registration successful! Please login with your new credentials.")
            st.session_state.registration_success = False

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="Your password")
                
                st.markdown("") # Spacer
                submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

                if submitted:
                    if not email or not password:
                        st.error("Please fill in all fields")
                    else:
                        with show_loading_spinner("Logging in..."):
                            user = UserService.authenticate_user(email, password)
                            if user:
                                st.session_state.user = user
                                st.toast(f"Welcome back, {user['first_name']}!")
                                time.sleep(1)
                                switch_page('products')
                            else:
                                st.error("Invalid email or password")

        with tab2:
            with st.form("register_form"):
                c1, c2 = st.columns(2)
                with c1:
                    first_name = st.text_input("First Name")
                    username = st.text_input("Username")
                    phone = st.text_input("Phone")
                with c2:
                    last_name = st.text_input("Last Name")
                    email = st.text_input("Email")
                    pincode = st.text_input("Pincode")

                address = st.text_area("Address", height=80)
                password = st.text_input("Password", type="password")

                st.markdown("") # Spacer
                submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

                if submitted:
                    # Client-side validation
                    if not all([first_name, last_name, username, email, phone, password]):
                        st.error("Please fill in all required fields")
                    else:
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
                                st.session_state.registration_success = True
                                switch_page('login')

# ------------ PRODUCTS PAGE ------------
elif st.session_state.page == 'products':
    st.title("Our Products")
    
    # Load products first
    with show_loading_spinner("Loading products..."):
        products = ProductService.get_all_products()

    # Featured Product Banner
    if products:
        import random
        # Pick a random high-stock item as featured
        high_stock_items = [p for p in products if p['stock'] > 10]
        featured = random.choice(high_stock_items) if high_stock_items else random.choice(products)
        
        with st.container():
            st.markdown(f"""
            <div style="background: linear-gradient(to right, #EFF6FF, #FFFFFF); padding: 2rem; border-radius: 12px; border: 1px solid #BFDBFE; margin-bottom: 2rem;">
                <div style="display: flex; align-items: center; gap: 2rem;">
                    <div style="flex: 1;">
                        <span style="background-color: #2563EB; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">FEATURED DROP</span>
                        <h2 style="color: #1E293B; margin-top: 1rem; margin-bottom: 0.5rem;">{featured['name']}</h2>
                        <p style="color: #64748B; font-size: 1.1rem; margin-bottom: 1.5rem;">{featured['description']}</p>
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <span style="font-size: 1.5rem; font-weight: 700; color: #2563EB;">₹{featured['price']}</span>
                            <span style="color: #16A34A; background-color: #DCFCE7; padding: 4px 12px; border-radius: 6px; font-size: 0.9rem; font-weight: 500;">In Stock</span>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Search and Filter Bar
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        search_term = st.text_input("Search", placeholder="Search for laptops, headphones...", label_visibility="collapsed")
    with c2:
        sort_by = st.selectbox("Sort", ["Newest", "Price: Low to High", "Price: High to Low"], label_visibility="collapsed")
    with c3:
        category_filter = st.selectbox("Category", ["All", "Electronics", "Accessories"], label_visibility="collapsed")

    st.markdown("---")

    if not products:
        st.info("No products found. Try adjusting your search.")
    else:
        # Filter logic
        filtered_products = products
        if search_term:
            filtered_products = [
                p for p in products
                if search_term.lower() in p['name'].lower() or search_term.lower() in p['description'].lower()
            ]
        
        # Sort logic
        if sort_by == "Price: Low to High":
            filtered_products.sort(key=lambda x: x['price'])
        elif sort_by == "Price: High to Low":
            filtered_products.sort(key=lambda x: x['price'], reverse=True)

        # Grid Layout
        cols = st.columns(3)
        for i, product in enumerate(filtered_products):
            with cols[i % 3]:
                with st.container(border=True):
                    # Image Area (Fixed Height Placeholder if no image)
                    if product.get('image'):
                        st.image(product['image'], use_container_width=True)
                    else:
                        st.markdown(
                            f'<div style="height: 160px; background-color: #F1F5F9; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #94A3B8; margin-bottom: 1rem;">No Image</div>',
                            unsafe_allow_html=True
                        )

                    # Product Info
                    st.markdown(f"#### {product['name']}")
                    st.caption(f"{product['description'][:60]}..." if len(product['description']) > 60 else product['description'])
                    
                    # Price and Stock Row
                    p1, p2 = st.columns([1, 1])
                    with p1:
                        st.markdown(f"**₹{product['price']}**")
                    with p2:
                        if product['stock'] > 10:
                            st.markdown(f"<div style='text-align: right; color: #16A34A; font-size: 0.9rem;'>● In Stock</div>", unsafe_allow_html=True)
                        elif product['stock'] > 0:
                            st.markdown(f"<div style='text-align: right; color: #EA580C; font-size: 0.9rem;'>● {product['stock']} left</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='text-align: right; color: #DC2626; font-size: 0.9rem;'>● Sold Out</div>", unsafe_allow_html=True)

                    st.markdown("") # Spacer
                    
                    # Action Buttons
                    b1, b2 = st.columns([1, 3])
                    with b1:
                        # Quick view / Details (using expander for now)
                        with st.popover("ℹ️"):
                            st.markdown(f"### {product['name']}")
                            st.write(product['description'])
                            st.info(f"Stock Level: {product['stock']} units")
                    with b2:
                        if st.button("Add to Cart", key=f"add_{product['id']}", type="primary", use_container_width=True):
                            with show_loading_spinner("Adding..."):
                                success = ProductService.add_to_cart(
                                    st.session_state.user['email'],
                                    product['id']
                                )
                                if success:
                                    st.toast(f"Added {product['name']} to cart!")
                                    time.sleep(0.5)
                                    st.rerun()

# ------------ CHAT PAGE ------------
elif st.session_state.page == 'chat':
    st.title("Chat with Kiki")
    st.markdown("Your AI shopping assistant - ask anything about our products!")

    # Product selection
    products = ProductService.get_all_products()
    product_options = {None: "General Chat"} | {p['id']: f"{p['name']}" for p in products}
    selected_product = st.selectbox(
        "Select a product to discuss (optional)",
        options=list(product_options.keys()),
        format_func=lambda x: product_options[x]
    )

    # Display chat history
    chat_container = st.container(height=400)
    with chat_container:
        if not st.session_state.messages:
            st.info("Hi! I'm Kiki. Ask me about products, prices, or check your cart!")
        
        for msg in st.session_state.messages:
            avatar = None # Use default icons or none for cleaner look
            with st.chat_message(msg['role'], avatar=avatar):
                st.write(msg['content'])

    def process_user_input(user_text):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_text})
        with chat_container:
            with st.chat_message("user"):
                st.write(user_text)

        # Save user message
        ConversationService.save_message(
            st.session_state.user['email'],
            selected_product,
            "user",
            user_text
        )

        # Process response
        with chat_container:
            with st.chat_message("assistant"):
                # Simulate typing effect
                message_placeholder = st.empty()
                message_placeholder.markdown("typing...")
                time.sleep(0.5) # Fake delay for realism
                
                with st.spinner("Thinking..."):
                    response = process_chat_message(user_text, selected_product)
                
                # Typewriter effect
                full_response = ""
                for chunk in response.split():
                    full_response += chunk + " "
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.05)
                message_placeholder.markdown(full_response)

        # Save bot message
        st.session_state.messages.append({"role": "assistant", "content": response})
        ConversationService.save_message(
            st.session_state.user['email'],
            selected_product,
            "bot",
            response
        )

    # Quick Actions
    st.caption("Quick Suggestions:")
    q1, q2, q3, q4 = st.columns(4)
    if q1.button("Best Deals", use_container_width=True):
        process_user_input("What are your best deals today?")
    if q2.button("Low Stock", use_container_width=True):
        process_user_input("Which items are running low on stock?")
    if q3.button("Help", use_container_width=True):
        process_user_input("How can you help me?")
    if q4.button("My Cart", use_container_width=True):
        process_user_input("What is in my cart?")

    # Chat input
    if prompt := st.chat_input("Ask me anything about our products..."):
        process_user_input(prompt)

    # Clear chat button
    if st.button("Clear Chat"):
        clear_messages()
        st.rerun()

# ------------ CART PAGE ------------
elif st.session_state.page == 'cart':
    st.title("Your Shopping Cart")

    # Load cart items
    with show_loading_spinner("Loading cart..."):
        cart_items = ProductService.get_cart_items(st.session_state.user['email'])

    if not cart_items:
        st.info("Your cart is empty. Browse our products to add items!")
        if st.button("Browse Products"):
            switch_page('products')
    else:
        # Cart Table
        total_amount = 0
        
        with st.container(border=True):
            st.markdown("### Order Summary")
            for item in cart_items:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.markdown(f"**{item['name']}**")
                    st.caption(item['description'][:50] + "...")
                with col2:
                    st.markdown(f"₹{item['price']}")
                with col3:
                    st.markdown(f"x {item['quantity']}")
                with col4:
                    subtotal = item['price'] * item['quantity']
                    st.markdown(f"**₹{subtotal}**")
                    total_amount += subtotal
                st.divider()
            
            # Total
            t1, t2 = st.columns([4, 1])
            with t2:
                st.markdown(f"### Total: ₹{total_amount}")

        # Checkout Actions
        c1, c2 = st.columns([1, 4])
        with c1:
            if st.button("Clear Cart"):
                # Logic to clear cart would go here
                st.warning("Feature coming soon!")
        with c2:
            if st.button("Proceed to Checkout", type="primary", use_container_width=True):
                with st.spinner("Processing payment..."):
                    time.sleep(2)
                    st.balloons()
                    st.success(f"Order placed successfully! Total paid: ₹{total_amount}")
                    # Here you would clear the cart in DB
                    time.sleep(2)
                    switch_page('products')

# ------------ ORDERS PAGE ------------
elif st.session_state.page == 'orders':
    st.title("Your Orders")
    
    # Mock orders for demonstration since we don't have an orders table yet
    st.info("This is a demo of the Orders page.")
    
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader("Order #ORD-2024-001")
            st.caption("Placed on Dec 24, 2025")
            st.write("• Sony WH-1000XM5 (x1)")
            st.write("• MacBook Air M2 (x1)")
        with c2:
            st.markdown("### ₹1,14,999")
            st.markdown(":green[Delivered]")
            if st.button("Track", key="track_1"):
                st.toast("Tracking info sent to email!")

    st.markdown("")
    
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader("Order #ORD-2024-002")
            st.caption("Placed on Dec 20, 2025")
            st.write("• iPhone 15 Pro (x1)")
        with c2:
            st.markdown("### ₹1,34,900")
            st.markdown(":blue[Shipped]")
            if st.button("Track", key="track_2"):
                st.toast("Tracking info sent to email!")

# ------------ FOOTER ------------
st.divider()
st.caption("Powered by AI • Built with Streamlit • © 2025 Smart Negotiator")
