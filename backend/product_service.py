from typing import List, Dict, Any, Optional
import streamlit as st
from backend.config import db_manager

class ProductService:
    """Service class for product management operations"""

    @staticmethod
    def get_all_products(include_embeddings: bool = False) -> List[Dict[str, Any]]:
        """Get all products with optional embeddings"""
        try:
            if include_embeddings:
                query = "SELECT * FROM products"
            else:
                query = "SELECT id, name, description, price, min_price, image, stock FROM products"

            return db_manager.execute_query(query, fetch=True) or []
        except Exception as e:
            st.error(f"Failed to load products: {str(e)}")
            return []

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        try:
            query = "SELECT * FROM products WHERE id = %s"
            result = db_manager.execute_query(query, (product_id,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            st.error(f"Failed to load product: {str(e)}")
            return None

    @staticmethod
    def get_products_with_embeddings() -> List[Dict[str, Any]]:
        """Get products that have embeddings"""
        try:
            query = "SELECT * FROM products WHERE embedding IS NOT NULL"
            return db_manager.execute_query(query, fetch=True) or []
        except Exception as e:
            st.error(f"Failed to load products with embeddings: {str(e)}")
            return []

    @staticmethod
    def add_to_cart(user_email: str, product_id: int, quantity: int = 1) -> bool:
        """Add product to user's cart"""
        try:
            # Get product details
            product = ProductService.get_product_by_id(product_id)
            if not product:
                st.error("Product not found")
                return False

            # Check quantity
            if quantity <= 0:
                st.error("Quantity must be greater than 0")
                return False

            # Check stock
            if product['stock'] < quantity:
                st.error(f"Insufficient stock. Available: {product['stock']}")
                return False

            # Check if item already in cart
            existing_query = "SELECT id, quantity FROM cart WHERE user_email = %s AND product_id = %s"
            existing = db_manager.execute_query(existing_query, (user_email, product_id), fetch=True)

            if existing:
                # Update quantity
                new_quantity = existing[0]['quantity'] + quantity
                update_query = "UPDATE cart SET quantity = %s WHERE id = %s"
                db_manager.execute_query(update_query, (new_quantity, existing[0]['id']))
            else:
                # Add new item
                insert_query = """
                    INSERT INTO cart (user_email, product_id, product_name, price, quantity)
                    VALUES (%s, %s, %s, %s, %s)
                """
                db_manager.execute_query(insert_query, (
                    user_email, product_id, product['name'], product['price'], quantity
                ))

            st.success("Added to cart!")
            return True

        except Exception as e:
            st.error(f"Failed to add to cart: {str(e)}")
            return False

    @staticmethod
    def get_cart_items(user_email: str) -> List[Dict[str, Any]]:
        """Get user's cart items with product details"""
        try:
            query = """
                SELECT c.id, c.user_email, c.product_id, c.quantity, c.price, 
                       p.name, p.description, p.image
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_email = %s 
                ORDER BY c.created_at DESC
            """
            return db_manager.execute_query(query, (user_email,), fetch=True) or []
        except Exception as e:
            st.error(f"Failed to load cart: {str(e)}")
            return []

    @staticmethod
    def remove_from_cart(cart_item_id: int, user_email: str) -> bool:
        """Remove item from cart"""
        try:
            query = "DELETE FROM cart WHERE id = %s AND user_email = %s"
            db_manager.execute_query(query, (cart_item_id, user_email))
            return True
        except Exception as e:
            st.error(f"Failed to remove item: {str(e)}")
            return False

    @staticmethod
    def clear_cart(user_email: str) -> bool:
        """Clear user's cart"""
        try:
            query = "DELETE FROM cart WHERE user_email = %s"
            db_manager.execute_query(query, (user_email,))
            return True
        except Exception as e:
            st.error(f"Failed to clear cart: {str(e)}")
            return False

    @staticmethod
    def calculate_cart_total(cart_items: List[Dict[str, Any]]) -> float:
        """Calculate total price of cart items"""
        return sum(float(item['price']) * int(item.get('quantity', 1)) for item in cart_items)

    @staticmethod
    def place_order(user_email: str, cart_items: List[Dict[str, Any]]) -> bool:
        """Place order from cart items"""
        try:
            total = ProductService.calculate_cart_total(cart_items)

            # Create order
            order_query = "INSERT INTO orders (user_email, total) VALUES (%s, %s)"
            db_manager.execute_query(order_query, (user_email, total))

            # Clear cart
            ProductService.clear_cart(user_email)

            st.success(f"Order placed successfully! Total: ₹{total}")
            return True

        except Exception as e:
            st.error(f"Failed to place order: {str(e)}")
            return False

    @staticmethod
    def get_user_orders(user_email: str) -> List[Dict[str, Any]]:
        """Get user's order history"""
        try:
            query = "SELECT * FROM orders WHERE user_email = %s ORDER BY created_at DESC"
            return db_manager.execute_query(query, (user_email,), fetch=True) or []
        except Exception as e:
            st.error(f"Failed to load orders: {str(e)}")
            return []