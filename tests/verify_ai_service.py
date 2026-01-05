import os
import sys

# Add current directory to path
sys.path.insert(0, os.getcwd())

from app.services.ai_service import ai_service

print("--- Testing OraculoAI Service (google-genai) ---")

# Test 1: Check initialization
if ai_service.client:
    print("SUCCESS: AI Client initialized (API Key found).")
else:
    print("WARNING: AI Client NOT initialized (API Key missing or invalid).")

# Test 2: Mock response generation
print("\n--- Testing Response Generation ---")
response = ai_service.generate_response("Olá, quem é você?")

if response:
    print(f"SUCCESS: Generated response: {response[:50]}...")
else:
    print("INFO: No response generated (Fallback mode active or Error).")

print("\n--- Verification Complete ---")
