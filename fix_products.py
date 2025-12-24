import os
import sys

# Add the current directory to the path so we can import backend modules
sys.path.append(os.getcwd())

from backend.config import db_manager
from backend.rag_engine import load_products_from_csv

def fix_products():
    print("Cleaning up database...")
    
    # Use a single connection for the entire operation to ensure session variables persist
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        try:
            # Disable FK checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            
            # Truncate tables
            print("Truncating cart...")
            cursor.execute("TRUNCATE TABLE cart")
            print("Truncating conversations...")
            cursor.execute("TRUNCATE TABLE conversations")
            print("Truncating products...")
            cursor.execute("TRUNCATE TABLE products")
            
            # Re-enable FK checks
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            conn.commit()
            print("Tables truncated successfully.")
            
        except Exception as e:
            conn.rollback()
            print(f"Error during cleanup: {e}")
            return

    print("Loading products from CSV...")
    count = load_products_from_csv()
    print(f"Successfully loaded {count} products.")

if __name__ == "__main__":
    fix_products()
