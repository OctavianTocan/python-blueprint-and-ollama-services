"""Post-processing helpers for blueprint analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence

from toolkit.formatting import format_inline_list

from .models import FunctionSynopsis, GraphSummary


@dataclass
class SynopsisConfig:
    """Configuration for deriving function synopses."""

    max_items: int = 6


def build_function_synopses(
    graphs: Sequence[GraphSummary],
    config: SynopsisConfig | None = None,
) -> List[FunctionSynopsis]:
    """Construct function synopses from graph summaries.

    @param graphs: Parsed graph summaries.
    @param config: Optional configuration for list truncation.
    @return: List of function synopses sorted by name.
    """
    cfg = config or SynopsisConfig()
    synopses: List[FunctionSynopsis] = []

    for graph in graphs:
        display_name = graph.name.replace("ExecuteUbergraph_", "Execute ")
        synopses.append(
            FunctionSynopsis(
                name=graph.name,
                display_name=display_name,
                category=graph.category,
                entry_points=_sorted_slice(graph.entry_points, cfg.max_items),
                calls=_sorted_slice(graph.calls, cfg.max_items),
                reads=_sorted_slice(graph.reads, cfg.max_items),
                writes=_sorted_slice(graph.writes, cfg.max_items),
                description=_summarise_graph(graph),
                access=_infer_access(graph),
                is_event="Event" in graph.category,
            )
        )

    return sorted(synopses, key=lambda synopsis: synopsis.name)


def _sorted_slice(items: Iterable[str], limit: int) -> List[str]:
    """Return sorted list truncated to the specified limit."""

    return list(sorted(items))[:limit]


def _infer_access(graph: GraphSummary) -> str:
    """Infer C++ access level based on graph category."""

    if graph.category in {"Event Graph", "Event Handler"}:
        return "Public"
    if graph.category == "Composite Graph":
        return "Protected"
    return "Public"


def _summarise_graph(graph: GraphSummary) -> str:
    """Generate short natural-language description for a graph."""

    parts: List[str] = []

    if graph.entry_points:
        entry_text = format_inline_list(sorted(graph.entry_points), limit=4)
        parts.append(f"Entry points: {entry_text}.")

    if graph.calls:
        call_text = format_inline_list(sorted(graph.calls), limit=4)
        parts.append(f"Invokes {call_text}.")

    if graph.reads:
        read_text = format_inline_list(sorted(graph.reads), limit=4)
        parts.append(f"Reads {read_text}.")

    if graph.writes:
        write_text = format_inline_list(sorted(graph.writes), limit=4)
        parts.append(f"Writes {write_text}.")

    if graph.comments:
        note = graph.comments[0]
        parts.append(f"Notes: {note}.")

    if not parts:
        return "Logic flow extracted from blueprint graph."

    return " ".join(parts)
