"""Request/response models for Ollama API.

Defines Pydantic models for API contract validation.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class OllamaOptions(BaseModel):
    """Configuration options for Ollama requests.

    @attr temperature: Controls randomness (0.0-1.0).
    @attr num_ctx: Token context window size.
    @attr num_predict: Maximum tokens to generate.
    """

    temperature: float = Field(
        default=0.7, ge=0.0, le=1.0, description="Controls randomness"
    )
    num_ctx: int = Field(default=2048, ge=1, description="Token context window size")
    num_predict: int = Field(
        default=-1, ge=-1, description="Maximum tokens to generate"
    )


class OllamaRequest(BaseModel):
    """Request model for Ollama ask endpoint.

    @attr prompt: Question or prompt to send to Ollama.
    @attr model: Ollama model to use.
    @attr system: Optional system prompt.
    @attr options: Generation options.
    @attr headers: Additional HTTP headers.
    @attr endpoint: Ollama API endpoint.
    """

    prompt: str = Field(description="Question or prompt to send to Ollama")
    model: str = Field(default="minimax-m2:cloud", description="Ollama model to use")
    system: Optional[str] = Field(default=None, description="Optional system prompt")
    options: Optional[OllamaOptions] = Field(
        default=None, description="Generation options"
    )
    headers: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Additional HTTP headers"
    )
    endpoint: Optional[str] = Field(default=None, description="Ollama API endpoint")


class OllamaResponse(BaseModel):
    """Response model for Ollama ask endpoint.

    @attr result: Ollama response text.
    @attr model: Model used for generation.
    @attr done: Whether generation is complete.
    @attr metadata: Additional response metadata.
    """

    result: str = Field(description="Ollama response text")
    model: Optional[str] = Field(default=None, description="Model used for generation")
    done: Optional[bool] = Field(
        default=None, description="Whether generation is complete"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional response metadata"
    )
