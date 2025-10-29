"""Shared utilities for parsing blueprint COPY files."""

from __future__ import annotations

import re
from typing import List, Optional, Sequence

METADATA_PAIR_RE = re.compile(r'(\w+)=(".*?"|\'.*?\'|[^,]+)')
FUNCTION_REF_RE = re.compile(r"FunctionReference=\(([^)]*)\)")
VARIABLE_REF_RE = re.compile(r"VariableReference=\(([^)]*)\)")
COMMENT_RE = re.compile(r"NodeComment=\"([^\"]+)\"")
CONTAINER_RE = re.compile(r"ContainerType=([A-Za-z]+)")


def find_first(pattern: str, text: str) -> Optional[str]:
    """Return the first capture group for a regex pattern."""

    match = re.search(pattern, text)
    return match.group(1) if match else None


def strip_wrappers(value: str) -> str:
    """Remove surrounding quotes or whitespace from a value."""

    trimmed = value.strip()
    if trimmed and trimmed[0] in {'"', "'"} and trimmed[-1] == trimmed[0]:
        return trimmed[1:-1]
    return trimmed


def extract_class_tail(raw: Optional[str]) -> Optional[str]:
    """Reduce a class reference to its readable tail."""

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


def dedupe_preserve_order(items: Sequence[str]) -> List[str]:
    """Remove duplicates while preserving the first occurrence order."""

    seen: set[str] = set()
    result: List[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def parse_metadata_map(chunk: str) -> dict[str, str]:
    """Convert blueprint metadata text into a dictionary."""

    data: dict[str, str] = {}
    for key, value in METADATA_PAIR_RE.findall(chunk):
        data[key] = strip_wrappers(value)
    return data
