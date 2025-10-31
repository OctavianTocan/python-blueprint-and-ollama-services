"""Variable entry collection and parsing.

Handles extraction of variable metadata sections from blueprint text
using balanced parenthesis matching.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Payload:
    """Balanced parenthesis payload extracted from blueprint text."""

    text: str
    next_index: int


def collect_variable_entries(content: str, anchor: str) -> List[str]:
    """Extract parenthesized metadata sections anchored by a token.

    @param content: Full blueprint text.
    @param anchor: Anchor keyword (e.g., "VariablesDescriptions").
    @return: List of extracted variable metadata strings.
    """
    entries: List[str] = []
    search_pos = 0

    while True:
        anchor_pos = content.find(anchor, search_pos)
        if anchor_pos == -1:
            return entries

        payload = extract_parenthesized_payload(content, anchor_pos)
        if payload:
            entries.append(payload.text)
            search_pos = payload.next_index
            continue

        search_pos = anchor_pos + len(anchor)


def extract_parenthesized_payload(content: str, start_index: int) -> Optional[Payload]:
    """Extract inner text of next balanced parenthesized block.

    @param content: Full text to search.
    @param start_index: Position to start searching from.
    @return: Payload containing extracted text and next index, or None.
    """
    open_index = content.find("=(", start_index)
    if open_index == -1:
        return None

    pos = open_index + 2
    depth = 1
    in_quote: Optional[str] = None

    while pos < len(content) and depth > 0:
        char = content[pos]
        if char in {'"', "'"}:
            if in_quote == char:
                in_quote = None
            elif in_quote is None:
                in_quote = char
        elif in_quote is None:
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
        pos += 1

    if depth != 0:
        return None

    return Payload(text=content[open_index + 2 : pos - 1], next_index=pos)
