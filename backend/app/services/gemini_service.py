import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

genai.configure(api_key=API_KEY)

# استخدم نموذجاً مستقراً
MODEL_NAME = "gemini-2.0-flash"  # بدلاً من "gemini-flash-latest"

async def get_gemini_response(prompt: str) -> str:
    model = genai.GenerativeModel(MODEL_NAME)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"❌ Gemini Error: {e}")
        return "عذراً، حدث خلل في الاتصال بالذكاء الاصطناعي."