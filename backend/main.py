from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import database, engine, Base
from app import models
from app.routers import chat, upload, sessions

from app.routers import chat, upload, sessions, auth  # أضف ", auth"

app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(sessions.router)
app.include_router(auth.router)  # أضف هذا السطر
# ============================================
# 1. تعريف تطبيق FastAPI (يجب أن يكون أولاً)
# ============================================
app = FastAPI(
    title="AI Customer Support Chatbot API",
    description="Full-stack chatbot with RAG and session management",
    version="1.0.0"
)

# ============================================
# 2. إعداد CORS (يحتاج إلى app)
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# 3. تضمين الروترات (يحتاج إلى app)
# ============================================
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(sessions.router)

# ============================================
# 4. أحداث دورة الحياة (تستخدم app)
# ============================================
@app.on_event("startup")
async def startup():
    await database.connect()
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ============================================
# 5. نقاط النهاية العامة
# ============================================
@app.get("/")
def read_root():
    return {"message": "AI Chatbot API is running!", "status": "success"}

@app.get("/health")
def health_check():
    return {"status": "OK"}