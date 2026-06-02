# app/services/document_service.py
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.document import Document

def create_document(
    db: Session,
    tenant_id: str,
    filename: str
) -> Document:
    """
    Initializes a new tracking record for an uploaded document.
    Defaults state to 'PROCESSING' while background jobs handle embedding parsing.
    """
    document = Document(
        tenant_id=tenant_id,
        filename=filename,
        status="PROCESSING"
    )

    db.add(document)
    db.commit()
    db.refresh(document)  # Pulls the newly generated UUID and created_at timestamp from Postgres

    return document


def update_document_status(
    db: Session,
    document_id: UUID,
    status: str,
    chunks_created: int = 0
) -> Document | None:
    """
    Updates the lifecycle status and total text fragment breakdown
    once a file parsing worker finishes execution.
    """
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        return None

    document.status = status
    document.chunks_created = chunks_created

    db.commit()
    db.refresh(document)

    return document


def get_documents(
    db: Session,
    tenant_id: str
) -> list[Document]:
    """
    Retrieves all records belonging to a specific tenant boundary,
    sorted with the newest additions arriving first.
    """
    return (
        db.query(Document)
        .filter(Document.tenant_id == tenant_id)
        .order_by(Document.created_at.desc())
        .all()
    )


# =====================================================================
# ADDED: POSTGRESQL RECORD RECORD DELETION
# =====================================================================
def delete_document(db: Session, document_id: str) -> Document | None:
    """
    Removes the document index metadata row permanently from Postgres.
    """
    document = (
        db.query(Document)
        .filter(Document.id == document_id)
        .first()
    )

    if not document:
        return None

    db.delete(document)
    db.commit()
    return document