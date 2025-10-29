"""Variable metadata parsing into structured records.

Transforms raw variable entry text into typed variable information objects
with category, type, and container details.
"""

from __future__ import annotations

import re
from typing import Optional, Tuple

from ..models import VariableInfo


CONTAINER_RE = re.compile(r"ContainerType=([A-Za-z]+)")


def parse_variable_entry(entry: str) -> Optional[VariableInfo]:
    """Translate raw variable metadata into structured record.

    @param entry: Raw variable metadata text.
    @return: Structured variable info or None if name not found.
    """
    name = extract_variable_name(entry)
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


def extract_variable_name(entry: str) -> Optional[str]:
    """Extract variable name from metadata entry.

    @param entry: Variable metadata text.
    @return: Variable name or None if not found.
    """
    match = re.search(r'FriendlyName="([^"]+)"', entry)
    if match:
        return match.group(1)
    match = re.search(r'VarName="([^"]+)"', entry)
    return match.group(1) if match else None


def parse_category(entry: str) -> Optional[str]:
    """Extract display category label from metadata.

    @param entry: Variable metadata text.
    @return: Category name or None.
    """
    match = re.search(r'Category=NSLOCTEXT\([^,]+,[^,]+,"([^"]+)"\)', entry)
    if match:
        return match.group(1)
    match = re.search(r'Category="([^"]+)"', entry)
    return match.group(1) if match else None


def parse_pin_type(entry: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract pin category information from variable entry.

    @param entry: Variable metadata text.
    @return: Tuple of (category, subcategory).
    """
    category_match = re.search(r'PinCategory="([^"]+)"', entry)
    subcategory_match = re.search(r'PinSubCategory="([^"]+)"', entry)

    category = category_match.group(1) if category_match else None
    subcategory = subcategory_match.group(1) if subcategory_match else None

    return category, subcategory


def parse_container_type(entry: str) -> Optional[str]:
    """Read container semantics for a variable.

    @param entry: Variable metadata text.
    @return: Container type (e.g., "Array", "Set") or None.
    """
    match = CONTAINER_RE.search(entry)
    if not match:
        return None
    value = match.group(1)
    return None if value.lower() == "none" else value


def parse_subcategory_object(entry: str) -> Optional[str]:
    """Resolve object or struct referenced by variable type.

    @param entry: Variable metadata text.
    @return: Cleaned class/struct name or None.
    """
    patterns = [
        r'PinSubCategoryObject=([^,]+)',
        r'SubCategoryObject=([^,]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, entry)
        if match:
            from toolkit.text_parsing import extract_tail_identifier
            raw_value = match.group(1).rstrip(')')
            return extract_tail_identifier(raw_value)

    return None


def compose_type_label(
    pin_category: Optional[str],
    pin_subcategory: Optional[str],
    object_type: Optional[str],
) -> Optional[str]:
    """Build human-readable type label from pin metadata.

    @param pin_category: Primary type category.
    @param pin_subcategory: Type subcategory.
    @param object_type: Referenced object/struct type.
    @return: Formatted type string or None.
    """
    if pin_category and object_type:
        return f"{pin_category}<{object_type}>"
    if pin_category and pin_subcategory:
        return f"{pin_category} ({pin_subcategory})"
    if object_type:
        return object_type
    return pin_category
