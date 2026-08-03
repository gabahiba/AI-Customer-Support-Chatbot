from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import desc
from app.database import database
from app.models import Conversation, Session, User
from app.schemas import ChatRequest, ChatResponse
from app.services.gemini_service import get_gemini_response
from app.rag_service import retrieve_context
from app.auth import get_current_user

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/", response_model=ChatResponse)
async def send_message(request: ChatRequest, current_user: User = Depends(get_current_user)):
    
    if not request.message or request.message.strip() == "":
        raise HTTPException(status_code=400, detail="الرسالة لا يمكن أن تكون فارغة")
    
    # ============================================
    # 1. التأكد من أن الجلسة موجودة وتنتمي للمستخدم الحالي
    # ============================================
    check_session = Session.__table__.select().where(
        Session.session_id == request.session_id,
        Session.user_id == current_user.id
    )
    existing_session = await database.fetch_one(check_session)
    if not existing_session:
        # إذا لم تكن الجلسة موجودة أو لا تنتمي للمستخدم، ننشئها مع ربطها به
        title = request.message[:30] + ("..." if len(request.message) > 30 else "")
        insert_session = Session.__table__.insert().values(
            session_id=request.session_id,
            title=title,
            user_id=current_user.id
        )
        await database.execute(insert_session)
    
    # 2. تخزين رسالة المستخدم في قاعدة البيانات
    query = Conversation.__table__.insert().values(
        session_id=request.session_id,
        role="user",
        content=request.message
    )
    await database.execute(query)
    
    # 3. جلب آخر 5 رسائل من تاريخ المحادثة (للسياق)
    select_query = Conversation.__table__.select() \
        .where(Conversation.session_id == request.session_id) \
        .order_by(desc(Conversation.created_at)) \
        .limit(5)
    recent_messages = await database.fetch_all(select_query)
    
    # 4. جلب المستندات ذات الصلة من RAG
    retrieved_docs = await retrieve_context(request.message)
    
    # 5. بناء الموجه (Prompt) وإرساله إلى Gemini
    system_instruction = """
    أنت مساعد ذكي ومفيد جداً، تتحدث جميع اللغات بطلاقة.
    يجب أن ترد دائماً بنفس اللغة التي كتب بها المستخدم سؤاله.
    لديك مصدران للمعرفة: المستندات المرفوعة ومعرفتك العامة.
    إذا كان السؤال متعلقاً بالمستندات، استخدمها وأجب بدقة.
    إذا كان السؤال عاماً، استخدم معرفتك العامة.
    لا تقل أبداً أنك "مختص فقط" بموضوع معين.
    """
    
    context_text = "--- تاريخ المحادثة ---\n"
    for msg in reversed(recent_messages):
        role = "المستخدم" if msg.role == "user" else "المساعد"
        context_text += f"{role}: {msg.content}\n"
    
    if retrieved_docs:
        context_text += "\n--- معلومات من المستندات المرفوعة ---\n"
        context_text += retrieved_docs
    else:
        context_text += "\n(لا توجد مستندات مرفوعة ذات صلة.)"
    
    full_prompt = f"{system_instruction}\n\n{context_text}\n\nسؤال المستخدم: {request.message}\n\nالمساعد:"
    
    # 6. استدعاء Gemini
    ai_response = await get_gemini_response(full_prompt)
    
    # 7. تخزين رد البوت
    query_assistant = Conversation.__table__.insert().values(
        session_id=request.session_id,
        role="assistant",
        content=ai_response
    )
    await database.execute(query_assistant)
    
    return ChatResponse(
        session_id=request.session_id,
        response=ai_response
    )