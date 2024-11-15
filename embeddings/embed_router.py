# router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import embeddings.embed as embed

router = APIRouter()

class EmbeddingRequest(BaseModel):
    token: str

class EmbeddingResponse(BaseModel):
    task_id: str
    status: str

@router.post("/generate-embeddings", response_model=EmbeddingResponse)
async def create_embeddings(request: EmbeddingRequest):
    """
    API endpoint to trigger embedding generation for a specific token.
    Returns a task ID that can be used to check the status.
    """
    try:
        task = embed.generate_embeddings.delay(request.token)
        return EmbeddingResponse(
            task_id=str(task.id),
            status="Processing"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error starting embedding generation: {str(e)}"
        )

@router.get("/embedding-status/{task_id}", response_model=Dict[str, Any])
async def get_embedding_status(task_id: str):
    """
    Check the status of an embedding generation task.
    """
    try:
        task = generate_embeddings.AsyncResult(task_id)
        
        if task.ready():
            if task.successful():
                return {
                    "status": "Completed",
                    "result": task.get()
                }
            else:
                return {
                    "status": "Failed",
                    "error": str(task.result)
                }
        
        return {
            "status": "Processing"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking task status: {str(e)}"
        )