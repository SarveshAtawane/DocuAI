import os
from fastapi import FastAPI
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
from celery import Celery

# Load environment variables
load_dotenv()

app = FastAPI()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

class DocumentProcess(BaseModel):
    token: str
    root_folder: str
    user_email: str

def create_chunks(text, chunk_size=200, overlap=50):
    chunks = []
    words = text.split()
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def process_file(file_path, collection):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    chunks = create_chunks(text)
    for chunk in chunks:
        embedding = model.encode(chunk).tolist()
        document = {
            "text": chunk,
            "embedding": embedding,
            "file_path": file_path
        }
        collection.insert_one(document)

@celery_app.task(bind=True)
def process_folders(self, token: str, root_path: str, user_email: str):
    for folder_name in os.listdir(root_path):
        folder_path = os.path.join(root_path, folder_name)
        if os.path.isdir(folder_path):
            collection = db[f"{token}_{folder_name}"]
            
            for subfolder in os.listdir(folder_path):
                subfolder_path = os.path.join(folder_path, subfolder)
                if os.path.isdir(subfolder_path):
                    if os.path.exists(subfolder_path):
                        for filename in os.listdir(subfolder_path):
                            if filename.endswith('.txt'):
                                print(f"Processing {filename}")
                                file_path = os.path.join(subfolder_path, filename)
                                process_file(file_path, collection)
            print(f"Processed folder {folder_name}")
    
    # Clean up the temporary folder after processing
    import shutil
    shutil.rmtree(root_path, ignore_errors=True)

    return {"message": "Processing completed", "user_email": user_email}

@app.post("/process_documents/")
async def process_documents(doc_process: DocumentProcess):
    task = process_folders.delay(doc_process.token, doc_process.root_folder, doc_process.user_email)
    return {"message": "Document processing task has been queued.", "task_id": str(task.id)}

@app.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is waiting for execution'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': str(task.info),
            'user_email': task.info['user_email'] if task.info else None
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info),
            'user_email': None
        }
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)