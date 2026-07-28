import asyncio
from types import SimpleNamespace

from app.services.llm_service import LLMService


class StreamingLLM:
    async def astream(self, _messages):
        for content in ("Hello", "", " world"):
            yield SimpleNamespace(content=content)


class FailingLLM:
    async def astream(self, _messages):
        raise RuntimeError("OpenAI is unavailable")
        yield  # pragma: no cover


async def collect_tokens(service: LLMService):
    return [
        token
        async for token in service.stream_answer(
            query="What is the policy?",
            context_chunks=[],
        )
    ]


def test_stream_answer_yields_non_empty_text_tokens():
    service = object.__new__(LLMService)
    service.llm = StreamingLLM()

    assert asyncio.run(collect_tokens(service)) == ["Hello", " world"]


def test_stream_answer_yields_fallback_after_error():
    service = object.__new__(LLMService)
    service.llm = FailingLLM()

    assert asyncio.run(collect_tokens(service)) == [
        "I'm sorry, I encountered an error while trying to generate the answer."
    ]
