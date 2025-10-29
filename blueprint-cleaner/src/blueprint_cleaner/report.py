"""Blueprint report construction."""

from __future__ import annotations

from .graphs import summarize_graphs
from .metadata import build_metadata
from .models import BlueprintReport
from .variables import extract_variables


def build_blueprint_report(content: str, debug: bool = False) -> BlueprintReport:
    """Parse blueprint text into a structured report."""

    metadata = build_metadata(content)
    variables = extract_variables(content)
    graphs = summarize_graphs(content, debug)
    return BlueprintReport(metadata=metadata, variables=variables, graphs=graphs)
