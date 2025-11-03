"""Ollama Service.

HTTP API wrapper for Ollama providing LLM query capabilities.
"""

from __future__ import annotations

from .summaries import generate_rolling_summary

__version__ = "0.1.0"

__all__ = ["generate_rolling_summary"]
