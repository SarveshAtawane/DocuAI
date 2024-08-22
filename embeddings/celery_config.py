from celery import Celery

app = Celery('vector_embedding_project')

# Configure Celery
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'

# Optional: Configure task routes, concurrency, etc.
app.conf.task_routes = {'tasks.create_vector_embedding': {'queue': 'embedding'}}
app.conf.worker_concurrency = 4