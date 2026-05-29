from celery import Celery

# Instantiate Celery and point it to the container-linked Redis Broker instance
celery_app = Celery(
    "enterprise_rag",
    broker="redis://redis-broker:6379/0",  # 🔥 Fixed hostname to match your docker-compose service
    backend="redis://redis-broker:6379/0"
)

# Core stability configuration updates
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Forces worker to discover tasks inside our ingestion modules automatically
    imports=["app.tasks.ingestion_tasks"] 
)