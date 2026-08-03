from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import desc
from app.database import database
from app.models import Session, Conversation
from app.schemas import SessionCreate, SessionUpdate, SessionResponse
from typing import Optional

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

# ================================================
# 1. جلب قائمة الجلسات (مع تصفية حسب المتصفح)
# ================================================
@router.get("/", response_model=list[SessionResponse])
async def get_sessions(
    browser_id: Optional[str] = Query(None, description="معرف المتصفح لتصفية الجلسات")
):
    """
    جلب الجلسات. إذا تم إرسال browser_id، نعيد فقط الجلسات الخاصة بهذا المتصفح.
    """
    query = Session.__table__.select().order_by(desc(Session.created_at))
    
    # التصفية حسب معرف المتصفح
    if browser_id:
        query = query.where(Session.session_id == browser_id)
    
    result = await database.fetch_all(query)
    return result

# ================================================
# 2. إنشاء جلسة جديدة (نفسها)
# ================================================
@router.post("/", response_model=SessionResponse)
async def create_session(session_data: SessionCreate):
    check_query = Session.__table__.select().where(Session.session_id == session_data.session_id)
    existing = await database.fetch_one(check_query)
    if existing:
        return existing

    query = Session.__table__.insert().values(
        session_id=session_data.session_id,
        title=session_data.title or "محادثة جديدة"
    )
    await database.execute(query)
    
    new_session = await database.fetch_one(
        Session.__table__.select().where(Session.session_id == session_data.session_id)
    )
    return new_session

# ================================================
# 3. تحديث عنوان جلسة (نفسها)
# ================================================
@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, update_data: SessionUpdate):
    query = Session.__table__.update().where(Session.session_id == session_id).values(
        title=update_data.title
    )
    await database.execute(query)
    
    updated = await database.fetch_one(
        Session.__table__.select().where(Session.session_id == session_id)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Session not found")
    return updated

# ================================================
# 4. حذف جلسة (نفسها)
# ================================================
@router.delete("/{session_id}")
async def delete_session(session_id: str):
    delete_conversations = Conversation.__table__.delete().where(
        Conversation.session_id == session_id
    )
    await database.execute(delete_conversations)
    
    delete_session = Session.__table__.delete().where(Session.session_id == session_id)
    result = await database.execute(delete_session)
    
    if result == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "message": "Session and all messages deleted"}

# ================================================
# 5. جلب رسائل جلسة معينة (نفسها)
# ================================================
@router.get("/{session_id}/messages")
async def get_session_messages(session_id: str):
    query = Conversation.__table__.select() \
        .where(Conversation.session_id == session_id) \
        .order_by(Conversation.created_at)
    result = await database.fetch_all(query)
    return result