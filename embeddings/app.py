# app.py
from fastapi import FastAPI
from celery import Celery
import time

app = FastAPI()

# Configure Celery
celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def count_to_100():
    for i in range(1, 101):
        print(i)
        time.sleep(1)

@app.post("/start-counter")
async def start_counter():
    task = count_to_100.delay()
    return {"message": "Counter started", "task_id": task.id}

# To run:
# 1. Start Redis server
# 2. Run Celery worker: celery -A app.celery worker --loglevel=info
# 3. Run FastAPI server: uvicorn app:app --reload