"""Text parsing utilities for extracting patterns from structured text.

Provides helpers for regex matching, metadata extraction, and text normalization
across different structured formats like blueprint files and API responses.
"""

from __future__ import annotations

import re
from typing import Optional


def find_first_match(pattern: str, text: str) -> Optional[str]:
    """Extract the first capture group from a regex pattern.

    @param pattern: Regular expression with at least one capture group.
    @param text: Text to search within.
    @return: First captured substring or None if no match found.
    """
    match = re.search(pattern, text)
    return match.group(1) if match else None


def strip_quote_wrappers(value: str) -> str:
    """Remove surrounding quotes or whitespace from a value.

    @param value: String potentially wrapped in quotes.
    @return: Cleaned string with quotes and outer whitespace removed.
    """
    trimmed = value.strip()
    if trimmed and trimmed[0] in {'"', "'"} and trimmed[-1] == trimmed[0]:
        return trimmed[1:-1]
    return trimmed


def extract_tail_identifier(raw: Optional[str]) -> Optional[str]:
    """Reduce a fully-qualified reference to its readable tail identifier.

    Handles blueprint paths, class references, and skeleton prefixes.

    @param raw: Fully-qualified path or class reference string.
    @return: Cleaned tail identifier or None if input is None/empty.
    """
    if not raw:
        return None
    cleaned = raw.replace('"', '')
    if "'" in cleaned:
        cleaned = cleaned.split("'", 1)[-1]
    cleaned = cleaned.replace("'", "")
    cleaned = cleaned.split('.')[-1]
    cleaned = cleaned.split('/')[-1]
    cleaned = cleaned.replace("SKEL_", "").replace("REINST_", "")
    result = cleaned.rstrip('_C')
    return result or cleaned


def normalize_multiline_comment(comment: str) -> str:
    """Sanitize comment text by removing line breaks and escape sequences.

    @param comment: Raw comment string potentially containing escape sequences.
    @return: Normalized single-line comment with whitespace collapsed.
    """
    cleaned = comment.replace("\\r", " ").replace("\\n", " ")
    cleaned = cleaned.replace("\\'", "'").replace('\\"', '"')
    return " ".join(cleaned.split()).strip()


def parse_key_value_pairs(
    chunk: str,
    pair_pattern: re.Pattern,
) -> dict[str, str]:
    """Convert structured text into a dictionary using regex pattern.

    @param chunk: Text containing key=value pairs.
    @param pair_pattern: Compiled regex with two capture groups (key, value).
    @return: Dictionary mapping keys to cleaned values.
    """
    data: dict[str, str] = {}
    for key, value in pair_pattern.findall(chunk):
        data[key] = strip_quote_wrappers(value)
    return data
