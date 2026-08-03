from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.auth import get_db, get_user_by_username, get_user_by_email, create_access_token, authenticate_user, get_password_hash
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str

@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_username(db, request.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if get_user_by_email(db, request.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    hashed_password = get_password_hash(request.password)
    new_user = User(username=request.username, email=request.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": str(new_user.id)})
    return TokenResponse(access_token=access_token, token_type="bearer", user_id=new_user.id, username=new_user.username)

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token, token_type="bearer", user_id=user.id, username=user.username)

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}