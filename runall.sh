#!/bin/bash

echo "Starting FastAPI app on port 8080..."
python3 -m api.main &
celery -A embeddings.website_loader worker --loglevel=info --concurrency=2 --max-memory-per-child=500000 -Q crawl_queue &



cd /home/saru/Desktop/Resume_projects/Faq/embeddings
uvicorn main2:app --reload --port 8080 &

cd /home/saru/Desktop/Resume_projects/Faq/embeddings
celery -A embed.celery_app worker --loglevel=info --concurrency=2 --max-memory-per-child=500000 -Q embedding_queue &


echo "Starting FastAPI app on port 8800..."
cd /home/saru/Desktop/Resume_projects/Faq/Rag_code
uvicorn app:app --reload --port 8800 &
echo "Starting frontend application..."
cd /home/saru/Desktop/Resume_projects/Faq/frontend/docuai-app
npm start &
wait