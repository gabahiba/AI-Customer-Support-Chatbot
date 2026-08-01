"""
خدمة RAG: مسؤولة عن استخراج النصوص من PDF، تقطيعها،
تخزينها في ChromaDB، واسترجاع القطع ذات الصلة.
"""

import os
import uuid
import asyncio
from typing import List, Optional

# مكتبات استخراج النص من PDF
import pypdf

# مكتبات التضمين (Embedding) والمتجهات
from sentence_transformers import SentenceTransformer
import chromadb

# ================================================
# 1. تهيئة نموذج التضمين (يعمل محلياً، مجاني، سريع)
# ================================================
# لماذا هذا النموذج؟ لأنه خفيف (80 ميجابايت) ويعطي نتائج جيدة جداً
# للغة العربية والإنجليزية. لا يحتاج إلى مفتاح API.
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# ================================================
# 2. تهيئة اتصال ChromaDB (تخزين المتجهات)
# ================================================
# PersistentClient يعني أن البيانات تُحفظ على القرص الصلب
# في مجلد "chroma_db" حتى بعد إيقاف الخادم.
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# اسم "المجموعة" (Collection) التي سنخزن فيها الملفات.
# يمكننا لاحقاً إنشاء عدة مجموعات لمشاريع مختلفة.
COLLECTION_NAME = "company_docs"
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)

# ================================================
# 3. الدوال المساعدة (استخراج النص وتقطيعه)
# ================================================

def extract_text_from_pdf(file_path: str) -> str:
    """
    تفتح ملف PDF وتستخرج كل النصوص منه، صفحة صفحة.
    """
    reader = pypdf.PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    return full_text

def split_text_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    تقسم النص الطويل إلى قطع صغيرة (Chunks).
    - chunk_size: حجم القطعة بالحروف.
    - overlap: عدد الحروف المتداخلة بين قطعتين (لضمان عدم فقدان السياق).
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end]
        chunks.append(chunk)
        # نبدأ القطعة التالية قبل نهاية القطعة الحالية بـ "overlap"
        start += (chunk_size - overlap)
    
    return chunks

# ================================================
# 4. الدوال الأساسية (الفهرسة والاسترجاع)
# ================================================

def get_embedding(text: str) -> List[float]:
    """
    تحويل النص إلى قائمة من الأرقام (متجه).
    هذه الأرقام تمثل "معنى" النص.
    """
    return embedding_model.encode(text).tolist()

async def index_pdf(file_path: str) -> int:
    """
    الدالة الرئيسية لرفع ملف PDF:
    - تستخرج النص.
    - تقطعه.
    - تحوله إلى متجهات.
    - تخزنه في ChromaDB.
    
    تعيد عدد القطع المخزنة.
    """
    # 1. استخراج النص (هذه عملية ثقيلة، ننفذها في خيط منفصل)
    text = await asyncio.to_thread(extract_text_from_pdf, file_path)
    
    if not text.strip():
        raise ValueError("الملف فارغ أو لا يحتوي على نص قابل للقراءة.")
    
    # 2. تقطيع النص
    chunks = split_text_into_chunks(text)
    
    if not chunks:
        raise ValueError("لم يتم استخراج أي نص من الملف.")
    
    # 3. تحويل كل قطعة إلى متجه (عملية ثقيلة، في خيط منفصل)
    # سنقوم بتوليد معرف فريد لكل قطعة
    ids = [str(uuid.uuid4()) for _ in chunks]
    
    # نحسب المتجهات دفعة واحدة (أسرع)
    embeddings = await asyncio.to_thread(
        lambda: [get_embedding(chunk) for chunk in chunks]
    )
    
    # 4. إضافة (أو تحديث) القطع في ChromaDB
    # Upsert: إذا كان المعرف موجوداً، يُحدّث، وإلا يُضاف.
    # للحفاظ على النظافة، سنحذف المجموعة القديمة إذا أردنا رفع ملف جديد بالكامل.
    # لكن في هذا التطبيق، سنضيف الملفات الجديدة إلى نفس المجموعة (تراكمي).
    for i, chunk in enumerate(chunks):
        collection.upsert(
            documents=[chunk],
            embeddings=[embeddings[i]],
            ids=[ids[i]]
        )
    
    return len(chunks)

async def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    تستقبل سؤال المستخدم، وتبحث في ChromaDB عن القطع الأكثر تشابهاً.
    تعيد النصوص المتشابهة كسلسلة نصية واحدة.
    """
    # 1. تحويل سؤال المستخدم إلى متجه
    query_embedding = await asyncio.to_thread(get_embedding, query)
    
    # 2. البحث في قاعدة البيانات
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    # 3. استخراج النصوص الناتجة
    if results and results['documents'] and len(results['documents']) > 0:
        # results['documents'] هي قائمة من القوائم، نأخذ أول قائمة
        documents = results['documents'][0]
        return "\n---\n".join(documents)
    
    return ""  # إذا لم يجد شيئاً، نعيد نصاً فارغاً

async def clear_collection():
    """
    (اختياري) لحذف جميع المستندات من قاعدة البيانات،
    مفيد إذا أردت رفع ملف جديد واستبدال القديم.
    """
    # في ChromaDB، الحذف يتم على مستوى القطع، أو يمكن حذف المجموعة كاملة.
    # الأسهل: حذف المجموعة وإنشاؤها من جديد.
    global collection
    chroma_client.delete_collection(COLLECTION_NAME)
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)