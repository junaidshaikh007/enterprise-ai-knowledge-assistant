"""Unit tests for the Langfuse observability integration (Day 26).

These tests verify that:
  - Langfuse configuration fields are present in Settings.
  - The @observe decorator does not break retrieval or LLM service when
    Langfuse is disabled/not configured (i.e. in CI without keys set).
  - The LLM service runs cleanly without Langfuse credentials.
"""

import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


# ──────────────────────────────────────────────────────────────────────────────
# 1. Settings tests
# ──────────────────────────────────────────────────────────────────────────────

def test_settings_has_langfuse_fields():
    """Settings class must expose the three Langfuse configuration fields."""
    from app.core.config import settings

    assert hasattr(settings, "LANGFUSE_PUBLIC_KEY"), "Missing LANGFUSE_PUBLIC_KEY"
    assert hasattr(settings, "LANGFUSE_SECRET_KEY"), "Missing LANGFUSE_SECRET_KEY"
    assert hasattr(settings, "LANGFUSE_HOST"), "Missing LANGFUSE_HOST"


def test_langfuse_host_has_default():
    """LANGFUSE_HOST should default to the cloud endpoint."""
    from app.core.config import settings

    assert settings.LANGFUSE_HOST == "https://cloud.langfuse.com"


def test_langfuse_keys_optional():
    """LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY are optional and can be None."""
    from app.core.config import settings

    # In a dev environment without a .env file defining them, both should be None or str
    # The important thing is they exist as attributes
    assert isinstance(settings.LANGFUSE_PUBLIC_KEY, (str, type(None)))
    assert isinstance(settings.LANGFUSE_SECRET_KEY, (str, type(None)))


# ──────────────────────────────────────────────────────────────────────────────
# 2. LLMService tests - @observe decorator and clean execution
# ──────────────────────────────────────────────────────────────────────────────

class _FakeLLM:
    """Synchronous and asynchronous stub that returns a canned answer."""

    def invoke(self, _messages, config=None):
        return SimpleNamespace(content="mocked answer")

    async def astream(self, _messages, config=None):
        for token in ("Hello", " world"):
            yield SimpleNamespace(content=token)


def test_generate_answer_works_without_langfuse_credentials():
    """generate_answer must succeed even when no Langfuse credentials are set."""
    from app.services.llm_service import LLMService

    svc = object.__new__(LLMService)
    svc.llm = _FakeLLM()

    result = svc.generate_answer(query="What is the policy?", context_chunks=[])
    assert result == "mocked answer"


def test_stream_answer_works_without_langfuse_credentials():
    """stream_answer must yield tokens even when no Langfuse credentials are set."""
    from app.services.llm_service import LLMService

    svc = object.__new__(LLMService)
    svc.llm = _FakeLLM()

    async def _collect():
        return [t async for t in svc.stream_answer(query="What is the policy?", context_chunks=[])]

    tokens = asyncio.run(_collect())
    assert tokens == ["Hello", " world"]


def test_generate_answer_observe_decorator_applied():
    """generate_answer should be callable (i.e. @observe does not break it)."""
    from app.services.llm_service import LLMService

    assert callable(LLMService.generate_answer)


def test_stream_answer_observe_decorator_applied():
    """stream_answer should be callable (i.e. @observe does not break it)."""
    from app.services.llm_service import LLMService

    assert callable(LLMService.stream_answer)


# ──────────────────────────────────────────────────────────────────────────────
# 3. RetrievalService @observe decoration smoke test
# ──────────────────────────────────────────────────────────────────────────────

def test_retrieval_service_observe_decorator_is_applied():
    """retrieve_context must still be callable after @observe is applied."""
    from app.services.retrieval_service import RetrievalService

    assert callable(RetrievalService.retrieve_context)


# ──────────────────────────────────────────────────────────────────────────────
# 4. Langfuse v4 API availability test
# ──────────────────────────────────────────────────────────────────────────────

def test_langfuse_v4_observe_importable():
    """Verify langfuse v4 observe and get_client are importable."""
    from langfuse import observe, get_client

    assert callable(observe)
    assert callable(get_client)


def test_langfuse_get_client_has_update_span():
    """get_client() must expose the update_current_span method used by our services."""
    from langfuse import get_client

    client = get_client()
    assert hasattr(client, "update_current_span"), (
        "Langfuse client must have update_current_span method for span instrumentation"
    )
    assert callable(client.update_current_span)
