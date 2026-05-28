from typing import Optional

from pydantic import BaseModel


class DocumentRequest(BaseModel):

    text: str

    source: str = "unknown"

    environment: str = "development"

    severity: str = "info"

    service: str = "general"


class LargeDocumentRequest(BaseModel):

    text: str

    source: str = "unknown"

    environment: str = "development"

    severity: str = "info"

    service: str = "general"


class SearchRequest(BaseModel):

    query: str

    environment: Optional[str] = None

    severity: Optional[str] = None

    source: Optional[str] = None

    service: Optional[str] = None


class RagQueryRequest(BaseModel):

    session_id: str

    query: str

    environment: Optional[str] = None

    severity: Optional[str] = None

    source: Optional[str] = None

    service: Optional[str] = None