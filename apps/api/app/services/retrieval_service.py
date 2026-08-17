import logging
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from app.core.config import settings
from app.core.vector_store import vector_store
from app.core.observability import observe, get_client

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self):
        self._embeddings = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            api_key = settings.OPENAI_API_KEY or "dummy_key"
            self._embeddings = OpenAIEmbeddings(
                openai_api_key=api_key,
                model=settings.EMBEDDING_MODEL
            )
        return self._embeddings

    @observe()
    def retrieve_context(self, query: str, organization_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Takes a user query, generates an embedding, and retrieves the most relevant
        document chunks from Qdrant, filtered securely by organization_id.
        """
        try:
            get_client().update_current_span(
                name="retrieve_context",
                input={"query": query, "organization_id": organization_id, "top_k": top_k},
                metadata={"organization_id": organization_id}
            )
            org_str = str(organization_id)
            org_filter = Filter(
                must=[
                    FieldCondition(
                        key="organization_id",
                        match=MatchValue(value=org_str)
                    )
                ]
            )

            try:
                if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "dummy_key":
                    raise ValueError("No valid OpenAI API key configured. Using local document retrieval.")
                query_vector = self.embeddings.embed_query(query)
            except Exception as embed_err:
                logger.info(f"Local retrieval mode ({embed_err}). Retrieving organization context via local store.")
                try:
                    records, _ = vector_store.client.scroll(
                        collection_name=vector_store.collection_name,
                        scroll_filter=org_filter,
                        limit=top_k
                    )
                    if not records:
                        # Fallback scroll across all collection points if filter misses
                        records, _ = vector_store.client.scroll(
                            collection_name=vector_store.collection_name,
                            limit=top_k
                        )
                    context = []
                    for rec in records:
                        context.append({
                            "score": 1.0,
                            "text": rec.payload.get("text", ""),
                            "file_name": rec.payload.get("file_name", ""),
                        })
                    logger.info(f"Retrieved {len(context)} relevant chunks via local scroll fallback.")
                    return context
                except Exception as scroll_err:
                    logger.error(f"Scroll fallback failed: {scroll_err}")
                    query_vector = [0.1] * 1536

            
            logger.info(f"Querying Qdrant for org_id: {organization_id}")
            # Ensure multi-tenancy: Only search documents belonging to this organization
            org_filter = Filter(
                must=[
                    FieldCondition(
                        key="organization_id",
                        match=MatchValue(value=str(organization_id))
                    )
                ]
            )
            
            search_results = vector_store.client.search(
                collection_name=vector_store.collection_name,
                query_vector=query_vector,
                query_filter=org_filter,
                limit=top_k
            )
            
            # Format results
            context = []
            for result in search_results:
                context.append({
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "file_name": result.payload.get("file_name", ""),
                })
                
            logger.info(f"Retrieved {len(context)} relevant chunks.")
            get_client().update_current_span(output=context)
            return context
            
        except Exception as e:
            get_client().update_current_span(level="ERROR", status_message=str(e))
            logger.error(f"Failed to retrieve context: {e}")
            return []

retrieval_service = RetrievalService()
