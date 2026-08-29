from fastapi import APIRouter, HTTPException
from sqlalchemy import desc
from app.database import database
from app.models import Conversation, Session
from app.schemas import ChatRequest, ChatResponse
from app.services.gemini_service import get_gemini_response
from app.rag_service import retrieve_context

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    if not request.message or request.message.strip() == "":
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # التحقق من وجود الجلسة للمتصفح
    check_session = Session.__table__.select().where(
        Session.session_id == request.session_id,
        Session.browser_id == request.browser_id
    )
    existing_session = await database.fetch_one(check_session)
    if not existing_session:
        title = request.message[:30] + ("..." if len(request.message) > 30 else "")
        insert_session = Session.__table__.insert().values(
            session_id=request.session_id,
            title=title,
            browser_id=request.browser_id
        )
        await database.execute(insert_session)

    # تخزين رسالة المستخدم
    query = Conversation.__table__.insert().values(
        session_id=request.session_id,
        role="user",
        content=request.message
    )
    await database.execute(query)

    # جلب السياق
    select_query = Conversation.__table__.select() \
        .where(Conversation.session_id == request.session_id) \
        .order_by(desc(Conversation.created_at)) \
        .limit(5)
    recent_messages = await database.fetch_all(select_query)

    retrieved_docs = await retrieve_context(request.message)

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

    ai_response = await get_gemini_response(full_prompt)

    # تخزين رد البوت
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