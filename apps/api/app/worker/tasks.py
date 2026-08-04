"""
Background tasks for the Knowledge Assistant worker.

Tasks
-----
ingest_document  — parse, chunk, and embed a single uploaded document.
"""
import base64
import logging
from typing import Any, Dict

from celery import Task

from app.worker.celery_app import celery_app
from app.utils.document_parser import document_parser
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Base task class with shared error hook
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Document ingestion task
# ---------------------------------------------------------------------------

@celery_app.task(
    bind=True,
    base=_BaseTask,
    name="worker.tasks.ingest_document",
    queue="ingestion",
    max_retries=3,
    default_retry_delay=15,  # seconds between retries
    acks_late=True,
)
def ingest_document(
    self: Task,
    file_content_b64: str,
    file_ext: str,
    file_name: str,
    organization_id: int,
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
    organization_id : int
        Tenant ID used for multi-tenant payload filtering in the vector store.

    Returns
    -------
    dict
        ``{"status": "success", "file_name": ..., "num_chunks": ..., "organization_id": ...}``

    Raises
    ------
    Retries the task (up to ``max_retries``) on any exception before raising.
    """
    logger.info(
        "ingest_document started | file=%s ext=%s org=%s task_id=%s",
        file_name,
        file_ext,
        organization_id,
        self.request.id,
    )

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
            return {
                "status": "success",
                "file_name": file_name,
                "num_chunks": 0,
                "organization_id": organization_id,
                "warning": "Document contained no extractable text.",
            }

        # ── Step 3: Embed & store in Qdrant ───────────────────────────────
        success = embedding_service.embed_and_store_chunks(
            chunks=chunk_texts,
            organization_id=organization_id,
            file_name=file_name,
        )

        if not success:
            raise RuntimeError(
                f"embed_and_store_chunks returned False for file={file_name}"
            )

        logger.info(
            "ingest_document finished | file=%s chunks=%d org=%s",
            file_name,
            len(chunk_texts),
            organization_id,
        )
        return {
            "status": "success",
            "file_name": file_name,
            "num_chunks": len(chunk_texts),
            "organization_id": organization_id,
        }

    except Exception as exc:
        logger.warning(
            "ingest_document failed (attempt %d/%d) | file=%s error=%s",
            self.request.retries + 1,
            self.max_retries + 1,
            file_name,
            exc,
        )
        # Exponential back-off: 15s, 30s, 60s
        raise self.retry(
            exc=exc,
            countdown=self.default_retry_delay * (2 ** self.request.retries),
        )
