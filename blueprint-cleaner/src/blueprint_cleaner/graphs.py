"""Graph summarization orchestration.

Coordinates parsing of graph blocks and construction of graph summaries
from blueprint text.
"""

from __future__ import annotations

from typing import List

from .models import GraphSummary
from .parsers.block_extraction import collect_graph_blocks, collect_node_blocks
from .parsers.graph_classification import classify_graph_category
from .parsers.node_parsing import (
    classify_node_kind,
    extract_custom_event_name,
    extract_function_calls,
    extract_function_entry_name,
    extract_node_comments,
    extract_variable_names,
)


def summarize_graphs(content: str, debug: bool) -> List[GraphSummary]:
    """Build summaries for each graph embedded in the blueprint.

    @param content: Full blueprint text.
    @param debug: Enable debug output.
    @return: List of graph summaries sorted by name.
    """
    lines = content.splitlines()
    blocks = collect_graph_blocks(lines)
    summaries = [summarize_graph_block(block) for block in blocks]

    if debug:
        print(f"Discovered {len(summaries)} graphs.")

    return sorted(summaries, key=lambda graph: graph.name)


def summarize_graph_block(block) -> GraphSummary:
    """Convert graph block into structured summary.

    @param block: Graph block with name and lines.
    @return: Graph summary with entry points, calls, reads, writes.
    """
    from toolkit.collections import dedupe_preserve_order

    summary = GraphSummary(
        name=block.name,
        category=classify_graph_category(block),
    )

    for node in collect_node_blocks(block):
        parse_node_block(node, summary)

    if not summary.entry_points:
        summary.entry_points.add(block.name)

    summary.comments = dedupe_preserve_order(summary.comments)
    return summary


def parse_node_block(node, summary: GraphSummary) -> None:
    """Update graph summary metrics based on node block.

    @param node: Node block to parse.
    @param summary: Graph summary to update.
    """
    kind = classify_node_kind(node.name)
    summary.node_types[kind] += 1

    text = "\n".join(node.lines)

    # Extract entry points
    custom_event = extract_custom_event_name(kind, text)
    if custom_event:
        summary.entry_points.add(custom_event)

    function_entry = extract_function_entry_name(kind, text)
    if function_entry:
        summary.entry_points.add(function_entry)

    # Extract function calls
    summary.calls.update(extract_function_calls(text))

    # Extract variable accesses
    if kind in {"VariableSet", "SetVariableOnPersistentFrame"}:
        summary.writes.update(extract_variable_names(text))

    if kind == "VariableGet":
        summary.reads.update(extract_variable_names(text))

    # Extract comments
    for comment in extract_node_comments(text):
        summary.comments.append(comment)
