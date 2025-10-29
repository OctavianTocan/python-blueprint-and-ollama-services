"""Output rendering for blueprint reports."""

from __future__ import annotations

import json
from collections import Counter
from typing import List, Sequence

from .models import BlueprintReport, GraphSummary, VariableInfo


def render_output(report: BlueprintReport, format_type: str) -> str:
    """Render the blueprint report in the requested format."""

    fmt = format_type.lower()
    if fmt == "json":
        return render_json_output(report)
    return format_as_markdown(report)


def format_as_markdown(report: BlueprintReport) -> str:
    """Compose the full markdown document."""

    sections = [
        render_summary_section(report),
        render_variable_section(report.variables),
        render_graph_section(report.graphs),
    ]
    return "\n\n".join(section for section in sections if section)


def render_summary_section(report: BlueprintReport) -> str:
    """Create the summary section for the markdown report."""

    lines = [f"# Blueprint: {report.metadata.name}", ""]
    if report.metadata.parent_class:
        lines.append(f"*Parent Class:* `{report.metadata.parent_class}`")
        lines.append("")
    event_count = sum(1 for graph in report.graphs if "Event" in graph.category)
    unique_calls = len({call for graph in report.graphs for call in graph.calls})
    lines.append("## At a glance")
    lines.append(f"- Variables: {len(report.variables)}")
    lines.append(f"- Graphs: {len(report.graphs)}")
    lines.append(f"- Event Handlers: {event_count}")
    lines.append(f"- Unique Calls: {unique_calls}")
    return "\n".join(lines)


def render_variable_section(variables: Sequence[VariableInfo]) -> str:
    """Render variable details as a markdown table."""

    if not variables:
        return ""
    lines = [
        "## Variables",
        "| Name | Type | Category | Notes |",
        "| --- | --- | --- | --- |",
    ]
    for variable in variables:
        lines.append(build_variable_row(variable))
    return "\n".join(lines)


def build_variable_row(variable: VariableInfo) -> str:
    """Build a markdown row for a variable."""

    type_label = variable.var_type or "Unknown"
    notes: List[str] = []
    if variable.container:
        notes.append(variable.container)
    if variable.subtype and variable.subtype not in type_label:
        notes.append(variable.subtype)
    note_text = ", ".join(notes) if notes else "—"
    return f"| `{variable.name}` | {type_label} | {variable.category} | {note_text} |"


def render_graph_section(graphs: Sequence[GraphSummary]) -> str:
    """Render graph insights grouped by category."""

    if not graphs:
        return ""
    lines: List[str] = ["## Graphs"]
    for category, items in group_graphs_by_category(graphs).items():
        lines.append(f"### {category}")
        for graph in items:
            lines.extend(render_graph_item(graph))
        lines.append("")
    return "\n".join(line for line in lines if line)


def group_graphs_by_category(graphs: Sequence[GraphSummary]) -> dict[str, List[GraphSummary]]:
    """Group graphs by their category label."""

    grouped: dict[str, List[GraphSummary]] = {}
    for graph in graphs:
        grouped.setdefault(graph.category, []).append(graph)
    for bucket in grouped.values():
        bucket.sort(key=lambda item: item.name)
    return dict(sorted(grouped.items(), key=lambda pair: pair[0]))


def render_graph_item(graph: GraphSummary) -> List[str]:
    """Build markdown bullet lines for a single graph."""

    lines = [f"- **{graph.name}**"]
    entry_line = render_graph_metric("Entry Points", sorted(graph.entry_points))
    if entry_line:
        lines.append(entry_line)
    call_line = render_graph_metric("Calls", sorted(graph.calls))
    if call_line:
        lines.append(call_line)
    read_line = render_graph_metric("Reads", sorted(graph.reads))
    if read_line:
        lines.append(read_line)
    write_line = render_graph_metric("Writes", sorted(graph.writes))
    if write_line:
        lines.append(write_line)
    comment_lines = render_graph_comments(graph.comments)
    if comment_lines:
        lines.extend(comment_lines)
    node_mix = render_node_mix(graph.node_types)
    if node_mix:
        lines.append(f"  - Node Mix: {node_mix}")
    return lines


def render_graph_metric(label: str, values: Sequence[str], limit: int = 6) -> str:
    """Format a bullet line for a graph metric."""

    if not values:
        return ""
    formatted = format_inline_list(values, limit)
    return f"  - {label}: {formatted}"


def render_graph_comments(comments: Sequence[str], limit: int = 3) -> List[str]:
    """Render developer comments for a graph."""

    if not comments:
        return []
    lines = ["  - Notes:"]
    for comment in comments[:limit]:
        lines.append(f"    - {comment}")
    remaining = len(comments) - limit
    if remaining > 0:
        lines.append(f"    - … (+{remaining} more)")
    return lines


def format_inline_list(values: Sequence[str], limit: int) -> str:
    """Format a sequence as an inline comma separated list."""

    display = list(values)[:limit]
    decorated = ", ".join(f"`{value}`" for value in display)
    remaining = len(values) - limit
    if remaining > 0:
        decorated += f", … (+{remaining} more)"
    return decorated


def render_node_mix(counter: dict[str, int]) -> str | None:
    """Summarise node distribution for a graph."""

    if not counter:
        return None
    parts = [f"{kind} ×{count}" for kind, count in Counter(counter).most_common(5)]
    return ", ".join(parts)


def render_json_output(report: BlueprintReport) -> str:
    """Serialise the blueprint report to JSON."""

    return json.dumps(report_to_dict(report), indent=2)


def report_to_dict(report: BlueprintReport) -> dict:
    """Convert a blueprint report into primitive types."""

    return {
        "name": report.metadata.name,
        "parent_class": report.metadata.parent_class,
        "variables": [variable_to_dict(variable) for variable in report.variables],
        "graphs": [graph_to_dict(graph) for graph in report.graphs],
    }


def graph_to_dict(graph: GraphSummary) -> dict:
    """Serialise a graph summary."""

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
    """Serialise a variable description."""

    return {
        "name": variable.name,
        "category": variable.category,
        "type": variable.var_type,
        "container": variable.container,
        "subtype": variable.subtype,
    }
