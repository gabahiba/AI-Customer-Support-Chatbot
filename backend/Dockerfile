# نستخدم صورة Python رسمية مع دعم الحزم النظامية
FROM python:3.10-slim

# تثبيت الحزم النظامية المطلوبة لـ onnxruntime و fastembed
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملف المتطلبات أولاً (لتسريع البناء في المرات القادمة)
COPY requirements.txt .

# تثبيت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي الملفات
COPY . .

# تشغيل الخادم
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]