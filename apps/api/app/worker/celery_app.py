"""
Celery application instance and worker configuration.

Broker  : Redis  (REDIS_URL env var, default redis://localhost:6379/0)
Backend : Redis  (same URL, database 0)
"""
from celery import Celery
from app.core.config import settings

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_celery_app() -> Celery:
    """Create and configure the Celery application."""
    app = Celery(
        "knowledge_assistant",
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_RESULT_BACKEND,
    )


    app.conf.update(
        # ── Serialisation ──────────────────────────────────────────────────
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",

        # ── Timezone ───────────────────────────────────────────────────────
        timezone="UTC",
        enable_utc=True,

        # ── Task behaviour ─────────────────────────────────────────────────
        # Acknowledge the task only after it completes (safer re-delivery on crash)
        task_acks_late=True,
        # Do not prefetch more than one task per worker process
        worker_prefetch_multiplier=1,

        # ── Result TTL ─────────────────────────────────────────────────────
        # Keep task results in Redis for 24 hours, then expire
        result_expires=60 * 60 * 24,

        # ── Retry policy ───────────────────────────────────────────────────
        task_max_retries=3,
        task_default_retry_delay=10,  # seconds

        # ── Routing ────────────────────────────────────────────────────────
        task_default_queue="default",
        task_queues={
            "default": {},
            "ingestion": {},   # dedicated queue for heavy document processing
        },
    )

    return app


# Module-level singleton consumed by workers and importers
celery_app: Celery = create_celery_app()
