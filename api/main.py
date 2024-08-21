from fastapi import FastAPI
from DB import sql
from DB import mongo

uri = "mongodb+srv://sarveshatawane03:y2flIDD1EmOaU5de@cluster0.sssmr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo.connect(uri)

app = FastAPI()
app.include_router(sql.sql_router)
app.include_router(mongo.mongo_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)