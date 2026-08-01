"""
هذا الملف يدير الاتصال بقاعدة البيانات.
يحتوي على إعدادات SQLite ومحرك SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

# 1. عنوان قاعدة البيانات
DATABASE_URL = "sqlite:///./chatbot.db"

# 2. كائن Database الخاص بـ 'databases' للاتصال غير المتزامن
database = Database(DATABASE_URL)

# 3. محرك SQLAlchemy
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 4. جلسة SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. الفئة الأساسية (Base) التي ستشتق منها جميع النماذج
Base = declarative_base()

# تأكد من عدم وجود أي سطر يحاول استيراد models هنا