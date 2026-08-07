import base64
import uuid
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_current_organization
from app.models.user import User
from app.models.organization import Organization
from app.models.document import Document, ProcessingStatus
from app.worker.tasks import ingest_document
from app.schemas.document import DocumentUploadResponse, DocumentListItem, DocumentStatusResponse

router = APIRouter()

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED, response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    current_org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """
    Accept a document upload, persist a DB record, and dispatch
    the ingestion work to a Celery background task.

    Returns 202 Accepted immediately with the document_id so the
    caller can poll /documents/{doc_id}/status for completion.
    """
    # ── 1. Validate file extension ──────────────────────────────────────────
    allowed_extensions = ["pdf", "txt", "docx"]
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension not allowed. Allowed types: {', '.join(allowed_extensions)}",
        )

    # ── 2. Read raw bytes ───────────────────────────────────────────────────
    content: bytes = await file.read()

    # ── 3. Register document row in DB (status = PENDING) ──────────────────
    doc = Document(
        file_name=file.filename,
        file_ext=file_ext,
        file_size=len(content),
        status=ProcessingStatus.PENDING,
        user_id=current_user.id,
        organization_id=current_org.id,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    # ── 4. Dispatch Celery task (non-blocking) ──────────────────────────────
    file_content_b64 = base64.b64encode(content).decode("utf-8")
    task = ingest_document.delay(
        file_content_b64=file_content_b64,
        file_ext=file_ext,
        file_name=file.filename,
        organization_id=str(current_org.id),
        document_id=str(doc.id),
    )

    # ── 5. Store the Celery task ID for status lookups ──────────────────────
    doc.task_id = task.id
    await db.commit()

    return {
        "document_id": str(doc.id),
        "task_id": task.id,
        "filename": file.filename,
        "file_size": len(content),
        "status": ProcessingStatus.PENDING,
        "message": "Document accepted. Ingestion running in background.",
    }


@router.get("/", response_model=List[DocumentListItem])
async def list_documents(
    current_user: User = Depends(get_current_active_user),
    current_org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """
    Return all documents belonging to the current organisation,
    ordered from newest to oldest.
    """
    result = await db.execute(
        select(Document)
        .where(Document.organization_id == current_org.id)
        .order_by(Document.created_at.desc())
    )
    docs = result.scalars().all()

    return [
        DocumentListItem(
            document_id=doc.id,
            filename=doc.file_name,
            file_ext=doc.file_ext,
            file_size=doc.file_size,
            status=doc.status,
            num_chunks=doc.num_chunks,
            created_at=doc.created_at,
        )
        for doc in docs
    ]


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    current_org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a document record by ID.

    Only documents belonging to the current organisation can be deleted
    (multi-tenant isolation enforced).
    """
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.organization_id == current_org.id,
        )
    )
    doc = result.scalar_one_or_none()

    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied.",
        )

    await db.delete(doc)
    await db.commit()


@router.get("/{doc_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    doc_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    current_org: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
):
    """
    Check the current processing status of an uploaded document.
    """
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.organization_id == current_org.id,
        )
    )
    doc = result.scalar_one_or_none()
