from fastapi import APIRouter, HTTPException
from sqlalchemy import desc
from app.database import database
from app.models import Conversation, Session
from app.schemas import ChatRequest, ChatResponse
from app.services.gemini_service import get_gemini_response
from app.rag_service import retrieve_context

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    
   
    if not request.message or request.message.strip() == "":
        raise HTTPException(status_code=400, detail="الرسالة لا يمكن أن تكون فارغة")
    

    check_session = Session.__table__.select().where(Session.session_id == request.session_id)
    existing_session = await database.fetch_one(check_session)
    if not existing_session:
        # ننشئ جلسة جديدة بعنوان افتراضي (أول كلمات الرسالة)
        title = request.message[:30] + ("..." if len(request.message) > 30 else "")
        insert_session = Session.__table__.insert().values(
            session_id=request.session_id,
            title=title
        )
        await database.execute(insert_session)
    
    
    query = Conversation.__table__.insert().values(
        session_id=request.session_id,
        role="user",
        content=request.message
    )
    await database.execute(query)
    
  
    select_query = Conversation.__table__.select() \
        .where(Conversation.session_id == request.session_id) \
        .order_by(desc(Conversation.created_at)) \
        .limit(5)
    
    recent_messages = await database.fetch_all(select_query)
    
    
    retrieved_docs = await retrieve_context(request.message)
    
   
    system_instruction = """
أنت مساعد ذكي ومفيد جداً، تتحدث جميع اللغات بطلاقة.
**يجب أن ترد دائماً بنفس اللغة التي كتب بها المستخدم سؤاله.**
إذا كتب المستخدم بالعربية، أجب بالعربية. إذا كتب بالإنجليزية، أجب بالإنجليزية. إذا كتب بالفرنسية، أجب بالفرنسية. وهكذا.

لديك مصدران للمعرفة:
1. "المعلومات المسترجعة من المستندات المرفوعة" (إن وجدت).
2. معرفتك العامة الواسعة.

تعليماتك:
- إذا كان السؤال متعلقاً بالمستندات، استخدمها وأجب بدقة.
- إذا كان السؤال عاماً، استخدم معرفتك العامة.
- لا تقل أبداً أنك "مختص فقط" بموضوع معين.
- كن ودوداً ومفصلاً في ردودك.
"""
    
   
    context_text = "--- تاريخ المحادثة (الذاكرة) ---\n"
    for msg in reversed(recent_messages):
        role = "المستخدم" if msg.role == "user" else "المساعد"
        context_text += f"{role}: {msg.content}\n"
    

    if retrieved_docs:
        context_text += "\n--- معلومات مسترجعة من المستندات المرفوعة (يجب الاعتماد عليها إن كانت ذات صلة) ---\n"
        context_text += retrieved_docs
    else:
        context_text += "\n(لا توجد مستندات مرفوعة ذات صلة بهذا السؤال.)"
    
  
    full_prompt = f"{system_instruction}\n\n{context_text}\n\nسؤال المستخدم الحالي: {request.message}\n\nالمساعد:"
    
    
    ai_response = await get_gemini_response(full_prompt)
    
    
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