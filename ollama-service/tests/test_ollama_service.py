"""Tests for Ollama service."""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest
import httpx

from ollama_service.client import (
    ask_ollama_question,
    build_ollama_payload,
    parse_ollama_response,
    send_ollama_request,
    strip_markdown_code_blocks,
    validate_ollama_request,
)
from ollama_service.models import OllamaOptions, OllamaRequest, OllamaResponse


class TestOllamaClient:
    """Test cases for Ollama client functions."""

    def test_build_ollama_payload_basic(self):
        """Test building basic Ollama payload."""
        request = OllamaRequest(prompt="Hello world", model="minimax-m2:cloud")

        payload = build_ollama_payload(request)

        assert payload["model"] == "minimax-m2:cloud"
        assert payload["prompt"] == "Hello world"
        assert payload["stream"] is False
        assert "system" not in payload
        assert "options" not in payload

    def test_build_ollama_payload_with_system(self):
        """Test building payload with system prompt."""
        request = OllamaRequest(
            prompt="Hello world",
            model="minimax-m2:cloud",
            system="You are a helpful assistant.",
        )

        payload = build_ollama_payload(request)

        assert payload["system"] == "You are a helpful assistant."

    def test_build_ollama_payload_with_options(self):
        """Test building payload with custom options."""
        options = OllamaOptions(temperature=0.5, num_ctx=1024, num_predict=100)
        request = OllamaRequest(
            prompt="Hello world", model="minimax-m2:cloud", options=options
        )

        payload = build_ollama_payload(request)

        assert payload["options"]["temperature"] == 0.5
        assert payload["options"]["num_ctx"] == 1024
        assert payload["options"]["num_predict"] == 100

    def test_parse_ollama_response_success(self):
        """Test parsing valid Ollama response."""
        response_text = '{"response": "Hello there!", "done": true}'

        result = parse_ollama_response(response_text)

        assert result == "Hello there!"

    def test_parse_ollama_response_missing_field(self):
        """Test parsing response missing response field."""
        response_text = '{"done": true}'

        with pytest.raises(ValueError, match="Response missing 'response' field"):
            parse_ollama_response(response_text)

    def test_parse_ollama_response_invalid_json(self):
        """Test parsing invalid JSON response."""
        response_text = "invalid json"

        with pytest.raises(json.JSONDecodeError):
            parse_ollama_response(response_text)

    def test_strip_markdown_code_blocks_multiline(self):
        """Test stripping multiline code blocks."""
        text = "```python\nprint('hello')\n```"

        result = strip_markdown_code_blocks(text)

        assert result == "print('hello')"

    def test_strip_markdown_code_blocks_single_line(self):
        """Test stripping single line code blocks."""
        text = "```hello world```"

        result = strip_markdown_code_blocks(text)

        assert result == "hello world"

    def test_strip_markdown_code_blocks_no_formatting(self):
        """Test text without code block formatting."""
        text = "Just plain text"

        result = strip_markdown_code_blocks(text)

        assert result == "Just plain text"

    def test_validate_ollama_request_success(self):
        """Test valid request validation."""
        request = OllamaRequest(
            prompt="Hello world",
            model="minimax-m2:cloud",
            options=OllamaOptions(temperature=0.7, num_ctx=2048),
        )

        # Should not raise exception
        validate_ollama_request(request)

    def test_validate_ollama_request_empty_prompt(self):
        """Test validation with empty prompt."""
        request = OllamaRequest(prompt="   ", model="minimax-m2:cloud")

        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            validate_ollama_request(request)

    def test_validate_ollama_request_empty_model(self):
        """Test validation with empty model."""
        request = OllamaRequest(prompt="Hello", model="   ")

        with pytest.raises(ValueError, match="Model cannot be empty"):
            validate_ollama_request(request)

    @patch("ollama_service.client.send_ollama_request")
    def test_ask_ollama_question_success(self, mock_send):
        """Test successful Ollama question."""
        mock_send.return_value = "Hello there!"

        result = ask_ollama_question("Hello world")

        assert result == "Hello there!"
        mock_send.assert_called_once()

    @patch("ollama_service.client.send_ollama_request")
    def test_ask_ollama_question_empty_response(self, mock_send):
        """Test handling empty response."""
        mock_send.return_value = "   "

        with pytest.raises(RuntimeError, match="Ollama API returned empty response"):
            ask_ollama_question("Hello world")

    @patch("ollama_service.client.send_ollama_request")
    def test_ask_ollama_question_error(self, mock_send):
        """Test handling API error."""
        mock_send.side_effect = Exception("Connection failed")

        with pytest.raises(RuntimeError, match="Failed to get response from Ollama"):
            ask_ollama_question("Hello world")

    @patch("httpx.Client")
    def test_send_ollama_request_success(self, mock_client_class):
        """Test successful HTTP request."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '{"response": "Hello!", "done": true}'

        mock_client = Mock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        request = OllamaRequest(prompt="Hello", model="minimax-m2:cloud")

        result = send_ollama_request(request)

        assert result == "Hello!"
        mock_client.post.assert_called_once()

    @patch("httpx.Client")
    def test_send_ollama_request_timeout(self, mock_client_class):
        """Test timed out HTTP request."""
        mock_client = Mock()
        mock_client.post.side_effect = httpx.TimeoutException("Request timed out")
        mock_client_class.return_value.__enter__.return_value = mock_client

        with pytest.raises(httpx.TimeoutException):
            send_ollama_request(
                request=OllamaRequest(prompt="Hello", model="minimax-m2:cloud")
            )


class TestOllamaModels:
    """Test cases for Ollama models."""

    def test_ollama_request_defaults(self):
        """Test OllamaRequest with default values."""
        request = OllamaRequest(prompt="Hello")

        assert request.prompt == "Hello"
        assert request.model == "minimax-m2:cloud"
        assert request.system is None
        assert request.options is None
        assert request.headers == {}

    def test_ollama_options_defaults(self):
        """Test OllamaOptions with default values."""
        options = OllamaOptions()

        assert options.temperature == 0.7
        assert options.num_ctx == 2048
        assert options.num_predict == -1

    def test_ollama_response_creation(self):
        """Test OllamaResponse creation."""
        response = OllamaResponse(
            result="Hello world",
            model="minimax-m2:cloud",
            done=True,
            metadata={"request_id": "123"},
        )

        assert response.result == "Hello world"
        assert response.model == "minimax-m2:cloud"
        assert response.done is True
        assert response.metadata["request_id"] == "123"
