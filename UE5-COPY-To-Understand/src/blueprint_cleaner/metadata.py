"""Blueprint-level metadata extraction."""

from __future__ import annotations

import re
from typing import Optional

from .models import BlueprintMetadata
from .utils import extract_class_tail


def build_metadata(content: str) -> BlueprintMetadata:
    """Collect blueprint-level metadata."""

    name = extract_blueprint_name(content)
    parent = extract_parent_class(content)
    return BlueprintMetadata(name=name, parent_class=parent)


def extract_blueprint_name(content: str) -> str:
    """Derive the blueprint asset name from the header."""

    match = re.search(r'Begin Object Class=/Script/\S+\s+Name="([^"]+)"', content)
    if match:
        return match.group(1)
    return "Unknown Blueprint"


def extract_parent_class(content: str) -> Optional[str]:
    """Identify the parent class referenced by the blueprint."""

    patterns = [
        r"ParentClass=Class\'\"([^\"]+)\"",
        r"GeneratedClass=BlueprintGeneratedClass\'\"([^\"]+)\"",
    ]
    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return extract_class_tail(match.group(1))
    return None
