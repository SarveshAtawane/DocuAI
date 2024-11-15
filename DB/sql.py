from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from auth import email_verification
import bcrypt
from datetime import datetime, timedelta
from datetime import datetime, timezone
import datetime
import jwt
import secrets
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import jwt
import logging
import datetime



SQLALCHEMY_DATABASE_URL = "sqlite:///./DB/sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
security = HTTPBearer()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)   
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)
    token = Column(String, default="None")

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, index=True)
    otp = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now(timezone.utc))
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# Update the Pydantic models with correct configuration
class UserStatsUpdate(BaseModel):
    total_documents: int | None = None
    api_calls: int | None = None
    used_model: str | None = None  # Changed from model_used to avoid namespace conflict

class UserStatsResponse(BaseModel):
    username: str
    token: str
    total_documents: int
    api_calls: int
    api_key: str
    used_model: str  # Changed from model_used to avoid namespace conflict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,  # This replaces orm_mode
        arbitrary_types_allowed=True
    )

class UserStats(Base):
    __tablename__ = "user_stats"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True)
    token = Column(String, unique=True)
    total_documents = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    api_key = Column(String, unique=True)
    used_model = Column(String, default="none")  # Changed from model_used
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)  # Recreate all tables with the updated schema

sql_router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_verified: bool
    token: str
    class Config:
        orm_mode = True

class OTPVerify(BaseModel):
    email: str
    otp: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def generate_api_key(length: int = 16) -> str:
    # Characters to use for API key generation
    characters = "abcdefghijklmnopqrstuvwxyz"
    # Generate random API key
    api_key = ''.join(secrets.choice(characters) for _ in range(length))
    
    # Insert a hyphen after every 4 characters
    api_key = '-'.join(api_key[i:i+4] for i in range(0, len(api_key), 4))
    return api_key
def get_ist_time():
    return datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
@sql_router.post("/signin/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    print("Creating user")
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    otp = email_verification.send_email_with_otp(user.email, user.username)
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password.decode('utf-8'), is_verified=False, token=None)
    db_otp = OTP(email=user.email, otp=otp, created_at=datetime.now(timezone.utc))
    
    db.add(db_user)
    db.add(db_otp)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@sql_router.post("/login/")
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid password")
    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    
    return {"message": "Login successful", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email, "is_verified": db_user.is_verified, "token": db_user.token}}

@sql_router.post("/verify-otp/")
async def verify_otp(otp_data: OTPVerify, db: Session = Depends(get_db)):
    db_otp = db.query(OTP).filter(OTP.email == otp_data.email).order_by(OTP.created_at.desc()).first()
    if db_otp is None:
        raise HTTPException(status_code=404, detail="OTP not found")
    
    if db_otp.otp != otp_data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    db_otp_time = db_otp.created_at.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) - db_otp_time > timedelta(minutes=1):
        print("current time ", datetime.now(timezone.utc))
        print("otp time ", db_otp_time)
        raise HTTPException(status_code=400, detail="OTP expired.")
    
    # Mark user as verified and assign a verification token
    db_user = db.query(User).filter(User.email == otp_data.email).first()
    db_user.is_verified = True
    token = jwt.encode({"user_id": db_user.id}, "secret_key", algorithm="HS256")
    db_user.token = token
    db.commit()
    
    # Delete the used OTP
    db.delete(db_otp)
    db.commit()
        # Create user stats
    api_key = generate_api_key()
    db_stats = UserStats(
        username=db_user.username,
        token=token,
        total_documents=0,
        api_calls=0,
        api_key=api_key,
        used_model="none"  # Changed from model_used
    )
    
    
    db.add(db_stats)
    db.commit()
    db.refresh(db_stats)
    return {"message": "Email verified successfully", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email, "is_verified": db_user.is_verified, "token": db_user.token}}
class ResendOTPRequest(BaseModel):
    email: str
# Function to verify JWT token
def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    db_user = db.query(User).filter(User.token == token).first()
    if not db_user or db_user.token == "None":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return token
@sql_router.get("/user-stats/", response_model=UserStatsResponse)
async def get_user_stats(token: str = Depends(verify_jwt), db: Session = Depends(get_db)):
    db_stats = db.query(UserStats).filter(UserStats.token == token).first()
    if not db_stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    return db_stats


@sql_router.put("/user-stats/update")
async def update_user_stats(
    token: str = Depends(verify_jwt),
    updates: UserStatsUpdate = None,
    db: Session = Depends(get_db)
):
    db_stats = db.query(UserStats).filter(UserStats.token == token).first()
    if not db_stats:
        raise HTTPException(status_code=404, detail="Stats not found")

    if updates.total_documents is not None:
        db_stats.total_documents = updates.total_documents
    if updates.api_calls is not None:
        db_stats.api_calls = updates.api_calls
    if updates.used_model is not None:
        db_stats.used_model = updates.used_model

    db_stats.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_stats)

    return {
        "message": "Stats updated successfully",
        "stats": {
            "username": db_stats.username,
            "total_documents": db_stats.total_documents,
            "api_calls": db_stats.api_calls,
            "used_model": db_stats.used_model
        }
    }

@sql_router.put("/user-stats/increment")
async def increment_user_stats(
    token: str = Depends(verify_jwt), 
    increment_documents: bool = False, 
    increment_api_calls: bool = False,
    used_model: str = None,
    db: Session = Depends(get_db)
):
    db_stats = db.query(UserStats).filter(UserStats.token == token).first()
    if not db_stats:
        raise HTTPException(status_code=404, detail="Stats not found")

    if increment_documents:
        db_stats.total_documents += 1
    if increment_api_calls:
        db_stats.api_calls += 1
    if used_model:
        db_stats.used_model = used_model

    db_stats.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_stats)

    return {
        "message": "Stats updated successfully",
        "total_documents": db_stats.total_documents,
        "api_calls": db_stats.api_calls,
        "used_model": db_stats.used_model
    }

@sql_router.post("/regenerate-api-key/")
async def regenerate_api_key(token: str = Depends(verify_jwt), db: Session = Depends(get_db)):
    db_stats = db.query(UserStats).filter(UserStats.token == token).first()
    if not db_stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    
    # Generate new API key
    new_api_key = generate_api_key()
    
    # Update the API key
    db_stats.api_key = new_api_key
    db_stats.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {
        "message": "API key regenerated successfully",
        "new_api_key": new_api_key
    }
@sql_router.post("/resend-verification-email/")
async def resend_verification_email(request: ResendOTPRequest, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == request.email).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")
    
    otp = email_verification.send_email_with_otp(db_user.email, db_user.username)
    
    # Delete any existing OTPs for this email
    db.query(OTP).filter(OTP.email == request.email).delete()
    
    # Create a new OTP
    db_otp = OTP(email=db_user.email, otp=otp, created_at=datetime.now(timezone.utc))
    db.add(db_otp)
    db.commit()
    
    return {"message": "Verification email sent successfully"}