"""Helpers for producing Server-Sent Events responses."""

import json
from typing import Any


def format_sse_event(data: Any, event: str | None = None) -> str:
    """Serialize a payload into one valid Server-Sent Events message.

    JSON keeps token contents unambiguous and lets the browser parse every
    streamed payload consistently.
    """
    payload = json.dumps(data, ensure_ascii=False)
    event_prefix = f"event: {event}\n" if event else ""
    return f"{event_prefix}data: {payload}\n\n"
