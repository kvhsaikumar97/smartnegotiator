from typing import List, Dict, Any, Optional
import streamlit as st
from backend.config import db_manager

class ConversationService:
    """Service class for conversation/chat management"""

    @staticmethod
    def save_message(user_email: str, product_id: Optional[int], role: str, message: str) -> bool:
        """Save a chat message to database"""
        try:
            query = """
                INSERT INTO conversations (user_email, product_id, role, message)
                VALUES (%s, %s, %s, %s)
            """
            db_manager.execute_query(query, (user_email, product_id, role, message))
            return True
        except Exception as e:
            # Log error but don't show to user for chat messages
            print(f"Failed to save message: {e}")
            return False

    @staticmethod
    def get_conversation_history(user_email: str, product_id: Optional[int] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for user and optional product"""
        try:
            if product_id:
                query = """
                    SELECT * FROM conversations
                    WHERE user_email = %s AND (product_id = %s OR product_id IS NULL)
                    ORDER BY created_at DESC LIMIT %s
                """
                params = (user_email, product_id, limit)
            else:
                query = """
                    SELECT * FROM conversations
                    WHERE user_email = %s
                    ORDER BY created_at DESC LIMIT %s
                """
                params = (user_email, limit)

            result = db_manager.execute_query(query, params, fetch=True) or []
            # Reverse to get chronological order
            return list(reversed(result))
        except Exception as e:
            st.error(f"Failed to load conversation history: {str(e)}")
            return []

    @staticmethod
    def get_recent_conversations(user_email: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations grouped by product"""
        try:
            query = """
                SELECT product_id, MAX(created_at) as last_message, COUNT(*) as message_count
                FROM conversations
                WHERE user_email = %s
                GROUP BY product_id
                ORDER BY last_message DESC
                LIMIT %s
            """
            return db_manager.execute_query(query, (user_email, limit), fetch=True) or []
        except Exception as e:
            st.error(f"Failed to load recent conversations: {str(e)}")
            return []

    @staticmethod
    def clear_conversation(user_email: str, product_id: Optional[int] = None) -> bool:
        """Clear conversation history"""
        try:
            if product_id:
                query = "DELETE FROM conversations WHERE user_email = %s AND product_id = %s"
                params = (user_email, product_id)
            else:
                query = "DELETE FROM conversations WHERE user_email = %s"
                params = (user_email,)

            db_manager.execute_query(query, params)
            return True
        except Exception as e:
            st.error(f"Failed to clear conversation: {str(e)}")
            return False

class NegotiationService:
    """Service for handling negotiation logic"""

    @staticmethod
    def calculate_offer(product_price: float, stock_level: int) -> Dict[str, Any]:
        """Calculate negotiation offer based on stock levels"""
        price = float(product_price)
        stock = int(stock_level)

        if stock > 15:
            # High stock - 10% discount
            offer_price = round(price * 0.9, 2)
            discount_percent = 10
            message = f"Great stock available! I can offer ₹{offer_price} (10% off the MRP of ₹{price})"
        elif 5 < stock <= 15:
            # Medium stock - 5% discount
            offer_price = round(price * 0.95, 2)
            discount_percent = 5
            message = f"Limited stock available. I can offer ₹{offer_price} (5% off the MRP of ₹{price})"
        else:
            # Low stock - no discount
            offer_price = price
            discount_percent = 0
            message = f"Very limited stock. Best price: ₹{price} (MRP)"

        return {
            'original_price': price,
            'offer_price': offer_price,
            'discount_percent': discount_percent,
            'message': message,
            'can_negotiate': discount_percent > 0
        }

    @staticmethod
    def is_negotiation_request(message: str) -> bool:
        """Check if message contains negotiation keywords"""
        negotiation_keywords = [
            'discount', 'offer', 'cheap', 'less', 'reduce', 'price',
            'negotiate', 'nego', 'bargain', 'deal', 'taggesthava'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in negotiation_keywords)

    @staticmethod
    def is_greeting(message: str) -> bool:
        """Check if message is a greeting"""
        greetings = [
            'hi', 'hello', 'hey', 'good morning', 'good evening',
            'hai', 'namaste', 'vanakkam', 'good afternoon'
        ]
        message_lower = message.lower()
        return any(greeting in message_lower for greeting in greetings)

    @staticmethod
    def generate_greeting_response(user_email: str) -> str:
        """Generate personalized greeting response"""
        # Extract username from email
        username = user_email.split('@')[0]
        return f"Hey {username}! 👋 How can I help you with our products today?"

    @staticmethod
    def process_negotiation_request(product_id: int, user_email: str) -> str:
        """Process a negotiation request for a specific product"""
        try:
            from backend.product_service import ProductService

            product = ProductService.get_product_by_id(product_id)
            if not product:
                return "Sorry, I couldn't find that product."

            offer = NegotiationService.calculate_offer(product['price'], product['stock'])

            return f"Kiki Bot 🤖: {offer['message']}"

        except Exception as e:
            return f"Kiki Bot 🤖: Sorry, I encountered an error while processing your request: {str(e)}"