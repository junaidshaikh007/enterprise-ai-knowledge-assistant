import logging
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from app.core.config import settings
from app.core.vector_store import vector_store

logger = logging.getLogger(__name__)

class RetrievalService:
    def __init__(self):
        api_key = settings.OPENAI_API_KEY or "dummy_key"
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            model=settings.EMBEDDING_MODEL
        )

    def retrieve_context(self, query: str, organization_id: int, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Takes a user query, generates an embedding, and retrieves the most relevant
        document chunks from Qdrant, filtered securely by organization_id.
        """
        try:
            logger.info(f"Generating embedding for query: '{query}'")
            query_vector = self.embeddings.embed_query(query)
            
            logger.info(f"Querying Qdrant for org_id: {organization_id}")
            # Ensure multi-tenancy: Only search documents belonging to this organization
            org_filter = Filter(
                must=[
                    FieldCondition(
                        key="organization_id",
                        match=MatchValue(value=organization_id)
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
            return context
            
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return []

retrieval_service = RetrievalService()
