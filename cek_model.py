import google.generativeai as genai

# TEMPEL API KEY ANDA DISINI
API_KEY = "AIzaSyCcZUHZzAQR5RTz_vHAUFSSG2Gh8--x-l0"

genai.configure(api_key=API_KEY)

print("Mencari model yang tersedia...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")