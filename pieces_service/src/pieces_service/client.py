"""Pieces SDK client wrapper.

Provides simplified interface to Pieces copilot for asking questions
and retrieving answers.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def ask_copilot_question(prompt: str) -> str:
    """Send prompt to Pieces copilot and return response.

    @param prompt: Question or prompt to send.
    @return: Copilot response text with code blocks stripped.
    @raises RuntimeError: If SDK fails or returns empty response.
    """
    from pieces_os_client.wrapper import PiecesClient

    try:
        client = PiecesClient()
        response_text = stream_copilot_response(client, prompt)
        client.close()

        if not response_text.strip():
            raise RuntimeError("Pieces SDK returned empty response")

        return strip_markdown_code_blocks(response_text)

    except Exception as exc:
        raise RuntimeError(f"Failed to get response from Pieces copilot: {exc}")


def stream_copilot_response(client, prompt: str) -> str:
    """Stream response from copilot client.

    @param client: Initialized Pieces client.
    @param prompt: Question to ask.
    @return: Accumulated response text.
    """
    response_text = ""
    for response in client.copilot.stream_question(prompt):
        if response.question:
            for answer in response.question.answers.iterable:
                response_text += answer.text
    return response_text


def strip_markdown_code_blocks(text: str) -> str:
    """Remove markdown code block formatting if present.

    @param text: Response text potentially wrapped in code blocks.
    @return: Cleaned text without code block markers.
    """
    cleaned = text.strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        lines = cleaned.split("\n")
        if len(lines) > 2:
            # Remove first and last lines (```language and ```)
            return "\n".join(lines[1:-1]).strip()
        if len(lines) == 2:
            # Single line code block like ```text```
            return lines[0].strip("`").strip()
    return cleaned
