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

from fastapi import APIRouter, BackgroundTasks

from app.models.request_models import (
    RagQueryRequest
)
from app.services.rag_service import (
    run_rag_pipeline,
    run_streaming_rag_pipeline
)
from app.services.ai_service import client

router = APIRouter()


# =====================================================================
# REAL-TIME STREAMING RAG ROUTE (TENANT-AWARE)
# =====================================================================
@router.post("/rag/stream")
def rag_query_stream(data: RagQueryRequest, background_tasks: BackgroundTasks): 
    filters = {
        "environment": data.environment,
        "severity": data.severity,
        "source": data.source,
        "service": data.service
    }

    result = run_streaming_rag_pipeline(
        client=client,
        tenant_id=data.tenant_id,          # 🔥 Extract and map tenant id
        session_id=data.session_id,
        query=data.query,
        background_tasks=background_tasks, 
        filters=filters
    )

    return result


# =====================================================================
# SYNC BACKUP PIPELINE (TENANT-AWARE & CLEANED)
# =====================================================================
@router.post("/rag")
def rag_query(data: RagQueryRequest):
    filters = {
        "environment": data.environment,
        "severity": data.severity,
        "source": data.source,
        "service": data.service
    }

    # 🔥 Fixed: Removed the unintentional streaming pipeline duplicate execution here
    result = run_rag_pipeline(
        tenant_id=data.tenant_id,          # 🔥 Extract and map tenant id
        session_id=data.session_id,
        query=data.query,
        filters=filters
    )

    return result