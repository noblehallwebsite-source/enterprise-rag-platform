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


# =====================================================================
# STANDARD DOCUMENT INGESTION ROUTE (TENANT-ISOLATED)
# =====================================================================
@router.post("/documents")
def store_document(
    data: DocumentRequest
):
    document_id = str(uuid.uuid4())

    # 🔥 Pass tenant_id down to enforce isolation boundary
    add_document(
        tenant_id=data.tenant_id,
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
        "tenant_id": data.tenant_id,
        "document_id": document_id
    }


# =====================================================================
# LARGE DOCUMENT INGESTION ROUTE (TENANT-ISOLATED)
# =====================================================================
@router.post("/documents/large")
def store_large_document(
    data: LargeDocumentRequest
):
    # Using your native chunk_text service package
    chunks = chunk_text(data.text)

    for chunk in chunks:
        chunk_id = str(uuid.uuid4())

        # 🔥 Pass tenant_id down to route each split chunk into the correct collection
        add_document(
            tenant_id=data.tenant_id,
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
        "tenant_id": data.tenant_id,
        "chunks_created": len(chunks)
    }


# =====================================================================
# STANDALONE SEMANTIC SEARCH ROUTE (TENANT-ISOLATED)
# =====================================================================
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

    # 🔥 Pass tenant_id to make it mathematically impossible to read another client's vectors
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