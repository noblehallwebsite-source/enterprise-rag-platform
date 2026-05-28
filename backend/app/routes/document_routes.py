import uuid

from fastapi import APIRouter

from app.models.request_models import (
    DocumentRequest,
    LargeDocumentRequest,
    SearchRequest
)

from app.services.chroma_service import (
    add_document,
    search_documents
)

from app.services.chunking_service import (
    chunk_text
)

router = APIRouter()


@router.post("/documents")
def store_document(
    data: DocumentRequest
):

    document_id = str(uuid.uuid4())

    add_document(
        document_id=document_id,
        text=data.text,
        metadata={
            "source": data.source,
            "environment": data.environment,
            "severity": data.severity,
            "service": data.service
        }
    )

    return {
        "message": "Document stored successfully",
        "document_id": document_id
    }


@router.post("/documents/large")
def store_large_document(
    data: LargeDocumentRequest
):

    chunks = chunk_text(data.text)

    for chunk in chunks:

        chunk_id = str(uuid.uuid4())

        add_document(
            document_id=chunk_id,
            text=chunk,
            metadata={
                "source": data.source,
                "environment": data.environment,
                "severity": data.severity,
                "service": data.service
            }
        )

    return {
        "message": "Large document stored",
        "chunks_created": len(chunks)
    }


@router.post("/search")
def semantic_search(
    data: SearchRequest
):

    filters = {
        "environment": data.environment,
        "severity": data.severity,
        "source": data.source,
        "service": data.service
    }

    results = search_documents(
        query=data.query,
        filters=filters
    )

    return {
        "query": data.query,
        "filters": filters,
        "results": results
    }