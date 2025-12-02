from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextlib import contextmanager
import os

# Database setup
# Use absolute path for database to avoid permission issues
db_dir = os.getenv("DB_DIR", os.getcwd())
db_path = os.path.join(db_dir, "messages.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")
engine = create_engine(
    DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30
    },
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class MessageDB(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    message = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    read = Column(Boolean, default=False)

# Create tables and ensure file is writable
def init_db():
    """Initialize database and ensure it's writable"""
    Base.metadata.create_all(bind=engine)
    if os.path.exists(db_path):
        # Set secure permissions: read/write for owner and group only
        os.chmod(db_path, 0o660)

init_db()

# Pydantic Models
class MessageCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

class MessageResponse(BaseModel):
    id: int
    name: str
    email: str
    subject: str
    message: str
    timestamp: datetime
    read: bool
    
    class Config:
        from_attributes = True

class MessageUpdate(BaseModel):
    read: Optional[bool] = None

# FastAPI app
app = FastAPI(
    title="Portfolio Admin API",
    description="Admin dashboard API for managing contact form messages",
    version="1.0.0"
)

# CORS middleware
# Note: In production, replace ["*"] with specific frontend origins
# e.g., ["https://yourportfolio.com", "https://www.yourportfolio.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure with specific origins in production
    allow_credentials=False,  # Set to True only with specific origins
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

# Database session context manager
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoints
@app.get("/")
def root():
    return {"message": "Portfolio Admin API", "version": "1.0.0"}

@app.post("/api/messages", response_model=MessageResponse, status_code=201)
def create_message(message: MessageCreate):
    """Create a new contact message"""
    with get_db() as db:
        db_message = MessageDB(
            name=message.name,
            email=message.email,
            subject=message.subject,
            message=message.message
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

@app.get("/api/admin/messages", response_model=List[MessageResponse])
def get_all_messages(skip: int = 0, limit: int = 100):
    """Get all messages (admin endpoint)"""
    with get_db() as db:
        messages = db.query(MessageDB).offset(skip).limit(limit).all()
        return messages

@app.get("/api/admin/messages/{message_id}", response_model=MessageResponse)
def get_message(message_id: int):
    """Get a specific message by ID (admin endpoint)"""
    with get_db() as db:
        message = db.query(MessageDB).filter(MessageDB.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        return message

@app.patch("/api/admin/messages/{message_id}", response_model=MessageResponse)
def update_message(message_id: int, update: MessageUpdate):
    """Update message status (admin endpoint)"""
    with get_db() as db:
        message = db.query(MessageDB).filter(MessageDB.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        if update.read is not None:
            message.read = update.read
        
        db.commit()
        db.refresh(message)
        return message

@app.delete("/api/admin/messages/{message_id}")
def delete_message(message_id: int):
    """Delete a message (admin endpoint)"""
    with get_db() as db:
        message = db.query(MessageDB).filter(MessageDB.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        db.delete(message)
        db.commit()
        return {"message": "Message deleted successfully"}

@app.get("/api/admin/messages/stats/summary")
def get_message_stats():
    """Get message statistics (admin endpoint)"""
    with get_db() as db:
        total = db.query(MessageDB).count()
        read = db.query(MessageDB).filter(MessageDB.read == True).count()
        unread = total - read
        return {
            "total": total,
            "read": read,
            "unread": unread
        }
