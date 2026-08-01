import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY غير موجود في ملف .env")

genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-flash-latest"     # أحدث نموذج Flash خفيف[reference:4]

# استبدل السطر الذي يبدأ بـ async def بهذا:
async def get_gemini_response(prompt: str) -> str:
    """
    ترسل النص الكامل (السياق + السؤال) إلى Gemini وتعيد الرد.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"خطأ في Gemini: {e}")
        return "عذراً، حدث خلل في الاتصال بالذكاء الاصطناعي."