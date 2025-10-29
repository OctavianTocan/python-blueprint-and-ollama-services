"""Blueprint-level metadata extraction.

Provides functions to extract blueprint name and parent class from header text.
"""

from __future__ import annotations

import re
from typing import Optional

from toolkit.text_parsing import extract_tail_identifier

from .models import BlueprintMetadata


def build_metadata(content: str) -> BlueprintMetadata:
    """Collect blueprint-level metadata.

    @param content: Full blueprint text.
    @return: Metadata with name and parent class.
    """
    name = extract_blueprint_name(content)
    parent = extract_parent_class(content)
    return BlueprintMetadata(name=name, parent_class=parent)


def extract_blueprint_name(content: str) -> str:
    """Derive blueprint asset name from header.

    @param content: Blueprint text.
    @return: Blueprint name or fallback.
    """
    match = re.search(r'Begin Object Class=/Script/\S+\s+Name="([^"]+)"', content)
    if match:
        return match.group(1)
    return "Unknown Blueprint"


def extract_parent_class(content: str) -> Optional[str]:
    """Identify parent class referenced by blueprint.

    @param content: Blueprint text.
    @return: Cleaned parent class name or None.
    """
    patterns = [
        r"ParentClass=Class\'\"([^\"]+)\"",
        r"GeneratedClass=BlueprintGeneratedClass\'\"([^\"]+)\"",
    ]
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return extract_tail_identifier(match.group(1))
    return None
