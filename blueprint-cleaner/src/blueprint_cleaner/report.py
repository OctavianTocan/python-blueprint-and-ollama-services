"""Blueprint report construction."""

from __future__ import annotations

from .analysis import build_function_synopses
from .graphs import summarize_graphs
from .metadata import build_metadata
from .models import BlueprintReport
from .variables import extract_variables
from .widget_data import (
    extract_widget_animations,
    extract_widget_bindings,
    extract_widget_variables,
)


def build_blueprint_report(content: str, debug: bool = False) -> BlueprintReport:
    """Parse blueprint text into a structured report."""

    metadata = build_metadata(content)
    variables = extract_variables(content)
    graphs = summarize_graphs(content, debug)
    functions = build_function_synopses(graphs)
    widget_bindings = extract_widget_bindings(content)
    widget_animations = extract_widget_animations(content)
    widget_variables = extract_widget_variables(content)
    return BlueprintReport(
        metadata=metadata,
        variables=variables,
        graphs=graphs,
        functions=functions,
        widget_bindings=widget_bindings,
        widget_animations=widget_animations,
        widget_variables=widget_variables,
    )
