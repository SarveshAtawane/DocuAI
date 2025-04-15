from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, ConfigDict
from auth import email_verification
import bcrypt
import jwt
import secrets
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import pytz
import datetime
from datetime import timedelta
import requests
SQLALCHEMY_DATABASE_URL = "sqlite:///./DB/sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
security = HTTPBearer()

# Define IST timezone
IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(IST)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)   
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_verified = Column(Boolean, default=False)
    token = Column(String, default="None")
class UserInfo(BaseModel):
    username: str
    email: str
    api_key: str
class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, index=True)
    otp = Column(String)
    # Ensure the DateTime column is timezone-aware
    created_at = Column(DateTime(timezone=True), default=get_ist_time)

class UserStatsUpdate(BaseModel):
    total_documents: int | None = None
    api_calls: int | None = None
    used_model: str | None = None

class UserStatsResponse(BaseModel):
    username: str
    token: str
    total_documents: int
    api_calls: int
    api_key: str
    used_model: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class UserStats(Base):
    __tablename__ = "user_stats"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True)
    token = Column(String, unique=True)
    total_documents = Column(Integer, default=0)
    api_calls = Column(Integer, default=0)
    api_key = Column(String, unique=True)
    used_model = Column(String, default="none")
    created_at = Column(DateTime(timezone=True), default=get_ist_time)
    updated_at = Column(DateTime(timezone=True), default=get_ist_time, onupdate=get_ist_time)

Base.metadata.create_all(bind=engine)

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

class ResendOTPRequest(BaseModel):
    email: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_api_key(length: int = 16) -> str:
    characters = "abcdefghijklmnopqrstuvwxyz"
    api_key = ''.join(secrets.choice(characters) for _ in range(length))
    api_key = '-'.join(api_key[i:i+4] for i in range(0, len(api_key), 4))
    return api_key

def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    db_user = db.query(User).filter(User.token == token).first()
    if not db_user or db_user.token == "None":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return token



# Add these imports at the top if not already present
from fastapi import Header
from typing import Optional

# Add these new models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    result: str
    model_used: str

# Add this helper function for API key validation
def verify_api_key(api_key: str = Header(...), db: Session = Depends(get_db)):
    db_stats = db.query(UserStats).filter(UserStats.api_key == api_key).first()
    if not db_stats:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return db_stats

@sql_router.post("/query/", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    # Verify API key and get user stats
    db_stats = verify_api_key(api_key, db)
    print(db_stats.token)
    try:
        chat_url = "http://localhost:8800/chat"
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": request.query,
            "entity_name": 'entity',
            "token": f"{db_stats.token}_embedding"  # Append _embedding as in your example
        }
        
        # Make the request to chat API
        response = requests.post(chat_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise exception for bad status codes
        
        # Get response data
        result = response.json()
        
        # Here you would process the query using your model
        # This is a placeholder for the actual query processing
        result = f"Processed query response: {result.get('response')}"
        model_used = "your-model-name"  # Replace with actual model name
        
        # Update user stats - increment API calls and update used model
        db_stats.api_calls += 1
        db_stats.used_model = model_used
        db_stats.updated_at = get_ist_time()
        db.commit()
        print("Query processed")
        return QueryResponse(
            result=result,
            model_used=model_used
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    




@sql_router.get("/user-info/", response_model=UserInfo)
async def get_user_info(token: str = Depends(verify_jwt), db: Session = Depends(get_db)):
    try:
        # Decode the JWT to get the user_id
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        user_id = payload.get("user_id")
        
        # Query the database to get user information
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Query the UserStats table instead of UserStatsResponse
        db_stats = db.query(UserStats).filter(UserStats.token == token).first()
        if not db_stats:
            raise HTTPException(status_code=404, detail="User stats not found")
        print(db_stats.api_key)
        return UserInfo(
            username=db_user.username, 
            email=db_user.email, 
            api_key=db_stats.api_key
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@sql_router.post("/signin/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    print("Creating user")
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
    
    return {"message": "Login successful", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email, "is_verified": db_user.is_verified, "token": db_user.token}}
@sql_router.post("/verify-otp/")
async def verify_otp(otp_data: OTPVerify, db: Session = Depends(get_db)):
    db_otp = db.query(OTP).filter(OTP.email == otp_data.email).order_by(OTP.created_at.desc()).first()
    if db_otp is None:
        raise HTTPException(status_code=404, detail="OTP not found")
    
    if db_otp.otp != otp_data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    current_time = get_ist_time()
    
    # Ensure OTP time is timezone-aware
    otp_time = db_otp.created_at
    if otp_time.tzinfo is None:
        otp_time = IST.localize(otp_time)
    else:
        otp_time = otp_time.astimezone(IST)
    
    # Now both times are timezone-aware and in IST
    if (current_time - otp_time) > timedelta(minutes=1):
        raise HTTPException(status_code=400, detail="OTP expired.")
    
    db_user = db.query(User).filter(User.email == otp_data.email).first()
    db_user.is_verified = True
    token = jwt.encode({"user_id": db_user.id}, "secret_key", algorithm="HS256")
    db_user.token = token
    db.commit()
    
    db.delete(db_otp)
    db.commit()

    api_key = generate_api_key()
    db_stats = UserStats(
        username=db_user.username,
        token=token,
        total_documents=0,
        api_calls=0,
        api_key=api_key,
        used_model="none"
    )
    
    db.add(db_stats)
    db.commit()
    db.refresh(db_stats)
    return {"message": "Email verified successfully", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email, "is_verified": db_user.is_verified, "token": db_user.token}}

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

    db_stats.updated_at = get_ist_time()
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
    if used_model:
        db_stats.used_model = used_model

    db_stats.updated_at = get_ist_time()
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
    new_api_key = generate_api_key()
    db_stats.api_key = new_api_key
    db_stats.updated_at = get_ist_time()
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
    
    db.query(OTP).filter(OTP.email == request.email).delete()
    
    db_otp = OTP(email=db_user.email, otp=otp)
    db.add(db_otp)
    db.commit()
    
    return {"message": "Verification email sent successfully"}