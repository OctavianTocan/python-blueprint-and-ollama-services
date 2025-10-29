"""Variable extraction helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

from .models import VariableInfo
from .utils import CONTAINER_RE, extract_class_tail, find_first


def extract_variables(content: str) -> List[VariableInfo]:
    """Parse variable declarations from blueprint text."""

    entries = collect_variable_entries(content, "VariablesDescriptions")
    entries.extend(collect_variable_entries(content, "NewVariables"))
    variables = [parse_variable_entry(entry) for entry in entries]
    filtered = [variable for variable in variables if variable]
    return deduplicate_variables(filtered)


def collect_variable_entries(content: str, anchor: str) -> List[str]:
    """Extract parenthesised metadata sections anchored by a token."""

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


@dataclass
class Payload:
    """Balanced parenthesis payload extracted from the blueprint text."""

    text: str
    next_index: int


def extract_parenthesized_payload(content: str, start_index: int) -> Optional[Payload]:
    """Return the inner text of the next balanced parenthesised block."""

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
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
        pos += 1
    if depth != 0:
        return None
    return Payload(text=content[open_index + 2:pos - 1], next_index=pos)


def parse_variable_entry(entry: str) -> Optional[VariableInfo]:
    """Translate raw variable metadata into a structured record."""

    name = find_first(r'FriendlyName="([^"]+)"', entry) or find_first(r'VarName="([^"]+)"', entry)
    if not name:
        return None
    category = parse_category(entry) or "Uncategorized"
    pin_category, pin_subcategory = parse_pin_type(entry)
    object_type = parse_subcategory_object(entry)
    subtype = object_type or pin_subcategory
    type_label = compose_type_label(pin_category, pin_subcategory, object_type)
    return VariableInfo(
        name=name,
        category=category,
        var_type=type_label,
        container=parse_container_type(entry),
        subtype=subtype,
    )


def parse_category(entry: str) -> Optional[str]:
    """Extract the display category label from metadata."""

    match = find_first(r'Category=NSLOCTEXT\([^,]+,[^,]+,"([^"]+)"\)', entry)
    if match:
        return match
    return find_first(r'Category="([^"]+)"', entry)


def parse_pin_type(entry: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract pin category information from a variable entry."""

    category = find_first(r'PinCategory="([^"]+)"', entry)
    subcategory = find_first(r'PinSubCategory="([^"]+)"', entry)
    return category, subcategory


def parse_container_type(entry: str) -> Optional[str]:
    """Read the container semantics for a variable."""

    match = CONTAINER_RE.search(entry)
    if not match:
        return None
    value = match.group(1)
    return None if value.lower() == "none" else value


def parse_subcategory_object(entry: str) -> Optional[str]:
    """Resolve the object or struct referenced by a variable type."""

    patterns = [
        r'PinSubCategoryObject=([^,]+)',
        r'SubCategoryObject=([^,]+)',
    ]
    for pattern in patterns:
        raw_value = find_first(pattern, entry)
        if raw_value:
            return extract_class_tail(raw_value.rstrip(')'))
    return None


def compose_type_label(
    pin_category: Optional[str],
    pin_subcategory: Optional[str],
    object_type: Optional[str],
) -> Optional[str]:
    """Build a human-readable type label from pin metadata."""

    if pin_category and object_type:
        return f"{pin_category}<{object_type}>"
    if pin_category and pin_subcategory:
        return f"{pin_category} ({pin_subcategory})"
    if object_type:
        return object_type
    return pin_category


def deduplicate_variables(variables: Iterable[VariableInfo]) -> List[VariableInfo]:
    """Coalesce duplicate variable definitions."""

    merged: dict[str, VariableInfo] = {}
    for variable in variables:
        existing = merged.get(variable.name)
        if not existing:
            merged[variable.name] = variable
            continue
        merged[variable.name] = merge_variable(existing, variable)
    return list(merged.values())


def merge_variable(primary: VariableInfo, secondary: VariableInfo) -> VariableInfo:
    """Merge two variable definitions prioritising populated fields."""

    return VariableInfo(
        name=primary.name,
        category=primary.category or secondary.category,
        var_type=primary.var_type or secondary.var_type,
        container=primary.container or secondary.container,
        subtype=primary.subtype or secondary.subtype,
    )
