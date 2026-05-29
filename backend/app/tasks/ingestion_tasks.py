import uuid
import logging
from app.tasks.celery_app import celery_app
from app.services.chunking_service import chunk_text
from app.services.chroma_service import add_document

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.ingestion_tasks.process_document_ingestion")
def process_document_ingestion(
    tenant_id: str,
    text: str,
    metadata: dict = None
):
    """
    Executes entirely within an isolated worker process.
    Chunks text blocks and streams them into the tenant-partitioned vector index.
    """
    logger.info(f"[WORKER] Initiating asynchronous background ingestion for tenant: {tenant_id}")
    
    try:
        chunks = chunk_text(text)
        logger.info(f"[WORKER] Successfully split raw asset payload into {len(chunks)} chunks.")

        for chunk in chunks:
            chunk_id = str(uuid.uuid4())
            
            # Enforces data tenant isolation context down to the vector collection
            add_document(
                tenant_id=tenant_id,
                document_id=chunk_id,
                text=chunk,
                metadata=metadata or {}
            )

        logger.info(f"[WORKER SUCCESS] Completed compilation sequence for tenant: {tenant_id}")
        return {
            "status": "completed",
            "tenant_id": tenant_id,
            "chunks_created": len(chunks)
        }
        
    except Exception as e:
        logger.error(f"[WORKER CRITICAL FAILURE] Execution failed for tenant {tenant_id}: {str(e)}")
        raise e