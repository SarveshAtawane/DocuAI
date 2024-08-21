from pymongo import MongoClient
from pymongo.server_api import ServerApi
from fastapi import APIRouter, Depends, HTTPException
client = None
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
client = MongoClient("mongodb://localhost:27017")
db = client["FAQ"]

# Pydantic model for the request data
class DocumentData(BaseModel):
    pdf_file: Optional[bytes]
    pdf_file_name: Optional[str]
    txt_file: Optional[str]
    txt_file_name: Optional[str]
    github_id_links: Optional[List[str]]
    github_docs_links: Optional[List[str]]

@mongo_router.post("/doc_upload/")
async def doc_upload(
    file: Union[UploadFile, None] = File(default=None),
    data: DocumentData = None
):
    if file is None and data is None:
        raise HTTPException(status_code=400, detail="No file or document data provided")

    try:
        # Save the file or document data to MongoDB
        collection = db["your_collection_name"]

        if file:
            file_data = await file.read()
            collection.insert_one({"file_content": file_data, "file_type": file.content_type})
            return {"message": "Document uploaded successfully!"}
        elif data:
            document = data.dict(exclude_none=True)
            result = collection.insert_one(document)
            return {"message": "Document uploaded successfully!", "id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {e}")