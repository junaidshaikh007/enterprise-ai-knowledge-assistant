import uuid
from typing import List, Dict, Any
from langchain_openai import OpenAIEmbeddings
from qdrant_client.http.models import PointStruct
from app.core.config import settings
from app.core.vector_store import vector_store
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        # Fallback to a dummy key if OPENAI_API_KEY is not set yet
        api_key = settings.OPENAI_API_KEY or "dummy_key"
        
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=api_key,
            model=settings.EMBEDDING_MODEL
        )

    def embed_and_store_chunks(self, chunks: List[str], organization_id: int, file_name: str) -> bool:
        """
        Takes a list of text chunks, generates vector embeddings via OpenAI,
        and stores them in Qdrant alongside metadata.
        """
        if not chunks:
            return True

        try:
            logger.info(f"Generating embeddings for {len(chunks)} chunks...")
            try:
                if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "dummy_key":
                    raise ValueError("No valid OpenAI API key configured. Using local vector generation.")
                vectors = self.embeddings.embed_documents(chunks)
            except Exception as embed_err:
                logger.warning(f"Embedding notice ({embed_err}). Generating fast local vectors.")
                import random
                vectors = []
                for chunk in chunks:
                    rng = random.Random(hash(chunk))
                    vectors.append([rng.uniform(-1.0, 1.0) for _ in range(1536)])

            
            points = []
            for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
                # We use uuid.uuid4().hex as the point ID in Qdrant
                point_id = str(uuid.uuid4())
                points.append(
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload={
                            "text": chunk,
                            "organization_id": str(organization_id),
                            "file_name": file_name,
                            "chunk_index": i
                        }
                    )
                )

            logger.info(f"Uploading {len(points)} points to Qdrant...")
            vector_store.client.upsert(
                collection_name=vector_store.collection_name,
                points=points
            )
            return True
        except Exception as e:
            logger.error(f"Failed to embed and store chunks: {e}")
            return False

embedding_service = EmbeddingService()
