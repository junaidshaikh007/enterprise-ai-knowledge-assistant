import uuid
import enum
from sqlalchemy import Column, String, DateTime, ForeignKey, func, Enum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class ProcessingStatus(str, enum.Enum):
    """Lifecycle states for an uploaded document."""
    PENDING    = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS    = "SUCCESS"
    FAILED     = "FAILED"


class Document(Base):
    """
    Represents a document uploaded by a user within an organisation.

    The `status` column tracks progress through the asynchronous Celery
    ingestion pipeline so the frontend can poll for completion.
    """
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # ── Basic metadata ──────────────────────────────────────────────────────
    file_name    = Column(String, nullable=False)
    file_ext     = Column(String(10), nullable=False)
    file_size    = Column(Integer, nullable=True)   # bytes
    num_chunks   = Column(Integer, nullable=True)   # populated after ingestion

    # ── Processing state ────────────────────────────────────────────────────
    status = Column(
        Enum(ProcessingStatus, name="processingstatus"),
        nullable=False,
        default=ProcessingStatus.PENDING,
        server_default=ProcessingStatus.PENDING.value,
    )
    # Optional: surface a human-readable error reason on failure
    error_message = Column(String, nullable=True)

    # ── Celery task reference ───────────────────────────────────────────────
    task_id = Column(String, nullable=True)         # Celery task UUID

    # ── Tenant relations ────────────────────────────────────────────────────
    user_id         = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)

    # ── Timestamps ──────────────────────────────────────────────────────────
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    # ── Relationships ───────────────────────────────────────────────────────
    user         = relationship("User",         backref="documents")
    organization = relationship("Organization", backref="documents")
