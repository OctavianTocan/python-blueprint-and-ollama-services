"""Markdown rendering for blueprint reports.

Handles conversion of structured blueprint data into markdown format
with sections for summary, variables, and graphs.
"""

from __future__ import annotations

from typing import List, Sequence

from ..models import (
    BlueprintReport,
    FunctionSynopsis,
    GraphSummary,
    VariableInfo,
    WidgetBinding,
    WidgetVariable,
)


def format_as_markdown(report: BlueprintReport) -> str:
    """Compose full markdown document from blueprint report.

    @param report: Structured blueprint data.
    @return: Complete markdown document string.
    """
    sections = [
        render_summary_section(report),
        render_variable_section(report.variables),
        render_widget_variable_section(report.widget_variables),
        render_widget_bindings_section(report.widget_bindings),
        render_widget_animation_section(report.widget_animations),
        render_function_section(report.functions),
        render_graph_section(report.graphs),
    ]
    return "\n\n".join(section for section in sections if section)


def render_summary_section(report: BlueprintReport) -> str:
    """Create summary section for markdown report.

    @param report: Blueprint report with metadata and metrics.
    @return: Formatted summary markdown.
    """
    lines = [f"# Blueprint: {report.metadata.name}", ""]

    if report.metadata.parent_class:
        lines.append(f"*Parent Class:* `{report.metadata.parent_class}`")
        lines.append("")

    event_count = count_event_graphs(report.graphs)
    unique_calls = count_unique_function_calls(report.graphs)

    lines.append("## At a glance")
    lines.append(f"- Variables: {len(report.variables)}")
    lines.append(f"- Graphs: {len(report.graphs)}")
    lines.append(f"- Event Handlers: {event_count}")
    lines.append(f"- Unique Calls: {unique_calls}")

    return "\n".join(lines)


def count_event_graphs(graphs: Sequence[GraphSummary]) -> int:
    """Count graphs categorized as events.

    @param graphs: Graph summaries to count.
    @return: Number of event-oriented graphs.
    """
    return sum(1 for graph in graphs if "Event" in graph.category)


def count_unique_function_calls(graphs: Sequence[GraphSummary]) -> int:
    """Count distinct function calls across all graphs.

    @param graphs: Graph summaries containing call data.
    @return: Number of unique function call strings.
    """
    return len({call for graph in graphs for call in graph.calls})


def render_variable_section(variables: Sequence[VariableInfo]) -> str:
    """Render variable details as markdown table.

    @param variables: Variable information records.
    @return: Markdown table or empty string if no variables.
    """
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


def render_widget_variable_section(variables: Sequence[WidgetVariable]) -> str:
    """Render widget component variables as markdown table."""

    if not variables:
        return ""

    lines = [
        "## Widget Variables",
        "| Name | GUID |",
        "| --- | --- |",
    ]

    for variable in variables:
        guid = variable.guid or "—"
        lines.append(f"| `{variable.name}` | {guid} |")

    return "\n".join(lines)


def render_widget_bindings_section(bindings: Sequence[WidgetBinding]) -> str:
    """Render widget bindings as bullet list."""

    if not bindings:
        return ""

    lines: List[str] = ["## UMG Bindings"]

    for binding in bindings:
        lines.append(
            f"- `{binding.widget_name}` → `{binding.property_name}` via `{binding.function_name}`"
        )

    return "\n".join(lines)


def render_widget_animation_section(animations: Sequence[str]) -> str:
    """Render widget animation names."""

    if not animations:
        return ""

    lines: List[str] = ["## UMG Animations"]
    for name in animations:
        lines.append(f"- `{name}`")

    return "\n".join(lines)


def build_variable_row(variable: VariableInfo) -> str:
    """Build markdown table row for a variable.

    @param variable: Variable information.
    @return: Markdown table row string.
    """
    type_label = variable.var_type or "Unknown"
    notes = collect_variable_notes(variable)
    note_text = ", ".join(notes) if notes else "—"

    return f"| `{variable.name}` | {type_label} | {variable.category} | {note_text} |"


def collect_variable_notes(variable: VariableInfo) -> List[str]:
    """Gather supplementary notes about a variable.

    @param variable: Variable information.
    @return: List of note strings (container, subtype).
    """
    notes: List[str] = []
    if variable.container:
        notes.append(variable.container)
    if variable.subtype and variable.subtype not in (variable.var_type or ""):
        notes.append(variable.subtype)
    return notes


def render_graph_section(graphs: Sequence[GraphSummary]) -> str:
    """Render graph insights grouped by category.

    @param graphs: Graph summaries to render.
    @return: Markdown section with categorized graphs.
    """
    if not graphs:
        return ""

    lines: List[str] = ["## Graphs"]
    grouped = group_graphs_by_category(graphs)

    for category, items in grouped.items():
        lines.append(f"### {category}")
        for graph in items:
            lines.extend(render_graph_item(graph))
        lines.append("")

    return "\n".join(line for line in lines if line)


def group_graphs_by_category(
    graphs: Sequence[GraphSummary],
) -> dict[str, List[GraphSummary]]:
    """Group graphs by category label.

    @param graphs: Graph summaries to group.
    @return: Dictionary mapping category to sorted graph list.
    """
    grouped: dict[str, List[GraphSummary]] = {}
    for graph in graphs:
        grouped.setdefault(graph.category, []).append(graph)

    for bucket in grouped.values():
        bucket.sort(key=lambda item: item.name)

    return dict(sorted(grouped.items(), key=lambda pair: pair[0]))


def render_graph_item(graph: GraphSummary) -> List[str]:
    """Build markdown bullet lines for a single graph.

    @param graph: Graph summary to render.
    @return: List of markdown lines.
    """
    from toolkit.formatting import format_inline_list
    from collections import Counter

    lines = [f"- **{graph.name}**"]

    if graph.entry_points:
        entry_text = format_inline_list(sorted(graph.entry_points), limit=6)
        lines.append(f"  - Entry Points: {entry_text}")

    if graph.calls:
        call_text = format_inline_list(sorted(graph.calls), limit=6)
        lines.append(f"  - Calls: {call_text}")

    if graph.reads:
        read_text = format_inline_list(sorted(graph.reads), limit=6)
        lines.append(f"  - Reads: {read_text}")

    if graph.writes:
        write_text = format_inline_list(sorted(graph.writes), limit=6)
        lines.append(f"  - Writes: {write_text}")

    if graph.comments:
        lines.extend(render_graph_comments(graph.comments, limit=3))

    if graph.node_types:
        node_mix = render_node_mix(graph.node_types)
        if node_mix:
            lines.append(f"  - Node Mix: {node_mix}")

    return lines


def render_function_section(functions: Sequence[FunctionSynopsis]) -> str:
    """Render function synopses with concise descriptions.

    @param functions: Function synopsis collection.
    @return: Markdown section listing logic flows.
    """
    if not functions:
        return ""

    lines: List[str] = ["## Logic Flows"]
    for synopsis in functions:
        lines.append(f"### {synopsis.display_name} ({synopsis.category})")
        lines.append(f"{synopsis.description}")

        if synopsis.calls:
            call_text = ", ".join(synopsis.calls)
            lines.append(f"- Calls: {call_text}")
        if synopsis.reads:
            read_text = ", ".join(synopsis.reads)
            lines.append(f"- Reads: {read_text}")
        if synopsis.writes:
            write_text = ", ".join(synopsis.writes)
            lines.append(f"- Writes: {write_text}")
        if synopsis.entry_points:
            entry_text = ", ".join(synopsis.entry_points)
            lines.append(f"- Entry Points: {entry_text}")

        lines.append("")

    return "\n".join(line for line in lines if line)


def render_graph_comments(comments: Sequence[str], limit: int) -> List[str]:
    """Render developer comments for a graph.

    @param comments: Comment strings to render.
    @param limit: Maximum number of comments to display.
    @return: List of markdown comment lines.
    """
    if not comments:
        return []

    lines = ["  - Notes:"]
    for comment in comments[:limit]:
        lines.append(f"    - {comment}")

    remaining = len(comments) - limit
    if remaining > 0:
        lines.append(f"    - … (+{remaining} more)")

    return lines


def render_node_mix(counter: dict[str, int]) -> str | None:
    """Summarize node distribution for a graph.

    @param counter: Node type frequency map.
    @return: Formatted summary string or None.
    """
    from collections import Counter

    if not counter:
        return None

    parts = [f"{kind} ×{count}" for kind, count in Counter(counter).most_common(5)]
    return ", ".join(parts)
