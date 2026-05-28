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

    result = run_rag_pipeline(
        query=data.query
    )

    return result