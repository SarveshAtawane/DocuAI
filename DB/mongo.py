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
from DB.sql import get_db
from DB.sql import User
import pytz
import datetime
from datetime import timedelta
def connect(uri):
    """Connects to MongoDB using the provided URI and pings the server."""
    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# MongoDB connection
uri = "mongodb+srv://sarveshatawane03:y2flIDD1EmOaU5de@cluster0.sssmr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = connect(uri)
db = client["FAQ"]
logs_db = client["logs"]

security = HTTPBearer()
mongo_router = APIRouter()

# Function to verify JWT token
def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    db_user = db.query(User).filter(User.token == token).first()
    if not db_user or db_user.token == "None":
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return token
IST = pytz.timezone('Asia/Kolkata')
def get_ist_time():
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.astimezone(IST)
# Pydantic model for request data
class DocumentLinks(BaseModel):
    github_repo_link: Optional[HttpUrl] = None
    website_link: Optional[HttpUrl] = None

# Function to log user actions
def log_action(user_token: str, action: str, details: dict):
    log_collection = logs_db[user_token]
    print(get_ist_time())
    log_document = {
        "action": action,
        "details": details,
        "timestamp": get_ist_time()
    }
    log_collection.insert_one(log_document)
    print(log_document)

# Endpoint to upload documents and log actions
class UserDetailsResponse(BaseModel):
    username: str
    email: str

@mongo_router.get("/user/details/", response_model=UserDetailsResponse)
async def get_user_details(
    token: str = Depends(verify_jwt),
    db: Session = Depends(get_db)
):
    try:
        # Get user from SQL database using token
        user = db.query(User).filter(User.token == token).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        

 
        
        # Construct response
        user_details = UserDetailsResponse(
            username=user.username,
            email=user.email,
            # total_documents=total_documents,
        )

        
        return user_details
        
    except Exception as e:
        logging.error(f"Error retrieving user details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error retrieving user details: {str(e)}"
        )
@mongo_router.post("/doc_upload/")
async def doc_upload(
    files: List[UploadFile] = File(...),
    github_repo_link: Optional[str] = Form(None),
    website_link: Optional[str] = Form(None),
    token: str = Depends(verify_jwt)
    
):
    allowed_types = ["text/plain", "application/pdf"]
    file_results = []
    link_results = []

    try:
        collection = db[token]
        
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
            # Log file upload action
            log_action(token, "uploaded", {
                "filename": file.filename,
                "file_type": file.content_type,
                "operation": "uploaded"
            })

        # Upload GitHub link
        if github_repo_link:
            github_link_document = {
                "type": "github_link",
                "github_repo_link": github_repo_link
            }
            
            result = collection.insert_one(github_link_document)
            link_results.append({
                "id": str(result.inserted_id),
                "github_repo_link": github_repo_link
            })
            # Log GitHub link upload action
            log_action(token, "added", {
                "github_repo_link": github_repo_link,
                "operation": "added"
            })
        
        # Upload Website link
        if website_link:
            website_link_document = {
                "type": "website_link",
                "website_link": website_link
            }
            
            result = collection.insert_one(website_link_document)
            link_results.append({
                "id": str(result.inserted_id),
                "website_link": website_link
            })
            # Log Website link upload action
            log_action(token, "added", {
                "website_link": website_link,
                "operation": "added"
            })
        
        response = {
            "message": "Files and links uploaded successfully", 
            "files": file_results,
            "links": link_results
        }
        
        return response
    except Exception as e:
        logging.error(f"Error uploading documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error uploading documents: {str(e)}")

# Endpoint to retrieve recent updates from logs
@mongo_router.get("/logs/recent_updates/")
async def get_recent_updates(
    token: str = Depends(verify_jwt),
    limit: int = Query(10, description="Number of recent updates to retrieve")
):
    try:
        # Access the user's log collection
        log_collection = logs_db[token]
        
        # Retrieve recent logs, sorted by timestamp in descending order
        recent_logs = log_collection.find().sort("timestamp", -1).limit(limit)
        
        # Format the logs to be JSON serializable
        updates = [
            {
                "action": log.get("action"),
                "details": log.get("details"),
                "timestamp": log.get("timestamp")
            }
            for log in recent_logs
        ]
        
        return {"recent_updates": updates}
    
    except Exception as e:
        logging.error(f"Error retrieving recent updates: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving recent updates: {str(e)}")

# Endpoint to delete a document
from bson import ObjectId

# Endpoint to delete a document
@mongo_router.delete("/doc_delete/{doc_id}/")
async def doc_delete(
    doc_id: str,
    token: str = Depends(verify_jwt)
):
    try:
        collection = db[token]
        
        # Convert the doc_id to ObjectId
        object_id = ObjectId(doc_id)
        
        # Fetch the document before deleting to print its details
        document = collection.find_one({"_id": object_id})
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Print the document details (type and name)
        print(f"Document ID: {doc_id}")
        print(f"Document Name: {document.get('filename', 'N/A')}")
        print(f"Document Type: {document.get('type', 'N/A')}")
        doc_name = ""
        if document.get("type") == "website_link":
            print(f"Website Link: {document.get('website_link', 'N/A')}")
            doc_name = document.get('website_link', 'N/A')
        else:
            print(f"File Type: {document.get('file_type', 'N/A')}")
            doc_name = document.get('filename', 'N/A')
        # Attempt to delete the document by ID
        result = collection.delete_one({"_id": object_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Log delete action
        log_action(token, "delete", {
            "filename": doc_name,
            "operation": "deleted"
        })

        return {"message": "Document deleted successfully"}
    
    except Exception as e:
        logging.error(f"Error deleting document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

# Endpoint to retrieve all documents
@mongo_router.get("/documents/")
async def get_documents(
    token: str = Depends(verify_jwt)
):
    try:
        collection = db[token]
        
        # Retrieve all documents from the user's collection
        documents = collection.find()
        
        # Format documents to include their IDs and other details
        document_list = [
            {
                "id": str(doc["_id"]),
                "filename": doc.get("filename"),
                "type": doc.get("type"),
                "file_type": doc.get("file_type"),
                # Add other fields as necessary
            }
            for doc in documents
        ]
        
        return {"documents": document_list}
    
    except Exception as e:
        logging.error(f"Error retrieving documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")
