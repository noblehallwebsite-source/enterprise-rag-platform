# import uuid

# from fastapi import APIRouter

# from app.models.request_models import (
#     DocumentRequest,
#     LargeDocumentRequest,
#     SearchRequest
# )

# from app.services.chroma_service import (
#     add_document,
#     search_documents
# )

# from app.services.chunking_service import (
#     chunk_text
# )

# router = APIRouter()


# @router.post("/documents")
# def store_document(
#     data: DocumentRequest
# ):

#     document_id = str(uuid.uuid4())

#     add_document(
#         document_id=document_id,
#         text=data.text,
#         metadata={
#             "source": data.source,
#             "environment": data.environment,
#             "severity": data.severity,
#             "service": data.service
#         }
#     )

#     return {
#         "message": "Document stored successfully",
#         "document_id": document_id
#     }


# @router.post("/documents/large")
# def store_large_document(
#     data: LargeDocumentRequest
# ):

#     chunks = chunk_text(data.text)

#     for chunk in chunks:

#         chunk_id = str(uuid.uuid4())

#         add_document(
#             document_id=chunk_id,
#             text=chunk,
#             metadata={
#                 "source": data.source,
#                 "environment": data.environment,
#                 "severity": data.severity,
#                 "service": data.service
#             }
#         )

#     return {
#         "message": "Large document stored",
#         "chunks_created": len(chunks)
#     }


# @router.post("/search")
# def semantic_search(
#     data: SearchRequest
# ):

#     filters = {
#         "environment": data.environment,
#         "severity": data.severity,
#         "source": data.source,
#         "service": data.service
#     }

#     results = search_documents(
#         query=data.query,
#         filters=filters
#     )

#     return {
#         "query": data.query,
#         "filters": filters,
#         "results": results
#     }









# import os
# import uuid
# import logging

# from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form

# from app.models.request_models import (
#     DocumentRequest,
#     LargeDocumentRequest,
#     SearchRequest
# )

# from app.services.chroma_service import (
#     add_document,
#     search_documents
# )

# # 🔥 Import authorization gateway layer
# from app.services.security_service import (
#     authorize_request
# )

# from app.tasks.ingestion_tasks import (
#     process_document_ingestion,
#     process_uploaded_file
# )

# from celery.result import AsyncResult
# from app.core.celery_app import celery_app  # ✅ ADD This

# router = APIRouter()
# logger = logging.getLogger(__name__)

# # Keep paths simple matching your workspace working directory layout
# UPLOAD_DIR = "/app/uploads" if os.path.exists("/app") else "uploads"

# # =====================================================================
# # 1. STANDARD DOCUMENT INGESTION ROUTE (SYNCHRONOUS / FAST EXECUTION)
# # =====================================================================
# @router.post("/documents", status_code=status.HTTP_201_CREATED)
# def store_document(
#     data: DocumentRequest,
#     auth: dict = Depends(authorize_request)  # 🔥 Intercepts header credential state
# ):
#     """
#     Handles immediate insertion of brief documents, snippets, or metadata adjustments.
#     Executes synchronously within the request lifecycle for instant validation feedback.
#     """
#     # 🔥 STEP 7 CROSS-CHECK: Deny spoofing payloads immediately
#     if auth["tenant_id"] != data.tenant_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Access Denied: The provided API credential token is not authorized to modify this tenant workspace."
#         )

#     document_id = str(uuid.uuid4())

#     add_document(
#         tenant_id=data.tenant_id,
#         document_id=document_id,
#         text=data.text,
#         metadata={
#             "source": data.source,
#             "environment": data.environment,
#             "severity": data.severity,
#             "service": data.service
#         }
#     )

#     return {
#         "message": "Document stored successfully",
#         "tenant_id": data.tenant_id,
#         "document_id": document_id
#     }


# # =====================================================================
# # 2. LARGE DOCUMENT INGESTION ROUTE (ASYNCHRONOUS / DISTRIBUTED WORKER)
# # =====================================================================
# @router.post("/documents/large", status_code=status.HTTP_202_ACCEPTED)
# def store_large_document(
#     data: LargeDocumentRequest,
#     auth: dict = Depends(authorize_request)  # 🔥 Intercepts header credential state
# ):
#     """
#     Handles massive system logs, dumps, or document uploads.
#     Offloads execution instantly to Celery via Redis to prevent FastAPI thread starvation 
#     and shield ChromaDB from concurrent multi-container write conflicts.
#     """
#     # 🔥 STEP 7 CROSS-CHECK: Deny spoofing payloads immediately
#     if auth["tenant_id"] != data.tenant_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Access Denied: The provided API credential token is not authorized to modify this tenant workspace."
#         )

#     # Package metadata parameters to pass cleanly through the Celery serializer
#     metadata_payload = {
#         "source": data.source,
#         "environment": data.environment,
#         "severity": data.severity,
#         "service": data.service
#     }

#     # 🔥 Dispatch processing to the Celery broker via .delay()
#     task = process_document_ingestion.delay(
#         tenant_id=data.tenant_id,
#         text=data.text,
#         metadata=metadata_payload
#     )

#     return {
#         "message": "Large document accepted and queued for asynchronous background processing.",
#         "tenant_id": data.tenant_id,
#         "task_id": task.id,
#         "status": "Accepted"
#     }


# # =====================================================================
# # 3. STANDALONE SEMANTIC SEARCH ROUTE (TENANT-ISOLATED & PROTECTED)
# # =====================================================================
# @router.post("/search", status_code=status.HTTP_200_OK)
# def semantic_search(
#     data: SearchRequest,
#     auth: dict = Depends(authorize_request)  # 🔥 Intercepts header credential state
# ):
#     """
#     Performs isolated real-time semantic query routing.
#     Limits collection operations strictly to the workspace bound to the tenant payload.
#     """
#     # 🔥 STEP 7 CROSS-CHECK: Deny spoofing payloads immediately
#     if auth["tenant_id"] != data.tenant_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Access Denied: The provided API credential token is not authorized to access this tenant workspace."
#         )

#     filters = {
#         "environment": data.environment,
#         "severity": data.severity,
#         "source": data.source,
#         "service": data.service
#     }

#     results = search_documents(
#         tenant_id=data.tenant_id,
#         query=data.query,
#         filters=filters
#     )

#     return {
#         "query": data.query,
#         "tenant_id": data.tenant_id,
#         "filters": filters,
#         "results": results
#     }


# # =====================================================================
# # 4. BINARY ENTERPRISE FILE UPLOAD ROUTE (SECURED, MULTIPART FORM DATA)
# # =====================================================================
# @router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
# async def upload_document(
#     tenant_id: str = Form(...),              # 🔥 Explicitly marked as Form data 
#     file: UploadFile = File(...),            # Handles incoming binary file stream
#     auth: dict = Depends(authorize_request)  # 🔥 Enforces platform key verification
# ):
#     """
#     Accepts raw enterprise documents (PDF/DOCX) via multipart/form-data payload,
#     safely verifies the tenant authorization token, writes the temporary payload to disk,
#     and forwards background extraction logic straight to our async worker queue.
#     """
#     # 🔥 Security Cross-Check: Prevent cross-tenant data leakage or malicious parameter injection
#     if auth["tenant_id"] != tenant_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Access Denied: The provided API credential token is not authorized to modify this tenant workspace."
#         )

#     # ==========================================
#     # Save Uploaded File
#     # ==========================================
#     extension = os.path.splitext(file.filename)[1]
#     unique_filename = f"{uuid.uuid4()}{extension}"
#     file_path = os.path.join(UPLOAD_DIR, unique_filename)

#     try:
#         with open(file_path, "wb") as buffer:
#             buffer.write(await file.read())
#     except Exception as e:
#         logger.error(f"[API ERROR] Failed writing uploaded artifact to storage volume: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Failed to write file to disk storage: {str(e)}"
#         )

#     # ==========================================
#     # Queue Background Processing
#     # ==========================================
#     task = process_uploaded_file.delay(
#         tenant_id=tenant_id,
#         file_path=file_path,
#         metadata={
#             "original_filename": file.filename
#         }
#     )

#     return {
#         "message": "File uploaded successfully and verification processing initiated.",
#         "tenant_id": tenant_id,
#         "task_id": task.id
#     }




# # =====================================================================
# # 5. ASYNCHRONOUS TASK TELEMETRY ROUTE (STATUS TRACKING)
# # =====================================================================
# @router.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
# def get_task_status(task_id: str):
#     """
#     Queries the Redis result backend to fetch live task execution telemetry.
#     Enables frontend UI polling loops to monitor document chunking progress.
#     """
#     try:
#         # Connects directly to the task state context inside Redis
#         task_result = AsyncResult(task_id, app=celery_app)
        
#         # If the task failed, task_result.result contains the raw exception string
#         result_payload = None
#         if task_result.status == "SUCCESS":
#             result_payload = task_result.result
#         elif task_result.status == "FAILURE":
#             result_payload = str(task_result.result)

#         return {
#             "task_id": task_id,
#             "status": task_result.status,          # PENDING, STARTED, SUCCESS, FAILURE
#             "result": result_payload,               # Returns metadata output dictionary or error stack
#             "traceback": task_result.traceback if task_result.status == "FAILURE" else None
#         }
        
#     except Exception as e:
#         logger.error(f"[API ERROR] Failed retrieving telemetry status for task {task_id}: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Internal status tracking layer failed: {str(e)}"
#         )







import os
import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session

from app.models.request_models import (
    DocumentRequest,
    LargeDocumentRequest,
    SearchRequest
)

from app.services.chroma_service import (
    add_document,
    search_documents,
    delete_document_chunks,
    get_document_chunks
)

# 🔥 Import authorization gateway layer
from app.services.security_service import (
    authorize_request
)

# 🔌 Import Relational Database Core Dependencies
from app.database.dependencies import (
    get_db
)
from app.services.document_service import (
    create_document,
    get_documents,
    delete_document,
    get_document_by_id
)

from app.tasks.ingestion_tasks import (
    process_document_ingestion,
    process_uploaded_file
)

from celery.result import AsyncResult
from app.core.celery_app import celery_app
from app.models.document import Document

router = APIRouter()
logger = logging.getLogger(__name__)

# Keep paths simple matching your workspace working directory layout
UPLOAD_DIR = "/app/uploads" if os.path.exists("/app") else "uploads"

# =====================================================================
# 1. STANDARD DOCUMENT INGESTION ROUTE (SYNCHRONOUS / FAST EXECUTION)
# =====================================================================
@router.post("/documents", status_code=status.HTTP_201_CREATED)
def store_document(
    data: DocumentRequest,
    auth: dict = Depends(authorize_request)  # 🔥 Intercepts header credential state
):
    """
    Handles immediate insertion of brief documents, snippets, or metadata adjustments.
    Executes synchronously within the request lifecycle for instant validation feedback.
    """
    if auth["tenant_id"] != data.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: The provided API credential token is not authorized to modify this tenant workspace."
        )

    document_id = str(uuid.uuid4())

    add_document(
        tenant_id=data.tenant_id,
        document_id=document_id,
        text=data.text,
        metadata={
            "source": data.source,
            "environment": data.environment,
            "severity": data.severity,
            "service": data.service,
            "document_id": document_id,
            "chunk_index": 0
        }
    )

    return {
        "message": "Document stored successfully",
        "tenant_id": data.tenant_id,
        "document_id": document_id
    }


# =====================================================================
# 2. LARGE DOCUMENT INGESTION ROUTE (ASYNCHRONOUS / DISTRIBUTED WORKER)
# =====================================================================
@router.post("/documents/large", status_code=status.HTTP_202_ACCEPTED)
def store_large_document(
    data: LargeDocumentRequest,
    auth: dict = Depends(authorize_request)  # 🔥 Intercepts header credential state
):
    """
    Handles massive system logs, dumps, or document uploads.
    Offloads execution instantly to Celery via Redis to prevent FastAPI thread starvation 
    and shield ChromaDB from concurrent multi-container write conflicts.
    """
    if auth["tenant_id"] != data.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: The provided API credential token is not authorized to modify this tenant workspace."
        )

    # Package metadata parameters to pass cleanly through the Celery serializer
    metadata_payload = {
        "source": data.source,
        "environment": data.environment,
        "severity": data.severity,
        "service": data.service
    }

    # 🔥 Dispatch processing to the Celery broker via .delay()
    task = process_document_ingestion.delay(
        tenant_id=data.tenant_id,
        text=data.text,
        metadata=metadata_payload
    )

    return {
        "message": "Large document accepted and queued for asynchronous background processing.",
        "tenant_id": data.tenant_id,
        "task_id": task.id,
        "status": "Accepted"
    }


# =====================================================================
# 3. STANDALONE SEMANTIC SEARCH ROUTE (TENANT-ISOLATED & PROTECTED)
# =====================================================================
@router.post("/search", status_code=status.HTTP_200_OK)
def semantic_search(
    data: SearchRequest,
    auth: dict = Depends(authorize_request)  # 🔥 Intercepts header credential state
):
    """
    Performs isolated real-time semantic query routing.
    Limits collection operations strictly to the workspace bound to the tenant payload.
    """
    if auth["tenant_id"] != data.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: The provided API credential token is not authorized to access this tenant workspace."
        )

    filters = {
        "environment": data.environment,
        "severity": data.severity,
        "source": data.source,
        "service": data.service
    }

    results = search_documents(
        tenant_id=data.tenant_id,
        query=data.query,
        filters=filters
    )

    return {
        "query": data.query,
        "tenant_id": data.tenant_id,
        "filters": filters,
        "results": results
    }


# =====================================================================
# 4. BINARY ENTERPRISE FILE UPLOAD ROUTE (SECURED, MULTIPART FORM DATA)
# =====================================================================
@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    tenant_id: str = Form(...),              # 🔥 Explicitly marked as Form data 
    file: UploadFile = File(...),            # Handles incoming binary file stream
    auth: dict = Depends(authorize_request),  # 🔥 Enforces platform key verification
    db: Session = Depends(get_db)            # 🔌 Injects relational transactional lifecycle context
):
    """
    Accepts raw enterprise documents (PDF/DOCX) via multipart/form-data payload,
    safely verifies the tenant authorization token, updates the SQL system-of-record state,
    writes the temporary payload to disk, and forwards background extraction logic straight 
    to our async worker queue.
    """
    if auth["tenant_id"] != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: The provided API credential token is not authorized to modify this tenant workspace."
        )

    try:
        document = create_document(
            db=db,
            tenant_id=tenant_id,
            filename=file.filename
        )
    except Exception as e:
        logger.error(f"[API ERROR] Failed creating database registry snapshot row: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register tracking context within system database."
        )

    extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
    except Exception as e:
        logger.error(f"[API ERROR] Failed writing uploaded artifact to storage volume: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to write file to disk storage: {str(e)}"
        )

    task = process_uploaded_file.delay(
        tenant_id=tenant_id,
        document_id=str(document.id),
        file_path=file_path,
        metadata={
            "original_filename": file.filename
        }
    )

    return {
        "message": "File uploaded successfully and verification processing initiated.",
        "tenant_id": tenant_id,
        "task_id": task.id,
        "document_id": str(document.id)
    }


# =====================================================================
# 5. ASYNCHRONOUS TASK TELEMETRY ROUTE (STATUS TRACKING)
# =====================================================================
@router.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def get_task_status(task_id: str):
    """
    Queries the Redis result backend to fetch live task execution telemetry.
    Enables frontend UI polling loops to monitor document chunking progress.
    """
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        result_payload = None
        if task_result.status == "SUCCESS":
            result_payload = task_result.result
        elif task_result.status == "FAILURE":
            result_payload = str(task_result.result)

        return {
            "task_id": task_id,
            "status": task_result.status,          # PENDING, STARTED, SUCCESS, FAILURE
            "result": result_payload,               # Returns metadata output dictionary or error stack
            "traceback": task_result.traceback if task_result.status == "FAILURE" else None
        }
        
    except Exception as e:
        logger.error(f"[API ERROR] Failed retrieving telemetry status for task {task_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal status tracking layer failed: {str(e)}"
        )


# =====================================================================
# 6. GET ALL DOCUMENTS ROUTE (TENANT-ISOLATED & SORTED REGISTRY)
# =====================================================================
@router.get("/documents", status_code=status.HTTP_200_OK)
def list_documents(
    tenant_id: str,                          # Passed cleanly as a query parameter (?tenant_id=...)
    auth: dict = Depends(authorize_request),  # 🔥 Validates API access keys
    db: Session = Depends(get_db)            # 🔌 Grabs a live PostgreSQL socket session
):
    """
    Retrieves the complete historical list of uploaded files, ingestion states, 
    and chunk breakdown stats belonging to the validated tenant workspace.
    """
    if auth["tenant_id"] != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: The provided API credential token is not authorized to view this tenant workspace."
        )

    documents = get_documents(
        db=db,
        tenant_id=tenant_id
    )

    return documents


# =====================================================================
# 7. DELETE DOCUMENT ROUTE (CASCADING RELATIONAL & VECTOR PURGE ENGINE)
# =====================================================================
@router.delete("/documents/{document_id}", status_code=status.HTTP_200_OK)
def remove_document(
    document_id: str,
    auth: dict = Depends(authorize_request),
    db: Session = Depends(get_db)
):
    """
    Performs validation checking on target records, wipes all matching chunk vector spaces 
    inside ChromaDB, drops the relational row inside PostgreSQL, and cleanly reports completion.
    """
    document = db.query(Document).filter(Document.id == document_id).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target document record not found in system database registry."
        )

    if document.tenant_id != auth["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Unprivileged access request to protected multi-tenant data asset blocks."
        )

    try:
        delete_document_chunks(
            tenant_id=document.tenant_id,
            document_id=document_id
        )
    except Exception as vector_err:
        logger.error(f"[CRITICAL API ERROR] Failed to drop vectors from ChromaDB: {str(vector_err)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanly remove document segments from vector database indexing collections."
        )

    delete_document(db=db, document_id=document_id)

    return {
        "message": "Document record and related vector index mappings evicted successfully.",
        "document_id": document_id,
        "tenant_id": document.tenant_id
    }


# =====================================================================
# 8. DOCUMENT OBSERVABILITY ROUTE (RELATIONAL METRICS + RAW CHROMA CHUNKS)
# =====================================================================
@router.get("/documents/{document_id}", status_code=status.HTTP_200_OK)
def get_document_details(
    document_id: str,
    auth: dict = Depends(authorize_request),
    db: Session = Depends(get_db)
):
    """
    Observability Endpoint: Aggregates relational system-of-record metrics 
    with unstructured raw text vector fragments for audit verification.
    """
    document = get_document_by_id(db, document_id=document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested document file could not be found in the system inventory registry."
        )

    if document.tenant_id != auth["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: The active security signature token cannot access this isolated workspace entity."
        )

    chunks = get_document_chunks(
        tenant_id=document.tenant_id,
        document_id=document_id
    )

    return {
        "document": {
            "id": str(document.id),
            "tenant_id": document.tenant_id,
            "filename": document.filename,
            "status": document.status,
            "chunks_created": document.chunks_created,
            "created_at": document.created_at
        },
        "chunks": chunks
    }