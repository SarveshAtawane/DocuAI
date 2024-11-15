from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from embed import generate_embeddings_task

app = FastAPI()

class TokenRequest(BaseModel):
    token: str

@app.post("/generate_embeddings")
async def generate_embeddings_endpoint(request: TokenRequest):
    try:
        task = generate_embeddings_task.delay(request.token)
        return {"message": "Embedding generation started", "task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting task: {str(e)}")
