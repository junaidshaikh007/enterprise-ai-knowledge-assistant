import json

from app.api.v1.sse import format_sse_event


def test_format_sse_event_serializes_json_payload():
    message = format_sse_event({"token": "Hello\nworld"})

    assert message.endswith("\n\n")
    assert message.startswith("data: ")
    assert json.loads(message.removeprefix("data: ").strip()) == {
        "token": "Hello\nworld"
    }


def test_format_sse_event_includes_optional_event_name():
    assert format_sse_event({"sources": []}, event="sources") == (
        'event: sources\ndata: {"sources": []}\n\n'
    )
