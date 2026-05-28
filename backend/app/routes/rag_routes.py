from fastapi import APIRouter

from app.models.request_models import (
    RagQueryRequest
)

from app.services.rag_service import (
    run_rag_pipeline
)

router = APIRouter()


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

    result = run_rag_pipeline(
        query=data.query,
        filters=filters
    )

    return result