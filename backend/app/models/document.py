# app/models/document.py
import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database.base import Base

class Document(Base):
    """
    The Relational Database Blueprint for Tracking Document Ingestion Pipelines.
    This table stores metadata about uploaded documents, their multi-tenant owners,
    and their parsing processing states.
    """
    __tablename__ = "documents"

    # 🔑 Unique Identifier Fingerprint
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # 🏢 Multi-Tenant Separation Layer
    tenant_id = Column(
        String,
        nullable=False
    )

    # 📂 Metadata Details
    filename = Column(
        String,
        nullable=False
    )

    # ⚙️ Lifecycle Status Indicator (e.g., "PENDING", "PROCESSING", "COMPLETED", "FAILED")
    status = Column(
        String,
        nullable=False
    )

    # 🔢 Document Chunk Split Counter
    chunks_created = Column(
        Integer,
        default=0
    )

    # ⏰ Server-Side Generation Timestamp Matrix
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )