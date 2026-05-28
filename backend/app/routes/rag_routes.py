from fastapi import APIRouter

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
# REAL-TIME STREAMING RAG ROUTE
# =====================================================================
@router.post("/rag/stream")  # 🔥 FIX 2: Explicitly named path for clarity
def rag_query_stream(
    data: RagQueryRequest
):

    filters = {
        "environment": data.environment,
        "severity": data.severity,
        "source": data.source,
        "service": data.service
    }

    # Execute and return your text/plain chunk stream generator
    result = run_streaming_rag_pipeline(
        client=client,
        session_id=data.session_id,
        query=data.query,
        filters=filters
    )

    return result


# =====================================================================
# OPTIONAL: KEEP THE BLOCKING BACKUP ALIVE
# =====================================================================
@router.post("/rag")
def rag_query(
    data: RagQueryRequest
):

    filters = {
        "environment": data.environment,
        "severity": data.severity,
        "source": data.source,
        "service": data.service
    }

    # result = run_rag_pipeline(
    #     session_id=data.session_id,
    #     query=data.query,
    #     filters=filters
    # )

    result = run_streaming_rag_pipeline(
        client=client,
        session_id=data.session_id,
        query=data.query,
        filters=filters
    )

    return result