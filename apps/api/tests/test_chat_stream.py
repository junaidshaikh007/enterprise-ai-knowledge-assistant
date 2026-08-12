import asyncio
import json
import sys
import uuid
from enum import Enum
from types import SimpleNamespace


class _OpenAIStub:
    def __init__(self, **_kwargs):
        pass


class _QdrantClientStub:
    def __init__(self, **_kwargs):
        pass

    def get_collections(self):
        return SimpleNamespace(collections=[])

    def create_collection(self, **_kwargs):
        pass


class _DistanceStub(Enum):
    COSINE = "cosine"


class _ModelStub:
    def __init__(self, **_kwargs):
        pass


sys.modules.setdefault(
    "langchain_openai",
    SimpleNamespace(ChatOpenAI=_OpenAIStub, OpenAIEmbeddings=_OpenAIStub),
)
sys.modules.setdefault(
    "langchain_core.messages",
    SimpleNamespace(SystemMessage=_ModelStub, HumanMessage=_ModelStub),
)
sys.modules.setdefault("qdrant_client", SimpleNamespace(QdrantClient=_QdrantClientStub))
sys.modules.setdefault(
    "qdrant_client.http.models",
    SimpleNamespace(
        Distance=_DistanceStub,
        FieldCondition=_ModelStub,
        Filter=_ModelStub,
        MatchValue=_ModelStub,
        VectorParams=_ModelStub,
    ),
)

from app.api.v1 import chat as chat_module
from app.schemas.chat import ChatRequest
from fastapi import HTTPException


class RetrievalServiceStub:
    def retrieve_context(self, **_kwargs):
        return [{"score": 0.91, "text": "Policy details", "file_name": "policy.pdf"}]


class LLMServiceStub:
    async def stream_answer(self, **_kwargs):
        yield "Hello"
        yield " world"


async def collect_events(response):
    return [event async for event in response.body_iterator]


class QueryResultStub:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class DatabaseStub:
    def __init__(self, session):
        self.session = session

    async def execute(self, _statement):
        return QueryResultStub(self.session)


class LangfuseClientStub:
    def update_current_span(self, **_kwargs):
        pass


def test_chat_returns_sse_sources_tokens_and_completion(monkeypatch):
    monkeypatch.setattr(chat_module, "retrieval_service", RetrievalServiceStub())
    monkeypatch.setattr(chat_module, "llm_service", LLMServiceStub())
    monkeypatch.setattr(chat_module, "get_client", LangfuseClientStub)

    response = asyncio.run(
        chat_module.chat(
            request=ChatRequest(message="What is the policy?"),
            current_user=SimpleNamespace(id="user-test-123"),
            current_org=SimpleNamespace(id="org-123"),
            db=SimpleNamespace(),
        )
    )
    events = asyncio.run(collect_events(response))

    assert response.media_type == "text/event-stream"
    assert response.headers["cache-control"] == "no-cache"
    assert events == [
        'event: sources\ndata: {"sources": [{"score": 0.91, "text": "Policy details", "file_name": "policy.pdf"}]}\n\n',
        'event: token\ndata: {"token": "Hello"}\n\n',
        'event: token\ndata: {"token": " world"}\n\n',
        'event: done\ndata: {"done": true}\n\n',
    ]
    assert json.loads(events[-1].split("data: ", maxsplit=1)[1]) == {"done": True}


def test_chat_rejects_a_session_outside_the_current_tenant(monkeypatch):
    monkeypatch.setattr(chat_module, "get_client", LangfuseClientStub)
    request = ChatRequest(message="What is the policy?", session_id=uuid.uuid4())

    try:
        asyncio.run(
            chat_module.chat(
                request=request,
                current_user=SimpleNamespace(id="user-test-123"),
                current_org=SimpleNamespace(id="org-123"),
                db=DatabaseStub(session=None),
            )
        )
    except HTTPException as error:
        assert error.status_code == 404
        assert error.detail == "Chat session not found"
    else:  # pragma: no cover - makes the security expectation explicit
        raise AssertionError("Expected a cross-tenant session to be rejected")
