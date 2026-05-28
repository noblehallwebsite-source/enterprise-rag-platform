from pydantic import BaseModel


class DocumentRequest(BaseModel):
    text: str
    source: str = "unknown"


class SearchRequest(BaseModel):
    query: str


class RagQueryRequest(BaseModel):
    query: str


class LargeDocumentRequest(BaseModel):
    text: str
    source: str = "unknown"