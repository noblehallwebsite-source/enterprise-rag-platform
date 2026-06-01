# import os
# import uuid
# import time
# import logging
# from app.core.celery_app import celery_app  # ✅ ADD This
# from app.services.chunking_service import chunk_text
# from app.services.chroma_service import add_document
# from app.services.file_extraction_service import extract_pdf_text, extract_docx_text

# logger = logging.getLogger(__name__)

# @celery_app.task(
#     name="app.tasks.ingestion_tasks.process_document_ingestion",
#     bind=True,  # Gives us access to self.request for tracking metadata
#     max_retries=3,
#     default_retry_delay=5
# )
# def process_document_ingestion(
#     self,
#     tenant_id: str,
#     text: str,
#     metadata: dict = None
# ):
#     """
#     Executes entirely within an isolated worker process.
#     Chunks text blocks, tracks internal latency metrics, and streams embeddings
#     into the tenant-partitioned vector index with production-ready telemetry.
#     """
#     task_id = self.request.id or str(uuid.uuid4())
#     metadata = metadata or {}
    
#     logger.info(
#         f"[WORKER START] [TaskID: {task_id}] Asynchronous ingestion triggered "
#         f"for tenant_id='{tenant_id}' | Payload size: {len(text)} chars."
#     )
    
#     start_total_time = time.perf_counter()
    
#     try:
#         # 1. Profile Chunking Pipeline Latency
#         start_chunk = time.perf_counter()
#         chunks = chunk_text(text)
#         chunk_duration = time.perf_counter() - start_chunk
        
#         logger.info(
#             f"[WORKER EXEC] [TaskID: {task_id}] Split raw asset into {len(chunks)} chunks "
#             f"in {chunk_duration:.4f}s for tenant_id='{tenant_id}'."
#         )

#         if not chunks:
#             logger.warning(
#                 f"[WORKER WARN] [TaskID: {task_id}] Ingestion payload yielded 0 chunks. "
#                 f"Aborting downstream write workflows for tenant_id='{tenant_id}'."
#             )
#             return {"status": "skipped", "tenant_id": tenant_id, "chunks_created": 0}

#         # 2. Profile Batch Vector Storage Writes
#         start_write = time.perf_counter()
#         for idx, chunk in enumerate(chunks):
#             chunk_id = str(uuid.uuid4())
            
#             # Inject trace parameters into object metadata dictionary
#             enriched_metadata = {
#                 **metadata,
#                 "chunk_index": idx,
#                 "parent_task_id": task_id
#             }
            
#             add_document(
#                 tenant_id=tenant_id,
#                 document_id=chunk_id,
#                 text=chunk,
#                 metadata=enriched_metadata
#             )
            
#         write_duration = time.perf_counter() - start_write
#         total_duration = time.perf_counter() - start_total_time

#         logger.info(
#             f"[WORKER SUCCESS] [TaskID: {task_id}] Storage pipeline commit verified for tenant_id='{tenant_id}'. "
#             f"Metrics -> Total: {total_duration:.3f}s | Chunking: {chunk_duration:.3f}s | VectorDB Write: {write_duration:.3f}s. "
#             f"Total Chunks: {len(chunks)}."
#         )
        
#         return {
#             "status": "completed",
#             "task_id": task_id,
#             "tenant_id": tenant_id,
#             "chunks_created": len(chunks),
#             "execution_metrics": {
#                 "total_seconds": round(total_duration, 4),
#                 "db_write_seconds": round(write_duration, 4)
#             }
#         }
        
#     except Exception as e:
#         total_duration = time.perf_counter() - start_total_time
#         # logger.exception automatically extracts and binds stack traces to stderr/stdout
#         logger.exception(
#             f"[WORKER CRITICAL FAILURE] [TaskID: {task_id}] Vector pipeline crashed after {total_duration:.3f}s "
#             f"for tenant_id='{tenant_id}'. Error details: {str(e)}"
#         )
#         raise e

    

# @celery_app.task(name="app.tasks.ingestion_tasks.process_uploaded_file", ignore_result=False)
# def process_uploaded_file(tenant_id: str, file_path: str, metadata: dict = None):
#     logger.info(f"[WORKER] Processing uploaded file: {file_path} for tenant: {tenant_id}")
    
#     try:
#         extension = os.path.splitext(file_path)[1].lower()

#         # ==========================================
#         # Extract Text
#         # ==========================================
#         if extension == ".pdf":
#             text = extract_pdf_text(file_path)
#         elif extension == ".docx":
#             text = extract_docx_text(file_path)
#         elif extension in [".txt", ".md"]:
#             with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
#                 text = f.read()
#         else:
#             raise Exception(f"Unsupported file type: {extension}")

#         # ==========================================
#         # Chunk + Store
#         # ==========================================
#         chunks = chunk_text(text)
#         logger.info(f"[WORKER] Successfully split payload into {len(chunks)} chunks.")

#         for chunk in chunks:
#             add_document(
#                 tenant_id=tenant_id,
#                 document_id=str(uuid.uuid4()),
#                 text=chunk,
#                 metadata=metadata or {}
#             )

#         logger.info(f"[WORKER SUCCESS] Completed compilation sequence for file: {file_path}")
#         return {
#             "status": "completed",
#             "chunks_created": len(chunks)
#         }

#     except Exception as e:
#         logger.error(f"[WORKER CRITICAL FAILURE] Execution failed for file {file_path}: {str(e)}")
#         raise e
#     finally:
#         # Clear out the file from the shared volume as root immediately after ingestion completes
#         if os.path.exists(file_path):
#             os.remove(file_path)
#             logger.info(f"[WORKER CLEANUP] Removed temporary staging file: {file_path}")










import os
import uuid
import time
import logging
from app.core.celery_app import celery_app
from app.services.chunking_service import chunk_text
from app.services.chroma_service import add_document
from app.services.file_extraction_service import extract_pdf_text, extract_docx_text

# 🔌 Import Relational Database Connection Elements
from app.database.connection import SessionLocal
from app.services.document_service import update_document_status

logger = logging.getLogger(__name__)

@celery_app.task(
    name="app.tasks.ingestion_tasks.process_document_ingestion",
    bind=True,  # Gives us access to self.request for tracking metadata
    max_retries=3,
    default_retry_delay=5
)
def process_document_ingestion(
    self,
    tenant_id: str,
    text: str,
    metadata: dict = None
):
    """
    Executes entirely within an isolated worker process.
    Chunks text blocks, tracks internal latency metrics, and streams embeddings
    into the tenant-partitioned vector index with production-ready telemetry.
    """
    task_id = self.request.id or str(uuid.uuid4())
    metadata = metadata or {}
    
    logger.info(
        f"[WORKER START] [TaskID: {task_id}] Asynchronous ingestion triggered "
        f"for tenant_id='{tenant_id}' | Payload size: {len(text)} chars."
    )
    
    start_total_time = time.perf_counter()
    
    try:
        # 1. Profile Chunking Pipeline Latency
        start_chunk = time.perf_counter()
        chunks = chunk_text(text)
        chunk_duration = time.perf_counter() - start_chunk
        
        logger.info(
            f"[WORKER EXEC] [TaskID: {task_id}] Split raw asset into {len(chunks)} chunks "
            f"in {chunk_duration:.4f}s for tenant_id='{tenant_id}'."
        )

        if not chunks:
            logger.warning(
                f"[WORKER WARN] [TaskID: {task_id}] Ingestion payload yielded 0 chunks. "
                f"Aborting downstream write workflows for tenant_id='{tenant_id}'."
            )
            return {"status": "skipped", "tenant_id": tenant_id, "chunks_created": 0}

        # 2. Profile Batch Vector Storage Writes
        start_write = time.perf_counter()
        for idx, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            
            # Inject trace parameters into object metadata dictionary
            enriched_metadata = {
                **metadata,
                "chunk_index": idx,
                "parent_task_id": task_id
            }
            
            add_document(
                tenant_id=tenant_id,
                document_id=chunk_id,
                text=chunk,
                metadata=enriched_metadata
            )
            
        write_duration = time.perf_counter() - start_write
        total_duration = time.perf_counter() - start_total_time

        logger.info(
            f"[WORKER SUCCESS] [TaskID: {task_id}] Storage pipeline commit verified for tenant_id='{tenant_id}'. "
            f"Metrics -> Total: {total_duration:.3f}s | Chunking: {chunk_duration:.3f}s | VectorDB Write: {write_duration:.3f}s. "
            f"Total Chunks: {len(chunks)}."
        )
        
        return {
            "status": "completed",
            "task_id": task_id,
            "tenant_id": tenant_id,
            "chunks_created": len(chunks),
            "execution_metrics": {
                "total_seconds": round(total_duration, 4),
                "db_write_seconds": round(write_duration, 4)
            }
        }
        
    except Exception as e:
        total_duration = time.perf_counter() - start_total_time
        logger.exception(
            f"[WORKER CRITICAL FAILURE] [TaskID: {task_id}] Vector pipeline crashed after {total_duration:.3f}s "
            f"for tenant_id='{tenant_id}'. Error details: {str(e)}"
        )
        raise e


# =====================================================================
# UPDATED BINARY FILE WORKER PROCESSING ROUTE WITH TRANSITIONAL TELEMETRY
# =====================================================================
@celery_app.task(name="app.tasks.ingestion_tasks.process_uploaded_file", ignore_result=False)
def process_uploaded_file(
    tenant_id: str, 
    document_id: str,     # 🔑 Injected tracking identifier param
    file_path: str, 
    metadata: dict = None
):
    logger.info(f"[WORKER] Processing uploaded file: {file_path} for document row: {document_id}")
    
    # 🔌 Connect to PostgreSQL socket engine
    db = SessionLocal()
    chunks = []

    try:
        extension = os.path.splitext(file_path)[1].lower()

        # ==========================================
        # 1. Extract Text Base
        # ==========================================
        if extension == ".pdf":
            text = extract_pdf_text(file_path)
        elif extension == ".docx":
            text = extract_docx_text(file_path)
        elif extension in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            raise Exception(f"Unsupported file type: {extension}")

        # ==========================================
        # 2. Chunk Fragment Analysis
        # ==========================================
        chunks = chunk_text(text)
        logger.info(f"[WORKER] Successfully split payload into {len(chunks)} chunks.")

        # 🔄 Update system-of-record status to show chunk metrics
        update_document_status(
            db=db,
            document_id=document_id,
            status="PROCESSING",
            chunks_created=len(chunks)
        )

        # ==========================================
        # 3. Vector DB Target Load Loop
        # ==========================================
        for chunk in chunks:
            add_document(
                tenant_id=tenant_id,
                document_id=str(uuid.uuid4()),
                text=chunk,
                metadata={
                    **(metadata or {}),
                    "parent_document_id": document_id
                }
            )

        # 🎉 Success Update Matrix
        logger.info(f"[WORKER SUCCESS] Completed compilation sequence for file: {file_path}")
        update_document_status(
            db=db,
            document_id=document_id,
            status="COMPLETED",
            chunks_created=len(chunks)
        )

        return {
            "status": "completed",
            "document_id": document_id,
            "chunks_created": len(chunks)
        }

    except Exception as e:
        logger.error(f"[WORKER CRITICAL FAILURE] Execution failed for file {file_path}: {str(e)}")
        
        # ❌ Exception state rollback update
        try:
            update_document_status(
                db=db,
                document_id=document_id,
                status="FAILED",
                chunks_created=len(chunks)
            )
        except Exception as db_err:
            logger.error(f"[WORKER] Failed logging error-state to relational database: {str(db_err)}")
            
        raise e
        
    finally:
        # 🔌 Safe resource teardown loops
        db.close()
        logger.info(f"[WORKER] Database transaction container released for {document_id}")
        
        # Clear out the file from the shared volume immediately after ingestion completes
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"[WORKER CLEANUP] Removed temporary staging file: {file_path}")