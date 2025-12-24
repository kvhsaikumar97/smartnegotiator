import os
import sys

# Add current directory to path so we can import backend
sys.path.append(os.getcwd())

from backend.rag_engine import analyze_intent_with_llm

print("Checking API Keys...")
print(f"OPENAI_API_KEY present: {bool(os.getenv('OPENAI_API_KEY'))}")
print(f"GEMINI_API_KEY present: {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"ANTHROPIC_API_KEY present: {bool(os.getenv('ANTHROPIC_API_KEY'))}")

print("\nTesting Intent Analysis...")
try:
    result = analyze_intent_with_llm("Which items are running low on stock?")
    print(f"Result: {result}")
except Exception as e:
    print(f"Error: {e}")
