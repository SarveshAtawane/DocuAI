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

SQLALCHEMY_DATABASE_URL = "sqlite:///./DB/sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

@sql_router.post("/signin/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    otp = email_verification.send_email_with_otp(user.email, user.username)
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password.decode('utf-8'), is_verified=False, token=None)
    db_otp = OTP(email=user.email, otp=otp)
    
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
    
    return {"message": "Login successful"}

@sql_router.post("/verify-otp/")
async def verify_otp(otp_data: OTPVerify, db: Session = Depends(get_db)):
    db_otp = db.query(OTP).filter(OTP.email == otp_data.email).order_by(OTP.created_at.desc()).first()
    if db_otp is None:
        raise HTTPException(status_code=404, detail="OTP not found")
    
    if db_otp.otp != otp_data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    db_otp_time = db_otp.created_at.replace(tzinfo=timezone.utc)
    if datetime.datetime.now(timezone.utc) - db_otp_time > timedelta(minutes=10):

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
    
    return {"message": "Email verified successfully", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email, "is_verified": db_user.is_verified, "token": db_user.token}}

@sql_router.post("/resend-verification-email/")
async def resend_verification_email(email: str, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if db_user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")
    
    otp = email_verification.send_email_with_otp(db_user.email, db_user.username)
    
    db_otp = OTP(email=db_user.email, otp=otp)
    db.add(db_otp)
    db.commit()
    
    return {"message": "Verification email sent successfully"}