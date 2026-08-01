"""
خدمة RAG خفيفة باستخدام fastembed + SQLite
بدلاً من ChromaDB (الضخم) لتوفير الذاكرة.
"""

import os
import uuid
import json
import sqlite3
import asyncio
import numpy as np
from typing import List, Optional
import pypdf
from fastembed import TextEmbedding

# ================================================
# 1. تهيئة SQLite (للتخزين المحلي)
# ================================================
DB_PATH = "./rag_data.db"

def get_db_connection():
    """إنشاء اتصال بقاعدة بيانات SQLite"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """إنشاء جدول التضمينات إذا لم يكن موجوداً"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            chunk TEXT NOT NULL,
            embedding BLOB NOT NULL,
            metadata TEXT
        )
    """)
    # إضافة فهرس لتسريع البحث (اختياري)
    conn.commit()
    conn.close()

# استدعاء التهيئة عند تحميل الملف
init_db()

# ================================================
# 2. تهيئة نموذج التضمين (يعمل بـ ONNX، خفيف جداً)
# ================================================
# هذا النموذج يستهلك حوالي 80 ميجابايت فقط، ولا يحتاج إلى PyTorch.
embedding_model = TextEmbedding(model_name="all-MiniLM-L6-v2")

def get_embedding(text: str) -> List[float]:
    """
    توليد تضمين (متجه) للنص باستخدام fastembed
    """
    # fastembed يولد مصفوفة numpy
    embeddings = list(embedding_model.embed([text]))
    return embeddings[0].tolist()

# ================================================
# 3. دوال استخراج النص وتقطيعه (نفسها كما كانت)
# ================================================

def extract_text_from_pdf(file_path: str) -> str:
    """استخراج النص من ملف PDF"""
    reader = pypdf.PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return full_text

def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """تقطيع النص إلى أجزاء صغيرة"""
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks

# ================================================
# 4. الدوال الأساسية (الفهرسة والاسترجاع)
# ================================================

async def index_pdf(file_path: str) -> int:
    """
    فهرسة ملف PDF: استخراج النص، تقطيعه، توليد التضمينات، وتخزينها في SQLite.
    """
    # 1. استخراج النص (في خيط منفصل لأنها عملية ثقيلة)
    text = await asyncio.to_thread(extract_text_from_pdf, file_path)
    if not text.strip():
        raise ValueError("الملف فارغ أو لا يحتوي على نص.")

    # 2. تقطيع النص
    chunks = split_text_into_chunks(text)
    if not chunks:
        raise ValueError("لم يتم استخراج أي نص من الملف.")

    # 3. حذف البيانات القديمة (استبدال كامل) - ننظف الجدول
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents")
    conn.commit()

    # 4. توليد التضمينات لكل قطعة (في خيط منفصل لتجنب حظر الخادم)
    def process_chunks():
        embeddings = []
        for chunk in chunks:
            emb = get_embedding(chunk)
            embeddings.append(emb)
        return embeddings

    all_embeddings = await asyncio.to_thread(process_chunks)

    # 5. تخزين البيانات في SQLite
    for i, chunk in enumerate(chunks):
        chunk_id = str(uuid.uuid4())
        embedding_blob = np.array(all_embeddings[i], dtype=np.float32).tobytes()
        cursor.execute(
            "INSERT INTO documents (id, chunk, embedding, metadata) VALUES (?, ?, ?, ?)",
            (chunk_id, chunk, embedding_blob, json.dumps({"source": file_path}))
        )
    
    conn.commit()
    conn.close()
    
    return len(chunks)

async def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    بحث عن القطع الأكثر تشابهاً مع سؤال المستخدم.
    """
    # 1. توليد تضمين السؤال
    query_embedding = await asyncio.to_thread(get_embedding, query)
    query_np = np.array(query_embedding, dtype=np.float32)

    # 2. جلب جميع البيانات من قاعدة البيانات
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, chunk, embedding FROM documents")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return ""

    # 3. حساب التشابه (جيب التمام) لكل قطعة
    similarities = []
    for row in rows:
        # تحويل BLOB إلى numpy array
        stored_emb = np.frombuffer(row[2], dtype=np.float32)
        # حساب التشابه (cosine similarity)
        norm_a = np.linalg.norm(query_np)
        norm_b = np.linalg.norm(stored_emb)
        if norm_a == 0 or norm_b == 0:
            sim = 0.0
        else:
            sim = np.dot(query_np, stored_emb) / (norm_a * norm_b)
        similarities.append((sim, row[1]))

    # 4. ترتيب النتائج تنازلياً (الأعلى تشابهاً أولاً)
    similarities.sort(key=lambda x: x[0], reverse=True)

    # 5. استخراج النصوص الأكثر تشابهاً
    top_chunks = [text for _, text in similarities[:top_k]]
    
    return "\n---\n".join(top_chunks)

async def clear_collection():
    """حذف جميع المستندات من قاعدة البيانات"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents")
    conn.commit()
    conn.close()
    return {"status": "cleared"}