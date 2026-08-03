from fastapi import APIRouter, HTTPException
from sqlalchemy import desc
from app.database import database
from app.models import Session, Conversation
from app.schemas import SessionCreate, SessionUpdate, SessionResponse

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

# ================================================
# 1. جلب قائمة جميع الجلسات (مرتبة حسب الأحدث)
# ================================================
@router.get("/", response_model=list[SessionResponse])
async def get_sessions():
    query = Session.__table__.select().order_by(desc(Session.created_at))
    result = await database.fetch_all(query)
    return result

# ================================================
# 2. إنشاء جلسة جديدة (أو التحقق من وجودها)
# ================================================
@router.post("/", response_model=SessionResponse)
async def create_session(session_data: SessionCreate):
    # التحقق من أن session_id غير موجودة مسبقاً
    check_query = Session.__table__.select().where(Session.session_id == session_data.session_id)
    existing = await database.fetch_one(check_query)
    if existing:
        return existing  # إذا كانت موجودة، نعيدها

    # إذا لم تكن موجودة، ننشئها
    query = Session.__table__.insert().values(
        session_id=session_data.session_id,
        title=session_data.title or "محادثة جديدة"
    )
    await database.execute(query)
    
    # نعيد البيانات المنشأة
    new_session = await database.fetch_one(
        Session.__table__.select().where(Session.session_id == session_data.session_id)
    )
    return new_session

# ================================================
# 3. تحديث عنوان جلسة (إعادة تسمية)
# ================================================
@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, update_data: SessionUpdate):
    query = Session.__table__.update().where(Session.session_id == session_id).values(
        title=update_data.title
    )
    await database.execute(query)
    
    # نعيد الجلسة المحدثة
    updated = await database.fetch_one(
        Session.__table__.select().where(Session.session_id == session_id)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="الجلسة غير موجودة")
    return updated

# ================================================
# 4. حذف جلسة (وجميع رسائلها المرتبطة)
# ================================================
@router.delete("/{session_id}")
async def delete_session(session_id: str):
    # 1. حذف جميع رسائل المحادثة المرتبطة بهذه الجلسة
    delete_conversations = Conversation.__table__.delete().where(
        Conversation.session_id == session_id
    )
    await database.execute(delete_conversations)
    
    # 2. حذف الجلسة نفسها
    delete_session = Session.__table__.delete().where(Session.session_id == session_id)
    result = await database.execute(delete_session)
    
    if result == 0:
        raise HTTPException(status_code=404, detail="الجلسة غير موجودة")
    
    return {"status": "success", "message": "تم حذف الجلسة وكل رسائلها"}

# ================================================
# 5. (إضافي) جلب رسائل جلسة معينة (لتحميل التاريخ عند النقر)
# ================================================
@router.get("/{session_id}/messages")
async def get_session_messages(session_id: str):
    query = Conversation.__table__.select() \
        .where(Conversation.session_id == session_id) \
        .order_by(Conversation.created_at)
    result = await database.fetch_all(query)
    return result