#!/usr/bin/env python3
"""
Simple Pieces SDK utilities for asking the copilot questions.

This module provides straightforward functions for interacting with the Pieces SDK
copilot without complex configuration or setup.
"""

import logging
from pieces_os_client.wrapper import PiecesClient

logger = logging.getLogger(__name__)


def ask_copilot(prompt: str) -> str:
    """
    Ask the Pieces copilot a question and get the response.

    This is a simple, straightforward function that sends a prompt to the Pieces SDK
    copilot and returns the response without any complex setup or configuration.

    Args:
        prompt: The question or prompt to send to the copilot.

    Returns:
        The copilot's response as a string, with any markdown code blocks stripped.

    Raises:
        RuntimeError: If the Pieces SDK fails or returns no response.

    Example:
        >>> response = ask_copilot("What is the capital of France?")
        >>> print(response)
        The capital of France is Paris.
    """
    try:
        # Initialize client and ask the question
        client = PiecesClient()
        response_text = ""

        for response in client.copilot.stream_question(prompt):
            if response.question:
                for answer in response.question.answers.iterable:
                    response_text += answer.text

        client.close()

        if not response_text.strip():
            raise RuntimeError("Pieces SDK returned empty response")

        # Strip markdown code blocks if present
        response_text = response_text.strip()
        if response_text.startswith("```") and response_text.endswith("```"):
            lines = response_text.split("\n")
            # Remove first and last lines (```language and ```)
            if len(lines) > 2:
                response_text = "\n".join(lines[1:-1]).strip()
            elif len(lines) == 2:
                # Single line code block like ```text```
                response_text = lines[0].strip("`").strip()

        return response_text

    except Exception as e:
        raise RuntimeError(f"Failed to get response from Pieces copilot: {e}")
