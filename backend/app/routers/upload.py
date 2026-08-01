"""
هذا الملف يحتوي على نقاط النهاية الخاصة برفع الملفات.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import shutil
import tempfile

# استيراد خدمة RAG
from app.rag_service import index_pdf, clear_collection

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

@router.post("/pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """
    تستقبل ملف PDF، وتخزنه في قاعدة البيانات المتجهية (ChromaDB).
    
    - file: ملف PDF مرفوع من المستخدم.
    - return: رسالة نجاح مع عدد القطع المخزنة.
    """
    
    # 1. التحقق من نوع الملف
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="نوع الملف غير مدعوم. يرجى رفع ملف PDF فقط."
        )
    
    # 2. حفظ الملف المؤقت على القرص (لأن PyPDF يحتاج إلى مسار ملف)
    #    نستخدم tempfile لضمان حذف الملف بعد الانتهاء.
    try:
        # ننشئ ملفاً مؤقتاً في مجلد النظام
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            # نكتب محتوى الملف المرفوع في الملف المؤقت
            shutil.copyfileobj(file.file, tmp_file)
            temp_path = tmp_file.name
        
        # 3. استدعاء خدمة RAG لفهرسة الملف
        #    نمرر مسار الملف المؤقت
        num_chunks = await index_pdf(temp_path)
        
        # 4. حذف الملف المؤقت بعد الانتهاء (تنظيف)
        os.unlink(temp_path)
        
        return {
            "status": "success",
            "message": f"تم رفع الملف '{file.filename}' بنجاح.",
            "chunks_stored": num_chunks
        }
        
    except Exception as e:
        # إذا حدث أي خطأ، نحذف الملف المؤقت إن وجد، ونعيد الخطأ
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        raise HTTPException(status_code=500, detail=f"حدث خطأ أثناء معالجة الملف: {str(e)}")