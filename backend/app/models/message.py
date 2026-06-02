import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database.base import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "chat_sessions.id",
            ondelete="CASCADE"  # Automatically purges messages if a thread is deleted
        ),
        nullable=False,
        index=True
    )
    role = Column(
        String,  # "user" or "assistant"
        nullable=False
    )
    content = Column(
        Text,
        nullable=False
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )