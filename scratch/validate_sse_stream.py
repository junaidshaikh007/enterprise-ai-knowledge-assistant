"""Manually validate the chat API's Server-Sent Events response."""

import argparse


DEFAULT_API_URL = "http://localhost:8000/api/v1/chat/"


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
    return parser.parse_args()


if __name__ == "__main__":
    parse_args()
