import google.generativeai as genai
from api.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

print("Mencari model yang tersedia...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
