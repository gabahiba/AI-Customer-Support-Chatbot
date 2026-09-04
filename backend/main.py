from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import database, engine, Base
from app import models
from app.routers import chat, upload, sessions
import os
from pathlib import Path
import sys

app = FastAPI(
    title="AI Customer Support Chatbot API",
    description="Full-stack chatbot with RAG and session management",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(sessions.router)

# ============================================
# Startup events with error handling
# ============================================
@app.on_event("startup")
async def startup():
    try:
        print("🚀 Starting up application...")
        
        # حذف قاعدة البيانات القديمة
        db_file = Path("chatbot.db")
        if db_file.exists():
            os.remove(db_file)
            print("🗑️ Old database deleted.")
        
        print("🔌 Connecting to database...")
        await database.connect()
        
        print("📊 Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database initialized successfully.")
    except Exception as e:
        print(f"❌ FATAL ERROR during startup: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        # إعادة رفع الاستثناء لإيقاف الخادم وإظهار الخطأ في السجلات
        raise

@app.on_event("shutdown")
async def shutdown():
    try:
        print("🛑 Shutting down...")
        await database.disconnect()
        print("✅ Disconnected from database.")
    except Exception as e:
        print(f"⚠️ Error during shutdown: {e}")

# ============================================
# Simple health check endpoints
# ============================================
@app.get("/")
def read_root():
    return {"message": "AI Chatbot API is running!", "status": "success"}

@app.get("/health")
def health_check():
    return {"status": "OK"}

if __name__ == "__main__":
    # للتشغيل المحلي
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)