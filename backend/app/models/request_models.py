# from typing import Optional

# from pydantic import BaseModel


# class DocumentRequest(BaseModel):

#     text: str

#     source: str = "unknown"

#     environment: str = "development"

#     severity: str = "info"

#     service: str = "general"


# class LargeDocumentRequest(BaseModel):

#     text: str

#     source: str = "unknown"

#     environment: str = "development"

#     severity: str = "info"

#     service: str = "general"


# class SearchRequest(BaseModel):

#     query: str

#     environment: Optional[str] = None

#     severity: Optional[str] = None

#     source: Optional[str] = None

#     service: Optional[str] = None


# class RagQueryRequest(BaseModel):

#     session_id: str

#     query: str

#     environment: Optional[str] = None

#     severity: Optional[str] = None

#     source: Optional[str] = None

#     service: Optional[str] = None

from typing import Optional
from pydantic import BaseModel, Field

# =====================================================================
# ENTERPRISE TENANT-AWARE REQUEST MODELS
# =====================================================================

class DocumentRequest(BaseModel):
    tenant_id: str = Field(..., description="Unique enterprise tenant identifier for collection routing")
    text: str
    source: str = "unknown"
    environment: str = "development"
    severity: str = "info"
    service: str = "general"


class LargeDocumentRequest(BaseModel):
    tenant_id: str = Field(..., description="Unique enterprise tenant identifier for collection routing")
    text: str
    source: str = "unknown"
    environment: str = "development"
    severity: str = "info"
    service: str = "general"


class SearchRequest(BaseModel):
    tenant_id: str = Field(..., description="Unique enterprise tenant identifier for isolated context retrieval")
    query: str
    environment: Optional[str] = None
    severity: Optional[str] = None
    source: Optional[str] = None
    service: Optional[str] = None


class RagQueryRequest(BaseModel):
    tenant_id: str = Field(..., description="Unique enterprise tenant identifier for context & history isolation")
    session_id: str
    query: str
    environment: Optional[str] = None
    severity: Optional[str] = None
    source: Optional[str] = None
    service: Optional[str] = None