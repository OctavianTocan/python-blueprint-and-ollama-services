"""Block extraction for graphs within blueprint files.

Provides functions to locate and extract named graph blocks and their
constituent node blocks from blueprint text.
"""

from __future__ import annotations

from typing import List, Sequence

from ..models import GraphBlock, NodeBlock


def collect_graph_blocks(lines: Sequence[str]) -> List[GraphBlock]:
    """Collect named EdGraph blocks from blueprint text.

    @param lines: Blueprint file split into individual lines.
    @return: List of graph blocks with names and content.
    """
    blocks: List[GraphBlock] = []
    stack: List[tuple[int, str]] = []

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Begin Object Name="):
            name = extract_name_from_begin_object(line)
            stack.append((index, name or ""))
        elif stripped == "End Object" and stack:
            start_index, name = stack.pop()
            if should_skip_block(name):
                continue
            block_lines = lines[start_index : index + 1]
            if is_graph_block(block_lines):
                blocks.append(GraphBlock(name=name, lines=block_lines))

    return blocks


def extract_name_from_begin_object(line: str) -> str | None:
    """Extract Name attribute from a Begin Object declaration.

    @param line: Line containing "Begin Object Name=...".
    @return: Extracted name or None if not found.
    """
    import re

    match = re.search(r'Name="([^"]+)"', line)
    return match.group(1) if match else None


def should_skip_block(name: str) -> bool:
    """Determine if a named block should be excluded from graph collection.

    @param name: Block name extracted from Begin Object.
    @return: True if block should be skipped (e.g., node-level blocks).
    """
    return not name or name.startswith("K2Node_")


def is_graph_block(lines: Sequence[str]) -> bool:
    """Check if block lines represent an EdGraph structure.

    @param lines: Block content lines.
    @return: True if block contains schema and nodes markers.
    """
    has_schema = any("Schema=Class" in line for line in lines)
    has_nodes = any("Nodes(" in line for line in lines)
    return has_schema and has_nodes


def collect_node_blocks(block: GraphBlock) -> list[NodeBlock]:
    """Extract node definitions from a graph block.

    @param block: Graph block containing node declarations.
    @return: List of node blocks with headers and content.
    """
    nodes: list[NodeBlock] = []
    lines = list(block.lines)
    stack: List[tuple[int, str, str]] = []

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Begin Object"):
            name = extract_name_from_begin_object(line) or ""
            stack.append((index, line, name))
        elif stripped == "End Object" and stack:
            start, header, name = stack.pop()
            if is_node_block(name):
                node_lines = lines[start : index + 1]
                nodes.append(NodeBlock(name=name, header=header, lines=node_lines))

    return nodes


def is_node_block(name: str) -> bool:
    """Check if a block name represents a graph node.

    @param name: Block name to evaluate.
    @return: True if name matches node patterns.
    """
    return name.startswith("K2Node_") or name.startswith("EdGraphNode_Comment")
