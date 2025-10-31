"""Node-level parsing for graph elements.

Extracts semantic information from individual nodes including function calls,
variable accesses, custom events, and developer comments.
"""

from __future__ import annotations

import re

from ..models import NodeBlock


# Compiled patterns for efficient matching
FUNCTION_REF_RE = re.compile(r"FunctionReference=\(([^)]*)\)")
VARIABLE_REF_RE = re.compile(r"VariableReference=\(([^)]*)\)")
COMMENT_RE = re.compile(r"NodeComment=\"([^\"]+)\"")
METADATA_PAIR_RE = re.compile(r'(\w+)=(".*?"|\'.*?\'|[^,]+)')


def classify_node_kind(node_name: str) -> str:
    """Reduce node name to semantic kind.

    @param node_name: Full node identifier.
    @return: Simplified node type (e.g., "VariableGet", "Comment").
    """
    if node_name.startswith("K2Node_"):
        tail = node_name[len("K2Node_") :]
        return tail.split("_")[0]
    if node_name.startswith("EdGraphNode_Comment"):
        return "Comment"
    return node_name


def extract_custom_event_name(kind: str, text: str) -> str | None:
    """Parse custom event name from node text.

    @param kind: Node kind classification.
    @param text: Full node text content.
    @return: Event name or None if not a custom event.
    """
    if kind != "CustomEvent":
        return None
    match = re.search(r'CustomFunctionName="([^"]+)"', text)
    return match.group(1) if match else None


def extract_function_entry_name(kind: str, text: str) -> str | None:
    """Parse function entry name from node text.

    @param kind: Node kind classification.
    @param text: Full node text content.
    @return: Function name or None if not a function entry.
    """
    if kind != "FunctionEntry":
        return None
    match = re.search(r'CustomGeneratedFunctionName="([^"]+)"', text)
    return match.group(1) if match else None


def extract_function_calls(text: str) -> set[str]:
    """Parse function call references from node text.

    @param text: Node text containing function references.
    @return: Set of formatted function call strings.
    """
    from toolkit.text_parsing import parse_key_value_pairs, extract_tail_identifier

    references: set[str] = set()
    for chunk in FUNCTION_REF_RE.findall(text):
        metadata = parse_key_value_pairs(chunk, METADATA_PAIR_RE)
        name = metadata.get("MemberName")
        if not name:
            continue

        if is_self_context(metadata):
            references.add(f"self.{name}")
            continue

        parent_name = extract_parent_class(metadata)
        references.add(f"{parent_name}::{name}" if parent_name else name)

    return references


def is_self_context(metadata: dict[str, str]) -> bool:
    """Check if function call is in self context.

    @param metadata: Parsed metadata dictionary.
    @return: True if bSelfContext is true.
    """
    return metadata.get("bSelfContext", "").lower() == "true"


def extract_parent_class(metadata: dict[str, str]) -> str | None:
    """Extract parent class name from metadata.

    @param metadata: Parsed metadata dictionary.
    @return: Cleaned parent class name or None.
    """
    from toolkit.text_parsing import extract_tail_identifier

    parent = metadata.get("MemberParent") or metadata.get("Outer")
    return extract_tail_identifier(parent)


def extract_variable_names(text: str) -> set[str]:
    """Parse variable references from node text.

    @param text: Node text containing variable references.
    @return: Set of variable names.
    """
    from toolkit.text_parsing import parse_key_value_pairs

    names: set[str] = set()
    for chunk in VARIABLE_REF_RE.findall(text):
        metadata = parse_key_value_pairs(chunk, METADATA_PAIR_RE)
        name = metadata.get("MemberName")
        if name:
            names.add(name)

    return names


def extract_node_comments(text: str) -> list[str]:
    """Collect developer comments from node text.

    @param text: Node text potentially containing comments.
    @return: List of normalized comment strings.
    """
    from toolkit.text_parsing import normalize_multiline_comment

    comments = []
    for raw_comment in COMMENT_RE.findall(text):
        normalized = normalize_multiline_comment(raw_comment)
        if normalized:
            comments.append(normalized)

    return comments
