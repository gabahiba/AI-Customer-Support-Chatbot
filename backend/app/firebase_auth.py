import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 1. تهيئة Firebase Admin SDK باستخدام ملف المفتاح
# تأكد من وضع الملف firebase-key.json في مجلد backend
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

security = HTTPBearer()

# 2. دالة للتحقق من صحة Token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token  # يحتوي على uid, email, name, إلخ
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )