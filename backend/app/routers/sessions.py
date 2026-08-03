from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import desc
from app.database import database
from app.models import Session, Conversation, User
from app.schemas import SessionCreate, SessionUpdate, SessionResponse
from app.auth import get_current_user

router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

# ================================================
# 1. جلب قائمة الجلسات الخاصة بالمستخدم الحالي
# ================================================
@router.get("/", response_model=list[SessionResponse])
async def get_sessions(current_user: User = Depends(get_current_user)):
    query = Session.__table__.select() \
        .where(Session.user_id == current_user.id) \
        .order_by(desc(Session.created_at))
    result = await database.fetch_all(query)
    return result

# ================================================
# 2. إنشاء جلسة جديدة مرتبطة بالمستخدم الحالي
# ================================================
@router.post("/", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, current_user: User = Depends(get_current_user)):
    # التحقق من أن session_id غير موجودة مسبقاً لهذا المستخدم
    check_query = Session.__table__.select() \
        .where(Session.session_id == session_data.session_id) \
        .where(Session.user_id == current_user.id)
    existing = await database.fetch_one(check_query)
    if existing:
        return existing  # إذا كانت موجودة لهذا المستخدم، نعيدها

    # إنشاء جلسة جديدة مع ربطها بالمستخدم
    query = Session.__table__.insert().values(
        session_id=session_data.session_id,
        title=session_data.title or "محادثة جديدة",
        user_id=current_user.id
    )
    await database.execute(query)
    
    # نعيد البيانات المنشأة
    new_session = await database.fetch_one(
        Session.__table__.select() \
            .where(Session.session_id == session_data.session_id) \
            .where(Session.user_id == current_user.id)
    )
    return new_session

# ================================================
# 3. تحديث عنوان جلسة (مع التحقق من الملكية)
# ================================================
@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, update_data: SessionUpdate, current_user: User = Depends(get_current_user)):
    # التأكد من أن الجلسة موجودة وتنتمي للمستخدم
    check_query = Session.__table__.select() \
        .where(Session.session_id == session_id) \
        .where(Session.user_id == current_user.id)
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail="الجلسة غير موجودة أو لا تنتمي لك")
    
    query = Session.__table__.update() \
        .where(Session.session_id == session_id) \
        .where(Session.user_id == current_user.id) \
        .values(title=update_data.title)
    await database.execute(query)
    
    updated = await database.fetch_one(
        Session.__table__.select() \
            .where(Session.session_id == session_id) \
            .where(Session.user_id == current_user.id)
    )
    return updated

# ================================================
# 4. حذف جلسة (مع التحقق من الملكية)
# ================================================
@router.delete("/{session_id}")
async def delete_session(session_id: str, current_user: User = Depends(get_current_user)):
    # التأكد من أن الجلسة موجودة وتنتمي للمستخدم
    check_query = Session.__table__.select() \
        .where(Session.session_id == session_id) \
        .where(Session.user_id == current_user.id)
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail="الجلسة غير موجودة أو لا تنتمي لك")
    
    # حذف رسائل المحادثة المرتبطة
    delete_conversations = Conversation.__table__.delete() \
        .where(Conversation.session_id == session_id)
    await database.execute(delete_conversations)
    
    # حذف الجلسة نفسها
    delete_session = Session.__table__.delete() \
        .where(Session.session_id == session_id) \
        .where(Session.user_id == current_user.id)
    result = await database.execute(delete_session)
    
    if result == 0:
        raise HTTPException(status_code=404, detail="الجلسة غير موجودة")
    
    return {"status": "success", "message": "تم حذف الجلسة وكل رسائلها"}

# ================================================
# 5. جلب رسائل جلسة معينة (مع التحقق من الملكية)
# ================================================
@router.get("/{session_id}/messages")
async def get_session_messages(session_id: str, current_user: User = Depends(get_current_user)):
    # التأكد من أن الجلسة تنتمي للمستخدم
    check_query = Session.__table__.select() \
        .where(Session.session_id == session_id) \
        .where(Session.user_id == current_user.id)
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail="الجلسة غير موجودة أو لا تنتمي لك")
    
    query = Conversation.__table__.select() \
        .where(Conversation.session_id == session_id) \
        .order_by(Conversation.created_at)
    result = await database.fetch_all(query)
    return result