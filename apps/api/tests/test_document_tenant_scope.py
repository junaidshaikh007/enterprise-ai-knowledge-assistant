import asyncio
import sys
from enum import Enum
from types import SimpleNamespace
import uuid


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
sys.modules.setdefault("qdrant_client", SimpleNamespace(QdrantClient=_QdrantClientStub))
sys.modules.setdefault(
    "qdrant_client.http.models",
    SimpleNamespace(
        Distance=_DistanceStub,
        FieldCondition=_ModelStub,
        Filter=_ModelStub,
        MatchValue=_ModelStub,
        PointStruct=_ModelStub,
        VectorParams=_ModelStub,
    ),
)

from fastapi import HTTPException

from app.api.v1.documents import delete_document, get_document_status


class QueryResultStub:
    def scalar_one_or_none(self):
        return None


class DatabaseStub:
    def __init__(self):
        self.statements = []

    async def execute(self, statement):
        self.statements.append(statement)
        return QueryResultStub()


def assert_cross_tenant_document_is_hidden(endpoint):
    db = DatabaseStub()
    doc_id = uuid.uuid4()

    try:
        asyncio.run(
            endpoint(
                doc_id=doc_id,
                current_user=SimpleNamespace(id=uuid.uuid4()),
                current_org=SimpleNamespace(id=uuid.uuid4()),
                db=db,
            )
        )
    except HTTPException as error:
        assert error.status_code == 404
    else:  # pragma: no cover
        raise AssertionError("Expected an inaccessible document to return 404")

    query = str(db.statements[0])
    assert "documents.organization_id" in query


def test_document_status_hides_documents_outside_the_current_tenant():
    assert_cross_tenant_document_is_hidden(get_document_status)


def test_document_delete_hides_documents_outside_the_current_tenant():
    assert_cross_tenant_document_is_hidden(delete_document)
