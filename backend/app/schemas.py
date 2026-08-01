"""
هذا الملف يحتوي على مخططات Pydantic.
تحدد شكل البيانات التي تدخل وتخرج من نقاط النهاية (Endpoints).
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ================================================
# 1. مخططات لاستقبال البيانات من العميل (Request)
# ================================================

class ChatRequest(BaseModel):
    """
    ما يرسله المستخدم عندما يكتب سؤاله.
    """
    session_id: str  # معرف الجلسة (يولده الواجهة الأمامية)
    message: str     # نص السؤال

# ================================================
# 2. مخططات لإرسال البيانات إلى العميل (Response)
# ================================================

class ChatResponse(BaseModel):
    """
    ما يستقبله المستخدم كرد من البوت.
    """
    session_id: str
    response: str   # رد البوت
    # (سنضيف لاحقاً: sources = قائمة المصادر إن وجدت)

class ConversationItem(BaseModel):
    """
    تمثل رسالة واحدة في تاريخ المحادثة (تُستخدم لعرض السجل).
    """
    id: int
    role: str       # "user" أو "assistant"
    content: str
    created_at: datetime

    # هذا التكوين يسمح لـ Pydantic بتحويل كائن SQLAlchemy تلقائياً
    class Config:
        from_attributes = True  # (كان يُسمى orm_mode في الإصدارات القديمة)

# ================================================
# 3. مخططات الجلسات (Sessions)
# ================================================

class SessionCreate(BaseModel):
    """بيانات إنشاء جلسة جديدة (يُرسلها العميل)"""
    session_id: str
    title: Optional[str] = None  # إذا لم يرسل عنواناً، سنولده تلقائياً

class SessionUpdate(BaseModel):
    """بيانات تحديث جلسة (تغيير العنوان)"""
    title: str

class SessionResponse(BaseModel):
    """بيانات جلسة (تُرسل إلى العميل)"""
    session_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True