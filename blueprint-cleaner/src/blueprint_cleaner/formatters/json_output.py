"""JSON serialization for blueprint reports.

Provides functions to convert structured blueprint data into JSON format.
"""

from __future__ import annotations

import json

from ..models import (
    BlueprintReport,
    FunctionSynopsis,
    GraphSummary,
    VariableInfo,
    WidgetBinding,
    WidgetVariable,
)


def render_json_output(report: BlueprintReport) -> str:
    """Serialize blueprint report to JSON.

    @param report: Structured blueprint data.
    @return: JSON string with indentation.
    """
    return json.dumps(report_to_dict(report), indent=2)


def report_to_dict(report: BlueprintReport) -> dict:
    """Convert blueprint report into primitive types.

    @param report: Blueprint report to convert.
    @return: Dictionary with serializable values.
    """
    return {
        "name": report.metadata.name,
        "parent_class": report.metadata.parent_class,
        "cpp_class": report.metadata.cpp_class_name,
        "variables": [variable_to_dict(variable) for variable in report.variables],
        "graphs": [graph_to_dict(graph) for graph in report.graphs],
        "functions": [function_to_dict(fn) for fn in report.functions],
        "widget_bindings": [
            binding_to_dict(binding) for binding in report.widget_bindings
        ],
        "widget_animations": report.widget_animations,
        "widget_variables": [
            widget_variable_to_dict(item) for item in report.widget_variables
        ],
    }


def graph_to_dict(graph: GraphSummary) -> dict:
    """Serialize graph summary to dictionary.

    @param graph: Graph summary to convert.
    @return: Dictionary representation.
    """
    return {
        "name": graph.name,
        "category": graph.category,
        "entry_points": sorted(graph.entry_points),
        "calls": sorted(graph.calls),
        "reads": sorted(graph.reads),
        "writes": sorted(graph.writes),
        "comments": graph.comments,
        "node_types": dict(graph.node_types),
    }


def variable_to_dict(variable: VariableInfo) -> dict:
    """Serialize variable description to dictionary.

    @param variable: Variable information to convert.
    @return: Dictionary representation.
    """
    return {
        "name": variable.name,
        "category": variable.category,
        "type": variable.var_type,
        "container": variable.container,
        "subtype": variable.subtype,
    }


def function_to_dict(function: FunctionSynopsis) -> dict:
    """Serialize function synopsis to dictionary."""

    return {
        "name": function.name,
        "display_name": function.display_name,
        "category": function.category,
        "entry_points": function.entry_points,
        "calls": function.calls,
        "reads": function.reads,
        "writes": function.writes,
        "description": function.description,
        "access": function.access,
        "is_event": function.is_event,
    }


def binding_to_dict(binding: WidgetBinding) -> dict:
    """Serialize widget binding to dictionary."""

    return {
        "widget": binding.widget_name,
        "property": binding.property_name,
        "function": binding.function_name,
    }


def widget_variable_to_dict(variable: WidgetVariable) -> dict:
    """Serialize widget variable to dictionary."""

    return {
        "name": variable.name,
        "guid": variable.guid,
    }
