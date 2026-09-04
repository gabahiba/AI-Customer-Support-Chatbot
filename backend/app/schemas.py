from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ============ Chat Schemas ============
class ChatRequest(BaseModel):
    session_id: str
    message: str
    browser_id: Optional[str] = None  # اختياري، لكن يجب أن يكون موجوداً عند الإرسال

class ChatResponse(BaseModel):
    session_id: str
    response: str

class ConversationItem(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

# ============ Session Schemas ============
class SessionCreate(BaseModel):
    session_id: str
    title: Optional[str] = None

class SessionUpdate(BaseModel):
    title: str

class SessionResponse(BaseModel):
    session_id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True