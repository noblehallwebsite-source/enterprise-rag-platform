# from fastapi import APIRouter, BackgroundTasks

# from app.models.request_models import (
#     RagQueryRequest
# )

# from app.services.rag_service import (
#     run_rag_pipeline,
#     run_streaming_rag_pipeline
# )

# from app.services.ai_service import client

# router = APIRouter()


# # =====================================================================
# # REAL-TIME STREAMING RAG ROUTE
# # =====================================================================
# @router.post("/rag/stream")
# def rag_query_stream(data: RagQueryRequest, background_tasks: BackgroundTasks):  # 🔥 Inject here
#     filters = {
#         "environment": data.environment,
#         "severity": data.severity,
#         "source": data.source,
#         "service": data.service
#     }

#     result = run_streaming_rag_pipeline(
#         client=client,
#         session_id=data.session_id,
#         query=data.query,
#         background_tasks=background_tasks,  # 🔥 Pass down here
#         filters=filters
#     )

#     return result


# # =====================================================================
# # OPTIONAL: KEEP THE BLOCKING BACKUP ALIVE
# # =====================================================================
# @router.post("/rag")
# def rag_query(
#     data: RagQueryRequest
# ):

#     filters = {
#         "environment": data.environment,
#         "severity": data.severity,
#         "source": data.source,
#         "service": data.service
#     }

#     result = run_rag_pipeline(
#         session_id=data.session_id,
#         query=data.query,
#         filters=filters
#     )

#     result = run_streaming_rag_pipeline(
#         client=client,
#         session_id=data.session_id,
#         query=data.query,
#         filters=filters
#     )

#     return result






from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.request_models import RagQueryRequest
from app.services.rag_service import (
    run_rag_pipeline,
    run_streaming_rag_pipeline
)
from app.services.security_service import authorize_request
from app.services.ai_service import client
from app.database.dependencies import get_db

router = APIRouter()

# =====================================================================
# REAL-TIME STREAMING RAG ROUTE (WITH CROSS-TENANT VERIFICATION)
# =====================================================================
@router.post("/rag/stream")
def rag_query_stream(
    data: RagQueryRequest, 
    background_tasks: BackgroundTasks,
    auth: dict = Depends(authorize_request),
    db: Session = Depends(get_db) 
): 
    # Enforce strict tenant security cross-check
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

    # Pass DB handle into the streaming executor for persistent history and memory
    return run_streaming_rag_pipeline(
        client=client,
        db=db, 
        tenant_id=data.tenant_id,  
        session_id=data.session_id,
        query=data.query,
        background_tasks=background_tasks, 
        filters=filters
    )


# =====================================================================
# SYNC BACKUP PIPELINE (WITH CROSS-TENANT VERIFICATION)
# =====================================================================
@router.post("/rag")
def rag_query(
    data: RagQueryRequest,
    auth: dict = Depends(authorize_request),
    db: Session = Depends(get_db) # 👈 FIXED: Injected DB dependency
):
    # Enforce strict tenant security cross-check
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

    # 🚀 FIXED: Passed db=db to allow the pipeline to persist messages and retrieve history
    result = run_rag_pipeline(
        db=db, 
        tenant_id=data.tenant_id,
        session_id=data.session_id,
        query=data.query,
        filters=filters
    )

    return result