"""
Background tasks for the Knowledge Assistant worker.

Tasks
-----
ingest_document  — parse, chunk, and embed a single uploaded document,
                   updating the Document.status field throughout.
"""
import base64
import logging
from typing import Any, Dict
from celery import Task

from app.utils.document_parser import document_parser
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


def _update_document_status(document_id: str, status: str, *, error_message: str | None = None, num_chunks: int | None = None) -> None:
    """Synchronously update the Document row's status inside worker context."""
    try:
        import uuid
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings
        import app.models.base  # Ensure all SQLAlchemy models are registered
        from app.models.document import Document

        sync_url = "sqlite:///./knowledge_assistant.db"
        try:
            if "postgresql+asyncpg://" in settings.DATABASE_URL:
                pg_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
                engine = create_engine(pg_url, pool_pre_ping=True)
                SessionLocal = sessionmaker(bind=engine)
                target_id = uuid.UUID(document_id) if isinstance(document_id, str) else document_id
                with SessionLocal() as session:
                    doc = session.get(Document, target_id)
                    if doc is not None:
                        doc.status = status
                        if error_message is not None:
                            doc.error_message = error_message
                        if num_chunks is not None:
                            doc.num_chunks = num_chunks
                        session.commit()
                        logger.debug("Document %s status -> %s", document_id, status)
                        return
        except Exception as pg_err:
            logger.info(f"PostgreSQL update skipped ({pg_err}). Falling back to local SQLite.")

        engine = create_engine(sync_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(bind=engine)
        target_id = uuid.UUID(document_id) if isinstance(document_id, str) else document_id
        with SessionLocal() as session:
            doc = session.get(Document, target_id)
            if doc is None:
                logger.warning("_update_document_status: Document %s not found in SQLite", document_id)
                return
            doc.status = status
            if error_message is not None:
                doc.error_message = error_message
            if num_chunks is not None:
                doc.num_chunks = num_chunks
            session.commit()
            logger.info("Document %s status -> %s (chunks: %s) in local SQLite", document_id, status, num_chunks)
    except Exception:
        logger.exception("Failed to update status for document %s", document_id)


class _BaseTask(Task):
    """Shared base that logs failures automatically."""

    abstract = True

    def on_failure(self, exc: Exception, task_id: str, args, kwargs, einfo) -> None:  # type: ignore[override]
        logger.error(
            "Task %s[%s] raised %s: %s",
            self.name,
            task_id,
            type(exc).__name__,
            exc,
            exc_info=einfo,
        )


try:
    from app.worker.celery_app import celery_app
    task_decorator = celery_app.task(
        bind=True,
        base=_BaseTask,
        name="worker.tasks.ingest_document",
        queue="ingestion",
        max_retries=3,
        default_retry_delay=15,
        acks_late=True,
    )
except Exception:
    def task_decorator(fn):
        return fn

@task_decorator
def ingest_document(
    self: Task,
    file_content_b64: str,
    file_ext: str,
    file_name: str,
    organization_id: str,
    document_id: str | None = None,
) -> Dict[str, Any]:
    """
    Background task: parse a document, split into chunks, embed and store in Qdrant.

    Parameters
    ----------
    file_content_b64 : str
        Base-64-encoded raw file bytes (JSON-safe for Celery serialisation).
    file_ext : str
        File extension without dot, e.g. ``"pdf"``, ``"docx"``, ``"txt"``.
    file_name : str
        Original filename — stored as metadata in Qdrant.
    organization_id : str
        Tenant ID used for multi-tenant payload filtering in the vector store.
    document_id : str | None
        Primary key of the ``documents`` row to update status on.
        When ``None`` the task runs without DB status tracking (backward compat).

    Returns
    -------
    dict
        ``{"status": "SUCCESS", "file_name": ..., "num_chunks": ..., "organization_id": ...}``

    Raises
    ------
    Retries the task (up to ``max_retries``) on any exception before raising.
    """
    task_id = getattr(getattr(self, "request", None), "id", "inline")
    logger.info(
        "ingest_document started | file=%s ext=%s org=%s doc_id=%s task_id=%s",
        file_name,
        file_ext,
        organization_id,
        document_id,
        task_id,
    )

    # ── Mark PROCESSING ────────────────────────────────────────────────────
    if document_id:
        _update_document_status(document_id, "PROCESSING")

    try:
        # ── Step 1: Decode file bytes ──────────────────────────────────────
        file_content: bytes = base64.b64decode(file_content_b64)
        logger.debug("Decoded %d bytes for %s", len(file_content), file_name)

        # ── Step 2: Parse & chunk ──────────────────────────────────────────
        # process_document returns [{"text": str, "chunk_index": int}, ...]
        chunk_dicts = document_parser.process_document(file_content, file_ext)
        chunk_texts: list[str] = [c["text"] for c in chunk_dicts]
        logger.info("Parsed %d chunks from %s", len(chunk_texts), file_name)

        if not chunk_texts:
            logger.warning("No chunks extracted from %s — skipping embedding.", file_name)
            if document_id:
                _update_document_status(
                    document_id, "SUCCESS",
                    num_chunks=0,
                    error_message="Document contained no extractable text.",
                )
            return {
                "status": "SUCCESS",
                "file_name": file_name,
                "num_chunks": 0,
                "organization_id": organization_id,
                "warning": "Document contained no extractable text.",
            }

        # ── Step 3: Embed & store in Qdrant ───────────────────────────────
        success = embedding_service.embed_and_store_chunks(
            chunks=chunk_texts,
            organization_id=str(organization_id),
            file_name=file_name,
        )

        if not success:
            raise RuntimeError(
                f"embed_and_store_chunks returned False for file={file_name}"
            )

        # ── Mark SUCCESS ───────────────────────────────────────────────────
        if document_id:
            _update_document_status(document_id, "SUCCESS", num_chunks=len(chunk_texts))

        logger.info(
            "ingest_document finished | file=%s chunks=%d org=%s",
            file_name,
            len(chunk_texts),
            organization_id,
        )
        return {
            "status": "SUCCESS",
            "file_name": file_name,
            "num_chunks": len(chunk_texts),
            "organization_id": organization_id,
        }

    except Exception as exc:
        retries = getattr(getattr(self, "request", None), "retries", 0)
        max_retries = getattr(self, "max_retries", 3)
        logger.warning(
            "ingest_document failed (attempt %d/%d) | file=%s error=%s",
            retries + 1,
            max_retries + 1,
            file_name,
            exc,
        )
        # On the final retry or inline run, mark the document as FAILED before raising
        is_final_retry = retries >= max_retries
        if document_id and is_final_retry:
            _update_document_status(document_id, "FAILED", error_message=str(exc))

        if hasattr(self, "retry") and getattr(self, "request", None) is not None:
            default_retry_delay = getattr(self, "default_retry_delay", 15)
            raise self.retry(
                exc=exc,
                countdown=default_retry_delay * (2 ** retries),
            )
        else:
            if document_id:
                _update_document_status(document_id, "FAILED", error_message=str(exc))
            raise exc

def ingest_document_inline(
    file_content_b64: str,
    file_ext: str,
    file_name: str,
    organization_id: str,
    document_id: str | None = None,
) -> Dict[str, Any]:
    """Convenience wrapper for inline execution when Celery is offline."""
    if hasattr(ingest_document, "run"):
        return ingest_document.run(
            file_content_b64=file_content_b64,
            file_ext=file_ext,
            file_name=file_name,
            organization_id=organization_id,
            document_id=document_id,
        )
    return ingest_document(
        file_content_b64=file_content_b64,
        file_ext=file_ext,
        file_name=file_name,
        organization_id=organization_id,
        document_id=document_id,
    )

