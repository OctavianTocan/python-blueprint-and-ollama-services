"""Data models for blueprint summaries."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Set


@dataclass
class BlueprintMetadata:
    """Metadata describing the blueprint asset."""

    name: str
    parent_class: Optional[str]


@dataclass
class VariableInfo:
    """Details about a blueprint variable."""

    name: str
    category: str
    var_type: Optional[str] = None
    container: Optional[str] = None
    subtype: Optional[str] = None


@dataclass
class GraphBlock:
    """Raw graph block extracted from the blueprint."""

    name: str
    lines: Sequence[str]


@dataclass
class NodeBlock:
    """Raw node block inside a graph."""

    name: str
    header: str
    lines: Sequence[str]


@dataclass
class GraphSummary:
    """Aggregated information about a graph."""

    name: str
    category: str
    entry_points: Set[str] = field(default_factory=set)
    calls: Set[str] = field(default_factory=set)
    reads: Set[str] = field(default_factory=set)
    writes: Set[str] = field(default_factory=set)
    comments: List[str] = field(default_factory=list)
    node_types: Counter = field(default_factory=Counter)


@dataclass
class FunctionSynopsis:
    """Structured narrative built from a graph summary."""

    name: str
    display_name: str
    category: str
    entry_points: List[str]
    calls: List[str]
    reads: List[str]
    writes: List[str]
    description: str
    access: str = "Public"
    is_event: bool = False


@dataclass
class BlueprintReport:
    """Top-level summary produced for a blueprint."""

    metadata: BlueprintMetadata
    variables: List[VariableInfo]
    graphs: List[GraphSummary]
    functions: List[FunctionSynopsis] = field(default_factory=list)
