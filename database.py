# database.py
from sqlalchemy import (
    create_engine, Column, Integer, String, Boolean, DateTime, Text, JSON, func
)
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
from config import DATABASE_URL
from logs import logger

Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized.")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)  # telegram id
    username = Column(String(64), nullable=True)
    points = Column(Integer, default=0)
    invited_count = Column(Integer, default=0)
    is_vip = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    favorites = Column(JSON, default=list)  # list of dicts
    searched_categories = Column(JSON, default=list)  # recent categories list
    invited_by = Column(Integer, nullable=True)  # referrer id

class CourseUpload(Base):
    __tablename__ = "course_uploads"
    id = Column(Integer, primary_key=True)
    uploader_id = Column(Integer)
    title = Column(String(255))
    description = Column(Text)
    url = Column(String(1024))
    image = Column(String(1024), nullable=True)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

class PointTransaction(Base):
    __tablename__ = "point_transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    amount = Column(Integer)
    reason = Column(String(128))
    created_at = Column(DateTime, default=func.now())

class PaymentRequest(Base):
    __tablename__ = "payment_requests"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    points = Column(Integer)
    ton_amount = Column(String(32))
    status = Column(String(32), default="pending")  # pending/confirmed/rejected
    created_at = Column(DateTime, default=func.now())