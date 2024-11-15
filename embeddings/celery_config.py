# celery_config.py
from celery import Celery

celery_app = Celery(
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.conf.update(
    task_track_started=True,
    worker_concurrency=2,
    worker_max_memory_per_child=500000,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        'path.to.process_website_content': {'queue': 'crawl_queue'},
        'path.to.generate_embeddings_task': {'queue': 'embedding_queue'},
    },
)
