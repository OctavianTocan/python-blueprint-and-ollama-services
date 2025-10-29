"""Text formatting utilities for rendering lists and structured output.

Provides helpers for formatting inline lists, wrapping items with delimiters,
and creating consistent text representations across different output formats.
"""

from __future__ import annotations

from typing import Sequence


def format_inline_list(
    values: Sequence[str],
    limit: int,
    decorator: str = "`",
) -> str:
    """Format a sequence as an inline comma-separated list with overflow indicator.

    @param values: Items to format.
    @param limit: Maximum number of items to display before truncating.
    @param decorator: Character to wrap each item (e.g., backtick for markdown).
    @return: Formatted string like "`item1`, `item2`, … (+3 more)".
    """
    display = list(values)[:limit]
    decorated = ", ".join(f"{decorator}{value}{decorator}" for value in display)
    remaining = len(values) - limit
    if remaining > 0:
        decorated += f", … (+{remaining} more)"
    return decorated


def wrap_items_with_decorator(items: Sequence[str], decorator: str) -> list[str]:
    """Wrap each item in a sequence with a decorator character.

    @param items: Items to wrap.
    @param decorator: Wrapping character (e.g., "`" for code formatting).
    @return: List of wrapped items.
    """
    return [f"{decorator}{item}{decorator}" for item in items]
