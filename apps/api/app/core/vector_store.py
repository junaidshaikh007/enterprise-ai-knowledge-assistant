from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.collection_name = "knowledge_base"
        try:
            if settings.QDRANT_HOST in ("localhost", "127.0.0.1"):
                self.client = QdrantClient(location=":memory:")
            else:
                self.client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    api_key=settings.QDRANT_API_KEY,
                    timeout=1.0,
                )
            self._ensure_collection_exists()
        except Exception as e:
            logger.warning(f"Falling back to in-memory Qdrant client: {e}")
            self.client = QdrantClient(location=":memory:")
            self._ensure_collection_exists()

    def _ensure_collection_exists(self):
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating Qdrant collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant collection exists: {e}")

vector_store = VectorStore()

