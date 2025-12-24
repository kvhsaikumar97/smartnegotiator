import os
import logging
from typing import Optional, Dict, Any
from contextlib import contextmanager
import mysql.connector
from mysql.connector import pooling
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection manager with connection pooling"""

    def __init__(self):
        self.pool = None
        self._init_pool()

    def _init_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="smartnegotiator_pool",
                pool_size=5,
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "smartnegotiator")
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = self.pool.get_connection()
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            st.error("Database connection failed. Please try again.")
            raise
        finally:
            if conn:
                conn.close()

    def execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> Optional[list]:
        """Execute a query with proper error handling"""
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(query, params or ())
                if fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    conn.commit()
                    return None
            except Exception as e:
                conn.rollback()
                logger.error(f"Query execution failed: {query} - {e}")
                raise
            finally:
                cursor.close()

# Global database manager instance
db_manager = DatabaseManager()

class SecurityManager:
    """Enhanced security utilities"""

    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple:
        """Hash password with salt using PBKDF2"""
        import hashlib
        import secrets

        if not salt:
            salt = secrets.token_hex(16)

        # Use PBKDF2 with SHA256
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        ).hex()

        return hashed, salt

    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """Verify password against hash"""
        import hashlib

        expected_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()

        return expected_hash == hashed

    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Basic phone validation (Indian numbers)"""
        import re
        # Allow +91 prefix or direct 10-digit numbers
        pattern = r'^(\+91)?[6-9]\d{9}$'
        return re.match(pattern, phone) is not None

    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not text:
            return ""
        # Remove potentially dangerous characters
        import re
        text = re.sub(r'[<>]', '', text)
        return text[:max_length].strip()

class Config:
    """Application configuration"""

    # Database
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "smartnegotiator")

    # AI APIs
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # App settings
    MAX_LOGIN_ATTEMPTS = 5
    SESSION_TIMEOUT = 3600  # 1 hour
    ITEMS_PER_PAGE = 10

    @classmethod
    def get_available_llm_providers(cls) -> list:
        """Get list of available LLM providers"""
        providers = []
        if cls.OPENAI_API_KEY:
            providers.append("openai")
        if cls.GEMINI_API_KEY:
            providers.append("gemini")
        if cls.ANTHROPIC_API_KEY:
            providers.append("anthropic")
        return providers