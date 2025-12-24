from typing import Optional, Dict, Any
import streamlit as st
from backend.config import db_manager, SecurityManager, Config

class UserService:
    """Service class for user management operations"""

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        try:
            # Sanitize inputs
            email = SecurityManager.sanitize_input(email, 255)
            if not SecurityManager.validate_email(email):
                return None

            query = """
                SELECT id, first_name, last_name, username, email, phone, address, pincode, password_hash, salt
                FROM users WHERE email = %s
            """
            result = db_manager.execute_query(query, (email,), fetch=True)

            if not result:
                return None

            user = result[0]
            if SecurityManager.verify_password(password, user['password_hash'], user['salt']):
                # Remove sensitive data before returning
                user_data = {k: v for k, v in user.items() if k not in ['password_hash', 'salt']}
                return user_data

            return None

        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")
            return None

    @staticmethod
    def register_user(user_data: Dict[str, str]) -> bool:
        """Register a new user with validation"""
        try:
            # Validate required fields
            required_fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'password']
            for field in required_fields:
                if not user_data.get(field):
                    st.error(f"{field.replace('_', ' ').title()} is required")
                    return False

            # Validate email
            if not SecurityManager.validate_email(user_data['email']):
                st.error("Invalid email format")
                return False

            # Validate phone
            if not SecurityManager.validate_phone(user_data['phone']):
                st.error("Invalid phone number format")
                return False

            # Check if user already exists
            existing_query = "SELECT 1 FROM users WHERE email = %s OR username = %s"
            existing = db_manager.execute_query(
                existing_query,
                (user_data['email'], user_data['username']),
                fetch=True
            )

            if existing:
                st.error("User with this email or username already exists")
                return False

            # Hash password
            hashed_password, salt = SecurityManager.hash_password(user_data['password'])

            # Sanitize inputs
            sanitized_data = {
                'first_name': SecurityManager.sanitize_input(user_data['first_name'], 255),
                'last_name': SecurityManager.sanitize_input(user_data['last_name'], 255),
                'username': SecurityManager.sanitize_input(user_data['username'], 255),
                'email': user_data['email'],  # Already validated
                'phone': user_data['phone'],  # Already validated
                'address': SecurityManager.sanitize_input(user_data.get('address', ''), 500),
                'pincode': SecurityManager.sanitize_input(user_data.get('pincode', ''), 10),
                'password_hash': hashed_password,
                'salt': salt
            }

            # Insert user
            insert_query = """
                INSERT INTO users (first_name, last_name, username, email, phone, address, pincode, password_hash, salt)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            db_manager.execute_query(insert_query, tuple(sanitized_data.values()))

            st.success("Registration successful! Please login.")
            return True

        except Exception as e:
            st.error(f"Registration failed: {str(e)}")
            return False

    @staticmethod
    def get_user_profile(email: str) -> Optional[Dict[str, Any]]:
        """Get user profile by email"""
        try:
            query = """
                SELECT id, first_name, last_name, username, email, phone, address, pincode
                FROM users WHERE email = %s
            """
            result = db_manager.execute_query(query, (email,), fetch=True)
            return result[0] if result else None
        except Exception as e:
            st.error(f"Failed to load profile: {str(e)}")
            return None

    @staticmethod
    def update_user_profile(email: str, updates: Dict[str, str]) -> bool:
        """Update user profile"""
        try:
            # Validate updates
            if 'email' in updates and not SecurityManager.validate_email(updates['email']):
                st.error("Invalid email format")
                return False

            if 'phone' in updates and not SecurityManager.validate_phone(updates['phone']):
                st.error("Invalid phone number format")
                return False

            # Sanitize inputs
            sanitized_updates = {}
            for key, value in updates.items():
                if key in ['first_name', 'last_name', 'username', 'address', 'pincode']:
                    sanitized_updates[key] = SecurityManager.sanitize_input(value, 255 if key != 'address' else 500)
                else:
                    sanitized_updates[key] = value

            # Build update query
            set_clause = ", ".join([f"{k} = %s" for k in sanitized_updates.keys()])
            values = list(sanitized_updates.values()) + [email]

            update_query = f"UPDATE users SET {set_clause} WHERE email = %s"
            db_manager.execute_query(update_query, tuple(values))

            st.success("Profile updated successfully!")
            return True

        except Exception as e:
            st.error(f"Profile update failed: {str(e)}")
            return False