"""Collection utilities for deduplication and list processing.

Provides helpers for maintaining order while removing duplicates and other
common collection transformation patterns.
"""

from __future__ import annotations

from typing import List, Sequence


def dedupe_preserve_order(items: Sequence[str]) -> List[str]:
    """Remove duplicates while preserving first occurrence order.

    @param items: Sequence potentially containing duplicates.
    @return: List with duplicates removed, original order maintained.
    """
    seen: set[str] = set()
    result: List[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result
