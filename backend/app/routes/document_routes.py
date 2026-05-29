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

from fastapi import APIRouter, Depends, HTTPException, status

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

# 🔥 Import authorization gateway layer
from app.services.security_service import (
    authorize_request
)

router = APIRouter()


# =====================================================================
# STANDARD DOCUMENT INGESTION ROUTE (TENANT-ISOLATED & PROTECTED)
# =====================================================================
@router.post("/documents")
def store_document(
    data: DocumentRequest,
    auth: dict = Depends(authorize_request)  # 🔥 Intercepts header credential state
):
    # 🔥 STEP 7 CROSS-CHECK: Deny spoofing payloads immediately
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
            "service": data.service
        }
    )

    return {
        "message": "Document stored successfully",
        "tenant_id": data.tenant_id,
        "document_id": document_id
    }


# =====================================================================
# LARGE DOCUMENT INGESTION ROUTE (TENANT-ISOLATED & PROTECTED)
# =====================================================================
@router.post("/documents/large")
def store_large_document(
    data: LargeDocumentRequest,
    auth: dict = Depends(authorize_request)  # 🔥 Intercepts header credential state
):
    # 🔥 STEP 7 CROSS-CHECK: Deny spoofing payloads immediately
    if auth["tenant_id"] != data.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: The provided API credential token is not authorized to modify this tenant workspace."
        )

    chunks = chunk_text(data.text)

    for chunk in chunks:
        chunk_id = str(uuid.uuid4())

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
# STANDALONE SEMANTIC SEARCH ROUTE (TENANT-ISOLATED & PROTECTED)
# =====================================================================
@router.post("/search")
def semantic_search(
    data: SearchRequest,
    auth: dict = Depends(authorize_request)  # 🔥 Intercepts header credential state
):
    # 🔥 STEP 7 CROSS-CHECK: Deny spoofing payloads immediately
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