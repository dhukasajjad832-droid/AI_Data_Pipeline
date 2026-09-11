import os
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if gemini_api_key:
    print("Gemini API key found!")
else:
    print("Gemini API key not found. Running without LLM API.")