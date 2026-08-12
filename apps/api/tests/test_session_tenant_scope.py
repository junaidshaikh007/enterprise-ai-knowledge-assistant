import asyncio
import uuid
from types import SimpleNamespace

from app.api.v1.sessions import fetch_session_messages


class ScalarResultStub:
    def __init__(self, value):
        self.value = value

    def first(self):
        return self.value

    def all(self):
        return self.value


class QueryResultStub:
    def __init__(self, value):
        self.value = value

    def scalars(self):
        return ScalarResultStub(self.value)


class DatabaseStub:
    def __init__(self):
        self.statements = []

    async def execute(self, statement):
        self.statements.append(statement)
        return QueryResultStub(SimpleNamespace() if len(self.statements) == 1 else [])


def test_message_history_query_is_scoped_to_the_current_tenant_and_user():
    db = DatabaseStub()

    asyncio.run(
        fetch_session_messages(
            session_id=uuid.uuid4(),
            current_user=SimpleNamespace(id=uuid.uuid4()),
            current_org=SimpleNamespace(id=uuid.uuid4()),
            db=db,
        )
    )

    message_query = str(db.statements[1])
    assert "JOIN chat_sessions" in message_query
    assert "chat_sessions.user_id" in message_query
    assert "chat_sessions.organization_id" in message_query
