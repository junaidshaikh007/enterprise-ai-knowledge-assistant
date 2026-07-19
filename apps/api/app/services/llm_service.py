import logging
from typing import List, Dict, Any
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
            temperature=0.0
        )

    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Takes the user query and the retrieved context chunks, constructs a prompt,
        and asks the LLM to generate an answer based STRICTLY on the context.
        """
        try:
            logger.info(f"Generating answer for query: '{query}' with {len(context_chunks)} context chunks.")
            
            # Format context into a single string
            context_text = ""
            for i, chunk in enumerate(context_chunks):
                text = chunk.get("text", "").strip()
                file_name = chunk.get("file_name", "Unknown File")
                context_text += f"\n--- Chunk {i+1} (Source: {file_name}) ---\n{text}\n"

            system_prompt = (
                "You are an enterprise AI knowledge assistant. You will be provided with context "
                "from the organization's knowledge base. Answer the user's question based ONLY "
                "on the provided context. If the answer cannot be found in the context, politely "
                "state that you do not have that information. Do not hallucinate or use outside knowledge."
                "\n\nContext:\n"
                f"{context_text}"
            )
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
            
            response = self.llm.invoke(messages)
            
            logger.info("Answer generated successfully.")
            return response.content

        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            return "I'm sorry, I encountered an error while trying to generate the answer."

llm_service = LLMService()
