from celery_config import celery_app
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import logging
import io
import base64
from typing import List
import fitz 
import torch
import sys
sys.path.append("/home/saru/Desktop/Resume_projects/Faq")
from auth import email_verification
# from DB import sql
import requests

BASE_URL = "http://localhost:8000"  # Adjust this to match your server URL


logging.basicConfig(level=logging.INFO)
torch.multiprocessing.set_start_method("spawn", force=True)
def get_mongo_client():
    """Create a MongoDB client within the task to ensure fork safety."""
    return MongoClient("mongodb+srv://sarveshatawane03:y2flIDD1EmOaU5de@cluster0.sssmr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

def chunk_text(text: str, chunk_size: int = 250) -> List[str]:
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def extract_pdf_content_from_binary(binary_content: bytes) -> str:
    text = ""
    try:
        pdf_stream = io.BytesIO(binary_content)
        with fitz.open(stream=pdf_stream, filetype="pdf") as pdf:
            for page_num, page in enumerate(pdf):
                page_text = page.get_text("text")
                text += page_text
                logging.info(f"Extracted text from page {page_num}")
    except Exception as e:
        logging.error(f"Error extracting PDF content: {e}")
        raise
    return text.strip()

def get_binary_content(file_content) -> bytes:
    try:
        if isinstance(file_content, bytes):
            return file_content
        if isinstance(file_content, str):
            if ';base64,' in file_content:
                file_content = file_content.split(';base64,')[1]
            padding = 4 - (len(file_content) % 4) if len(file_content) % 4 else 0
            file_content += '=' * padding
            return base64.b64decode(file_content)
        raise ValueError(f"Unsupported content type: {type(file_content)}")
    except Exception as e:
        logging.error(f"Error converting content to binary: {e}")
        raise

@celery_app.task(name="path.to.generate_embeddings_task", queue="embedding_queue")
def generate_embeddings_task(token: str):
    client = get_mongo_client()
    db = client["FAQ"]
    collection = db[token]
    embedding_collection = db[f"{token}_embedding"]
    embedding_collection.delete_many({})
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2', device='cuda')

    for document in collection.find():
        object_id = str(document["_id"])
        content_source = document["type"]
        logging.info(f"Processing document {object_id} of type {content_source}")

        embedding_result = {
            "id": object_id,
            "source": content_source,
            "original_reference": document,
            "embeddings": []
        }

        try:
            if content_source == "website_content":
                text_content = document["content"]
                chunks = chunk_text(text_content)
                for chunk in chunks:
                    embedding = model.encode(chunk).tolist()
                    embedding_result["embeddings"].append({"text": chunk, "embedding": embedding})

            elif content_source == "file":
                if document.get("file_type") == "application/pdf":
                    file_content = document.get("file_content")
                    if not file_content:
                        logging.warning(f"No file content found for document {object_id}")
                        continue

                    binary_content = get_binary_content(file_content)
                    text_content = extract_pdf_content_from_binary(binary_content)
                    chunks = chunk_text(text_content)
                    for chunk in chunks:
                        embedding = model.encode(chunk).tolist()
                        embedding_result["embeddings"].append({"text": chunk, "embedding": embedding})

                elif document.get("file_type") == "text/plain":
                    file_content = document.get("file_content")
                    binary_content = get_binary_content(file_content)
                    text_content = binary_content.decode('utf-8', errors='replace')
                    chunks = chunk_text(text_content)
                    for chunk in chunks:
                        embedding = model.encode(chunk).tolist()
                        embedding_result["embeddings"].append({"text": chunk, "embedding": embedding})

            if embedding_result["embeddings"]:
                embedding_collection.insert_one(embedding_result)
                logging.info(f"Successfully generated embeddings for document {object_id}")
            else:
                logging.warning(f"No embeddings generated for document {object_id}")

        except Exception as e:
            logging.error(f"Error processing document {object_id}: {str(e)}")
            continue
    
    def get_user_info(token: str) -> dict:
        """Get user information using JWT token"""
        user_info_url = f"{BASE_URL}/user-info/"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()
    print(get_user_info(token))
    logging.info("Embedding generation complete.")
    email_verification.send_api_key_notification(get_user_info(token)["email"], get_user_info(token)["username"], get_user_info(token)["api_key"])
    # email_verification.send_email_with_otp('sarveshatawane03@gmail.com',"sarves")
    print("Embedding generation complete ansd I am herreee.")