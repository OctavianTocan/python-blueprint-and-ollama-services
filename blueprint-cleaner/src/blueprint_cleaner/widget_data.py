"""Widget-specific extraction utilities for blueprint reports.

Provides helpers to parse bindings, animations, and widget component variables
from WidgetBlueprint exports.
"""

from __future__ import annotations

import re
from typing import Iterable, List

from toolkit.text_parsing import extract_tail_identifier

from .models import WidgetBinding, WidgetVariable
from .parsers.variable_collection import collect_variable_entries

_BINDING_OBJECT_RE = re.compile(r'ObjectName="([^"]+)"')
_BINDING_PROPERTY_RE = re.compile(r'PropertyName="([^"]+)"')
_BINDING_FUNCTION_RE = re.compile(r'FunctionName="([^"]+)"')
_WIDGET_VARIABLE_RE = re.compile(r'\("([^"]+)",\s*([^\)]+)\)')
_ANIMATION_RE = re.compile(r'Animations\(\d+\)="([^"]+)"')


def extract_widget_bindings(content: str) -> List[WidgetBinding]:
    """Extract widget bindings from blueprint text."""

    bindings: List[WidgetBinding] = []
    for entry in collect_variable_entries(content, "Bindings"):
        widget_name = _find_first(_BINDING_OBJECT_RE, entry)
        property_name = _find_first(_BINDING_PROPERTY_RE, entry)
        function_name = _find_first(_BINDING_FUNCTION_RE, entry)
        if not widget_name or not property_name or not function_name:
            continue
        bindings.append(
            WidgetBinding(
                widget_name=widget_name,
                property_name=property_name,
                function_name=function_name,
            )
        )

    bindings.sort(
        key=lambda item: (item.widget_name.lower(), item.property_name.lower())
    )
    return bindings


def extract_widget_animations(content: str) -> List[str]:
    """Extract widget animation names from blueprint text."""

    names = {
        extracted
        for raw in _ANIMATION_RE.findall(content)
        for extracted in [_clean_animation_name(raw)]
        if extracted
    }
    return sorted(names, key=str.lower)


def extract_widget_variables(content: str) -> List[WidgetVariable]:
    """Extract widget component variables declared on the blueprint."""

    discovered: dict[str, WidgetVariable] = {}
    for entry in collect_variable_entries(content, "WidgetVariableNameToGuidMap"):
        for name, guid in _WIDGET_VARIABLE_RE.findall(entry):
            cleaned_guid = guid.strip().rstrip(")")
            record = WidgetVariable(name=name, guid=cleaned_guid or None)
            discovered[name] = record

    return _sort_widget_variables(discovered.values())


def _clean_animation_name(raw: str) -> str | None:
    """Convert full animation export path to display name."""

    name = extract_tail_identifier(raw)
    if not name:
        return None
    return name.split(":")[-1]


def _sort_widget_variables(variables: Iterable[WidgetVariable]) -> List[WidgetVariable]:
    """Order widget variables alphabetically for stable output."""

    return sorted(variables, key=lambda item: item.name.lower())


def _find_first(pattern: re.Pattern[str], text: str) -> str | None:
    """Return first regex capture group or None."""

    match = pattern.search(text)
    return match.group(1) if match else None
