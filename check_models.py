import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("❌ No GOOGLE_API_KEY found in .env")
else:
    genai.configure(api_key=api_key)
    print(f"🔑 Checking models for API Key: {api_key[:5]}...")
    
    try:
        print("\n📋 Available Models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"❌ Error listing models: {e}")
