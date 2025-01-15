from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from model import RAGModel

app = FastAPI(title="RAG Chat API", description="API for conversational RAG system")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ChatRequest(BaseModel):
    query: str
    entity_name: str
    token: str

# Response model
class ChatResponse(BaseModel):
    response: str
    status: str

# Initialize RAG model
rag_model = RAGModel()

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    print(request)
    try:
        print(request)
        # Get response from RAG model
        response = rag_model.chat_with_rag(
            query=request.query,
            entity_name=request.entity_name,
            token=request.token
        )
        
        return ChatResponse(
            response=response,
            status="success"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8800)