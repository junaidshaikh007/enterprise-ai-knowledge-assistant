import logging
from typing import Any, AsyncIterator, Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        api_key = settings.OPENAI_API_KEY or "dummy_key"
        self.llm = ChatOpenAI(
            openai_api_key=api_key,
            model_name="gpt-4o",  # or gpt-3.5-turbo based on settings
            temperature=0.0,
            streaming=True,
        )

    def _build_messages(
        self, query: str, context_chunks: List[Dict[str, Any]]
    ) -> List[SystemMessage | HumanMessage]:
        """Build the context-grounded messages used by synchronous and streamed replies."""
        context_text = ""
        for index, chunk in enumerate(context_chunks, start=1):
            text = chunk.get("text", "").strip()
            file_name = chunk.get("file_name", "Unknown File")
            context_text += f"\n--- Chunk {index} (Source: {file_name}) ---\n{text}\n"

        system_prompt = (
            "You are an enterprise AI knowledge assistant. You will be provided with context "
            "from the organization's knowledge base. Answer the user's question based ONLY "
            "on the provided context. If the answer cannot be found in the context, politely "
            "state that you do not have that information. Do not hallucinate or use outside knowledge."
            "\n\nContext:\n"
            f"{context_text}"
        )

        return [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query),
        ]

    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Generate a complete answer from the retrieved context chunks."""
        try:
            logger.info(f"Generating answer for query: '{query}' with {len(context_chunks)} context chunks.")
            messages = self._build_messages(query, context_chunks)
            
            response = self.llm.invoke(messages)
            
            logger.info("Answer generated successfully.")
            return response.content

        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return "I'm sorry, I encountered an error while trying to generate the answer."

    async def stream_answer(
        self, query: str, context_chunks: List[Dict[str, Any]]
    ) -> AsyncIterator[str]:
        """Asynchronously yield non-empty text tokens from the configured LLM."""
        logger.info(
            "Streaming answer for query: '%s' with %d context chunks.",
            query,
            len(context_chunks),
        )
        messages = self._build_messages(query, context_chunks)

        async for chunk in self.llm.astream(messages):
            content = chunk.content
            if isinstance(content, str) and content:
                yield content

llm_service = LLMService()
