"""Graph parsing and summarisation."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, List, Sequence

from .models import GraphBlock, GraphSummary, NodeBlock
from .utils import (
    COMMENT_RE,
    FUNCTION_REF_RE,
    VARIABLE_REF_RE,
    dedupe_preserve_order,
    extract_class_tail,
    find_first,
    parse_metadata_map,
)


def summarize_graphs(content: str, debug: bool) -> List[GraphSummary]:
    """Build summaries for each graph embedded in the blueprint."""

    lines = content.splitlines()
    blocks = collect_graph_blocks(lines)
    summaries = [summarize_graph_block(block) for block in blocks]
    if debug:
        print(f"Discovered {len(summaries)} graphs.")
    return sorted(summaries, key=lambda graph: graph.name)


def collect_graph_blocks(lines: Sequence[str]) -> List[GraphBlock]:
    """Collect named EdGraph blocks from the blueprint."""

    blocks: List[GraphBlock] = []
    stack: List[tuple[int, str]] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Begin Object Name="):
            name = extract_name_from_line(line)
            stack.append((index, name or ""))
        elif stripped == "End Object" and stack:
            start_index, name = stack.pop()
            if not name or name.startswith("K2Node_"):
                continue
            block_lines = lines[start_index:index + 1]
            if is_graph_block(block_lines):
                blocks.append(GraphBlock(name=name, lines=block_lines))
    return blocks


def extract_name_from_line(line: str) -> str | None:
    """Pull the Name attribute from a Begin Object line."""

    match = find_first(r'Name="([^"]+)"', line)
    return match


def is_graph_block(lines: Sequence[str]) -> bool:
    """Determine whether a named block represents an EdGraph."""

    return any("Schema=Class" in line for line in lines) and any("Nodes(" in line for line in lines)


def summarize_graph_block(block: GraphBlock) -> GraphSummary:
    """Convert a graph block into a structured summary."""

    summary = GraphSummary(name=block.name, category=classify_graph_category(block))
    for node in collect_node_blocks(block):
        parse_node_block(node, summary)
    if not summary.entry_points:
        summary.entry_points.add(block.name)
    summary.comments = dedupe_preserve_order(summary.comments)
    return summary


def classify_graph_category(block: GraphBlock) -> str:
    """Assign a human-readable category to a graph."""

    name = block.name
    if name == "EventGraph":
        return "Event Graph"
    if name.startswith("Event "):
        return "Event Handler"
    if name.startswith("CGraph "):
        return "Composite Graph"
    if any("K2Node_FunctionEntry" in line for line in block.lines):
        return "Function Graph"
    return "Utility Graph"


def collect_node_blocks(block: GraphBlock) -> Iterable[NodeBlock]:
    """Iterate over node definitions inside a graph block."""

    lines = list(block.lines)
    stack: List[tuple[int, str, str]] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Begin Object"):
            name = extract_name_from_line(line) or ""
            stack.append((index, line, name))
        elif stripped == "End Object" and stack:
            start, header, name = stack.pop()
            if name.startswith("K2Node_") or name.startswith("EdGraphNode_Comment"):
                yield NodeBlock(name=name, header=header, lines=lines[start:index + 1])


def classify_node_kind(node_name: str) -> str:
    """Reduce a node name to its semantic kind."""

    if node_name.startswith("K2Node_"):
        tail = node_name[len("K2Node_"):]
        return tail.split('_')[0]
    if node_name.startswith("EdGraphNode_Comment"):
        return "Comment"
    return node_name


def parse_node_block(node: NodeBlock, summary: GraphSummary) -> None:
    """Update graph summary metrics based on a node block."""

    kind = classify_node_kind(node.name)
    summary.node_types[kind] += 1
    text = "\n".join(node.lines)
    summary.entry_points.update(parse_custom_events(kind, text))
    summary.entry_points.update(parse_function_entries(kind, text))
    summary.calls.update(parse_function_references(text))
    if kind in {"VariableSet", "SetVariableOnPersistentFrame"}:
        summary.writes.update(parse_variable_references(text))
    if kind == "VariableGet":
        summary.reads.update(parse_variable_references(text))
    add_comments_from_text(text, summary)


def parse_custom_events(kind: str, text: str) -> set[str]:
    """Extract custom event names when present."""

    if kind != "CustomEvent":
        return set()
    name = find_first(r'CustomFunctionName="([^"]+)"', text)
    return {name} if name else set()


def parse_function_entries(kind: str, text: str) -> set[str]:
    """Extract generated function entry names."""

    if kind != "FunctionEntry":
        return set()
    name = find_first(r'CustomGeneratedFunctionName="([^"]+)"', text)
    return {name} if name else set()


def parse_function_references(text: str) -> set[str]:
    """Extract formatted function call references from node text."""

    references: set[str] = set()
    for chunk in FUNCTION_REF_RE.findall(text):
        metadata = parse_metadata_map(chunk)
        name = metadata.get("MemberName")
        if not name:
            continue
        if metadata.get("bSelfContext", "").lower() == "true":
            references.add(f"self.{name}")
            continue
        parent = metadata.get("MemberParent") or metadata.get("Outer")
        parent_name = extract_class_tail(parent)
        references.add(f"{parent_name}::{name}" if parent_name else name)
    return references


def parse_variable_references(text: str) -> set[str]:
    """Extract variable names referenced by a node."""

    names: set[str] = set()
    for chunk in VARIABLE_REF_RE.findall(text):
        metadata = parse_metadata_map(chunk)
        name = metadata.get("MemberName")
        if name:
            names.add(name)
    return names


def add_comments_from_text(text: str, summary: GraphSummary) -> None:
    """Collect developer comments embedded in a node."""

    for raw_comment in COMMENT_RE.findall(text):
        comment = normalize_comment(raw_comment)
        if comment:
            summary.comments.append(comment)


def normalize_comment(comment: str) -> str:
    """Sanitise blueprint comment text."""

    cleaned = comment.replace("\\r", " ").replace("\\n", " ")
    cleaned = cleaned.replace("\\'", "'").replace('\\"', '"')
    return " ".join(cleaned.split()).strip()
