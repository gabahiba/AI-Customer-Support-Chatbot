from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import database, engine, Base
from app import models
from app.routers import chat, upload, sessions

app = FastAPI(
    title="AI Customer Support Chatbot API",
    description="Full-stack chatbot with RAG and session management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(sessions.router)

@app.on_event("startup")
async def startup():
    await database.connect()
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
def read_root():
    return {"message": "AI Chatbot API is running!", "status": "success"}

@app.get("/health")
def health_check():
    return {"status": "OK"}