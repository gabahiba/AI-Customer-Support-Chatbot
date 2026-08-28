from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import desc
from app.database import database
from app.models import Session, Conversation
from app.schemas import SessionCreate, SessionUpdate, SessionResponse
from app.firebase_auth import get_current_user

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.get("/", response_model=list[SessionResponse])
async def get_sessions(current_user: dict = Depends(get_current_user)):
    uid = current_user["uid"]
    query = Session.__table__.select().where(Session.firebase_uid == uid).order_by(desc(Session.created_at))
    result = await database.fetch_all(query)
    return result

@router.post("/", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, current_user: dict = Depends(get_current_user)):
    uid = current_user["uid"]
    check_query = Session.__table__.select().where(
        Session.session_id == session_data.session_id,
        Session.firebase_uid == uid
    )
    existing = await database.fetch_one(check_query)
    if existing:
        return existing
    query = Session.__table__.insert().values(
        session_id=session_data.session_id,
        title=session_data.title or "محادثة جديدة",
        firebase_uid=uid
    )
    await database.execute(query)
    new_session = await database.fetch_one(
        Session.__table__.select().where(Session.session_id == session_data.session_id)
    )
    return new_session

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(session_id: str, update_data: SessionUpdate, current_user: dict = Depends(get_current_user)):
    uid = current_user["uid"]
    check_query = Session.__table__.select().where(
        Session.session_id == session_id,
        Session.firebase_uid == uid
    )
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found")
    query = Session.__table__.update().where(
        Session.session_id == session_id,
        Session.firebase_uid == uid
    ).values(title=update_data.title)
    await database.execute(query)
    updated = await database.fetch_one(
        Session.__table__.select().where(Session.session_id == session_id)
    )
    return updated

@router.delete("/{session_id}")
async def delete_session(session_id: str, current_user: dict = Depends(get_current_user)):
    uid = current_user["uid"]
    check_query = Session.__table__.select().where(
        Session.session_id == session_id,
        Session.firebase_uid == uid
    )
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found")
    await database.execute(Conversation.__table__.delete().where(Conversation.session_id == session_id))
    result = await database.execute(
        Session.__table__.delete().where(
            Session.session_id == session_id,
            Session.firebase_uid == uid
        )
    )
    if result == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success"}

@router.get("/{session_id}/messages")
async def get_session_messages(session_id: str, current_user: dict = Depends(get_current_user)):
    uid = current_user["uid"]
    check_query = Session.__table__.select().where(
        Session.session_id == session_id,
        Session.firebase_uid == uid
    )
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail="Session not found")
    query = Conversation.__table__.select().where(Conversation.session_id == session_id).order_by(Conversation.created_at)
    result = await database.fetch_all(query)
    return result