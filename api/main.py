from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from DB import sql
from DB import mongo

uri = "mongodb+srv://sarveshatawane03:y2flIDD1EmOaU5de@cluster0.sssmr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo.connect(uri)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(sql.sql_router)
app.include_router(mongo.mongo_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)