from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import desc
from app.database import database
from app.models import Conversation, Session, User
from app.schemas import ChatRequest, ChatResponse
from app.services.gemini_service import get_gemini_response
from app.rag_service import retrieve_context
from app.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
async def send_message(request: ChatRequest, current_user: User = Depends(get_current_user)):
    if not request.message or request.message.strip() == "":
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # تحقق من وجود الجلسة للمستخدم
    check_session = Session.__table__.select().where(Session.session_id == request.session_id, Session.user_id == current_user.id)
    existing_session = await database.fetch_one(check_session)
    if not existing_session:
        title = request.message[:30] + ("..." if len(request.message) > 30 else "")
        await database.execute(Session.__table__.insert().values(
            session_id=request.session_id,
            title=title,
            user_id=current_user.id
        ))
    
    # تخزين رسالة المستخدم
    await database.execute(Conversation.__table__.insert().values(
        session_id=request.session_id,
        role="user",
        content=request.message
    ))
    
    # جلب السياق
    select_query = Conversation.__table__.select().where(Conversation.session_id == request.session_id).order_by(desc(Conversation.created_at)).limit(5)
    recent_messages = await database.fetch_all(select_query)
    retrieved_docs = await retrieve_context(request.message)
    
    # بناء الموجه
    system_instruction = "أنت مساعد ذكي... (ضع النص الكامل هنا)"
    context_text = "--- تاريخ المحادثة ---\n"
    for msg in reversed(recent_messages):
        role = "المستخدم" if msg.role == "user" else "المساعد"
        context_text += f"{role}: {msg.content}\n"
    if retrieved_docs:
        context_text += f"\n--- معلومات من المستندات ---\n{retrieved_docs}"
    full_prompt = f"{system_instruction}\n\n{context_text}\n\nسؤال المستخدم: {request.message}\n\nالمساعد:"
    
    ai_response = await get_gemini_response(full_prompt)
    
    # تخزين رد البوت
    await database.execute(Conversation.__table__.insert().values(
        session_id=request.session_id,
        role="assistant",
        content=ai_response
    ))
    
    return ChatResponse(session_id=request.session_id, response=ai_response)