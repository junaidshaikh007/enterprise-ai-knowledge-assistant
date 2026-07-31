"""Manually validate the chat API's Server-Sent Events response."""

import argparse
import json
import os
from urllib.request import Request, urlopen


DEFAULT_API_URL = "http://localhost:8000/api/v1/chat/"


def build_headers(access_token: str | None) -> dict[str, str]:
    """Build the headers expected by the authenticated SSE chat endpoint."""
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def build_request_body(message: str) -> bytes:
    """Serialize the chat request in the format accepted by the API."""
    return json.dumps({"message": message}).encode("utf-8")


def open_sse_stream(api_url: str, message: str, access_token: str | None):
    """Open the authenticated chat request and return its streaming response."""
    request = Request(
        api_url,
        data=build_request_body(message),
        headers=build_headers(access_token),
        method="POST",
    )
    return urlopen(request, timeout=30)


def print_sse_lines(response) -> None:
    """Print each non-empty SSE line as soon as the server sends it."""
    for raw_line in response:
        line = raw_line.decode("utf-8").strip()
        if line:
            print(line)


def parse_args() -> argparse.Namespace:
    """Read the connection details and question for one manual stream check."""
    parser = argparse.ArgumentParser(
        description="Send a chat question and print the SSE events as they arrive."
    )
    parser.add_argument(
        "message",
        help="Question to send to the chat endpoint.",
    )
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"Chat endpoint URL (default: {DEFAULT_API_URL}).",
    )
    parser.add_argument(
        "--access-token",
        default=os.getenv("ACCESS_TOKEN"),
        help="JWT access token (defaults to the ACCESS_TOKEN environment variable).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    parse_args()
