from pymongo import MongoClient
from pymongo.server_api import ServerApi
from fastapi import APIRouter, Depends, HTTPException
from fastapi import HTTPException, UploadFile, File
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
import jwt
import logging
from typing import List
from DB.sql import get_db, User
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
from sqlalchemy.orm import Session
import logging
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo import MongoClient
import logging
from typing import List, Optional, Union
from pydantic import BaseModel, HttpUrl
from bson import ObjectId


def connect(uri):
    """Connects to MongoDB using the provided URI and pings the server."""
    client = MongoClient(uri, server_api=ServerApi('1'))

    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"An error occurred: {e}")
from pymongo import MongoClient
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from typing import Union, List, Optional
from pydantic import BaseModel

mongo_router = APIRouter()

# MongoDB client
uri = "mongodb+srv://sarveshatawane03:y2flIDD1EmOaU5de@cluster0.sssmr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(uri)
db = client["FAQ"]
security = HTTPBearer()
# Pydantic model for the request data


import logging
def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    db_user = db.query(User).filter(User.token == token).first()
    if not db_user or db_user.token == "None":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return token

class DocumentLinks(BaseModel):
    github_repo_link: Optional[HttpUrl] = None
    website_link: Optional[HttpUrl] = None

@mongo_router.post("/doc_upload/")
async def doc_upload(
    files: List[UploadFile] = File(...),
    github_repo_link: Optional[str] = Form(None),
    website_link: Optional[str] = Form(None),
    token: str = Depends(verify_jwt)
):
    allowed_types = ["text/plain", "application/pdf"]
    file_results = []
    link_result = None

    try:
        collection = db[token]  # Use the token as the collection name
        
        # Upload files
        for file in files:
            if file.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a text or PDF file")
            
            file_data = await file.read()
            file_document = {
                "type": "file",
                "filename": file.filename,
                "file_content": file_data,
                "file_type": file.content_type,
            }
            
            result = collection.insert_one(file_document)
            file_results.append({
                "filename": file.filename,
                "id": str(result.inserted_id),
            })

        # Upload links
        if github_repo_link or website_link:
            link_document = {
                "type": "link",
                "github_repo_link": github_repo_link,
                "website_link": website_link
            }
            
            result = collection.insert_one(link_document)
            link_result = {
                "id": str(result.inserted_id),
                "github_repo_link": github_repo_link,
                "website_link": website_link
            }
        
        response = {
            "message": "Files uploaded successfully", 
            "files": file_results,
        }
        
        if link_result:
            response["links"] = link_result
        
        return response
    except Exception as e:
        logging.error(f"Error uploading documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error uploading documents: {str(e)}")