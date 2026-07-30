import asyncio
import json
import sys
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


class RetrievalServiceStub:
    def retrieve_context(self, **_kwargs):
        return [{"score": 0.91, "text": "Policy details", "file_name": "policy.pdf"}]


class LLMServiceStub:
    async def stream_answer(self, **_kwargs):
        yield "Hello"
        yield " world"


async def collect_events(response):
    return [event async for event in response.body_iterator]


def test_chat_returns_sse_sources_tokens_and_completion(monkeypatch):
    monkeypatch.setattr(chat_module, "retrieval_service", RetrievalServiceStub())
    monkeypatch.setattr(chat_module, "llm_service", LLMServiceStub())

    response = asyncio.run(
        chat_module.chat(
            request=ChatRequest(message="What is the policy?"),
            current_user=SimpleNamespace(),
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
