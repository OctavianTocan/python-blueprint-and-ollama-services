"""Ollama API client wrapper.

Provides simplified interface to Ollama for asking questions
and retrieving answers.
"""

from __future__ import annotations

import json
import logging
from typing import Optional

import httpx

from .models import OllamaOptions, OllamaRequest, OllamaResponse

logger = logging.getLogger(__name__)


def ask_ollama_question(
    prompt: str,
    model: str = "llama2",
    system: Optional[str] = None,
    options: Optional[OllamaOptions] = None,
    endpoint: str = "http://localhost:11434/api/generate",
    headers: Optional[dict] = None,
) -> str:
    """Send prompt to Ollama and return response.

    @param prompt: Question or prompt to send.
    @param model: Ollama model to use.
    @param system: Optional system prompt.
    @param options: Generation options.
    @param endpoint: Ollama API endpoint.
    @param headers: Additional HTTP headers.
    @return: Ollama response text.
    @raises RuntimeError: If API fails or returns empty response.
    """
    request = OllamaRequest(
        prompt=prompt,
        model=model,
        system=system,
        options=options or OllamaOptions(),
        headers=headers or {},
        endpoint=endpoint,
    )

    try:
        response_text = send_ollama_request(request)

        if not response_text.strip():
            raise RuntimeError("Ollama API returned empty response")

        return strip_markdown_code_blocks(response_text)

    except Exception as exc:
        raise RuntimeError(f"Failed to get response from Ollama: {exc}")


def send_ollama_request(request: OllamaRequest) -> str:
    """Send HTTP request to Ollama API.

    @param request: Request configuration.
    @return: Response text from Ollama.
    @raises httpx.HTTPError: On HTTP errors.
    @raises json.JSONDecodeError: On invalid JSON response.
    """
    endpoint = request.endpoint or "http://localhost:11434/api/generate"

    payload = build_ollama_payload(request)

    default_headers = {"Content-Type": "application/json"}
    if request.headers:
        default_headers.update(request.headers)

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            endpoint,
            json=payload,
            headers=default_headers,
        )
        response.raise_for_status()

        return parse_ollama_response(response.text)


def build_ollama_payload(request: OllamaRequest) -> dict:
    """Build JSON payload for Ollama API.

    @param request: Request configuration.
    @return: JSON payload dict.
    """
    payload = {
        "model": request.model,
        "prompt": request.prompt,
        "stream": False,
    }

    if request.system:
        payload["system"] = request.system

    if request.options:
        options_dict = {}
        if request.options.temperature != 0.7:
            options_dict["temperature"] = request.options.temperature
        if request.options.num_ctx != 2048:
            options_dict["num_ctx"] = request.options.num_ctx
        if request.options.num_predict != -1:
            options_dict["num_predict"] = request.options.num_predict

        if options_dict:
            payload["options"] = options_dict

    return payload


def parse_ollama_response(response_text: str) -> str:
    """Parse Ollama API response and extract content.

    @param response_text: Raw JSON response from Ollama.
    @return: Extracted response content.
    @raises json.JSONDecodeError: On invalid JSON.
    @raises ValueError: On missing response field.
    """
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as exc:
        raise json.JSONDecodeError(
            f"Invalid JSON response: {exc}", response_text, exc.pos
        )

    if "response" not in data:
        raise ValueError("Response missing 'response' field")

    return data["response"]


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
        if len(lines) == 1:
            # Single line code block like ```text```
            return lines[0].strip("`").strip()
    return cleaned


def validate_ollama_request(request: OllamaRequest) -> None:
    """Validate Ollama request parameters.

    @param request: Request to validate.
    @raises ValueError: On invalid parameters.
    """
    if not request.prompt.strip():
        raise ValueError("Prompt cannot be empty")

    if not request.model.strip():
        raise ValueError("Model cannot be empty")

    if request.options:
        if not (0.0 <= request.options.temperature <= 1.0):
            raise ValueError("Temperature must be between 0.0 and 1.0")
        if request.options.num_ctx <= 0:
            raise ValueError("num_ctx must be positive")
