"""Variable extraction orchestration.

Coordinates collection and parsing of variable entries from blueprint text.
"""

from __future__ import annotations

from typing import Iterable, List

from .models import VariableInfo
from .parsers.variable_collection import collect_variable_entries
from .parsers.variable_parsing import parse_variable_entry


def extract_variables(content: str) -> List[VariableInfo]:
    """Parse variable declarations from blueprint text.

    @param content: Full blueprint text.
    @return: List of deduplicated variable records.
    """
    entries = collect_variable_entries(content, "VariablesDescriptions")
    entries.extend(collect_variable_entries(content, "NewVariables"))

    variables = [parse_variable_entry(entry) for entry in entries]
    filtered = [variable for variable in variables if variable]

    return deduplicate_variables(filtered)


def deduplicate_variables(variables: Iterable[VariableInfo]) -> List[VariableInfo]:
    """Coalesce duplicate variable definitions.

    @param variables: Variable records potentially containing duplicates.
    @return: List of merged unique variables.
    """
    merged: dict[str, VariableInfo] = {}

    for variable in variables:
        existing = merged.get(variable.name)
        if not existing:
            merged[variable.name] = variable
            continue
        merged[variable.name] = merge_variable(existing, variable)

    return list(merged.values())


def merge_variable(primary: VariableInfo, secondary: VariableInfo) -> VariableInfo:
    """Merge two variable definitions prioritizing populated fields.

    @param primary: First variable definition.
    @param secondary: Second variable definition.
    @return: Merged variable with filled fields.
    """
    return VariableInfo(
        name=primary.name,
        category=primary.category or secondary.category,
        var_type=primary.var_type or secondary.var_type,
        container=primary.container or secondary.container,
        subtype=primary.subtype or secondary.subtype,
    )
