"""
Pydantic schemas for document-related API responses.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.document import ProcessingStatus


class DocumentUploadResponse(BaseModel):
    """Returned immediately (HTTP 202) after a file is accepted for ingestion."""

    document_id: uuid.UUID
    task_id: str
    filename: str
    file_size: int
    status: ProcessingStatus
    message: str

    model_config = {"from_attributes": True}


class DocumentStatusResponse(BaseModel):
    """Returned by the status-polling endpoint (Day 24)."""

    document_id: uuid.UUID
    filename: str
    file_ext: str
    file_size: Optional[int] = None
    status: ProcessingStatus
    task_id: Optional[str] = None
    num_chunks: Optional[int] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DocumentListItem(BaseModel):
    """A single row in the document list response."""

    document_id: uuid.UUID
    filename: str
    file_ext: str
    file_size: Optional[int] = None
    status: ProcessingStatus
    num_chunks: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
