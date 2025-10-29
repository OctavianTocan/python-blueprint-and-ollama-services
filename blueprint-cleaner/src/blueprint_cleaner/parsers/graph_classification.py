"""Graph categorization based on naming patterns and content.

Provides logic to classify graph blocks into semantic categories
like event handlers, function graphs, and utility graphs.
"""

from __future__ import annotations

from ..models import GraphBlock


def classify_graph_category(block: GraphBlock) -> str:
    """Assign semantic category to a graph block.

    @param block: Graph block to classify.
    @return: Human-readable category label.
    """
    name = block.name

    if name == "EventGraph":
        return "Event Graph"
    if name.startswith("Event "):
        return "Event Handler"
    if name.startswith("CGraph "):
        return "Composite Graph"
    if contains_function_entry(block):
        return "Function Graph"

    return "Utility Graph"


def contains_function_entry(block: GraphBlock) -> bool:
    """Check if graph contains function entry node.

    @param block: Graph block to inspect.
    @return: True if block contains K2Node_FunctionEntry.
    """
    return any("K2Node_FunctionEntry" in line for line in block.lines)
