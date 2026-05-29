from celery import Celery

# =====================================================================
# ENTERPRISE DISTRIBUTED TASK INFRASTRUCTURE CONFIGURATION
# =====================================================================

# Instantiate Celery and point it to the container-linked Redis Broker instance
celery_app = Celery(
    "enterprise_rag",
    broker="redis://redis-broker:6379/0",  # Resolves dynamically via Docker internal DNS
    backend="redis://redis-broker:6379/0"  # Tracks state and task return conditions
)

# Core stability configuration updates
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # 🔥 Production Stability: Ensures safe socket reconnect handling if Redis boots slowly
    broker_connection_retry_on_startup=True,
    
    # Forces worker pool daemon to discover tasks inside our ingestion modules automatically
    imports=["app.tasks.ingestion_tasks"] 
)