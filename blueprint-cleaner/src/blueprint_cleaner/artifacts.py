"""Data structures representing blueprint output artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict

from .models import BlueprintReport, FunctionSynopsis

AVAILABLE_FORMATS = [
    "markdown",
    "json",
    "summary",
    "bundle",
    "cpp-header",
    "cpp-source",
]


@dataclass
class BlueprintArtifacts:
    """Aggregate outputs generated from a blueprint report."""

    report: BlueprintReport
    markdown: str
    json_text: str
    ai_summary: str
    cpp_header: str
    cpp_source: str
    cpp_header_path: str
    cpp_source_path: str
    functions: list[FunctionSynopsis] = field(default_factory=list)

    def to_bundle(self) -> Dict[str, object]:
        """Convert artifacts into a JSON-serialisable dictionary."""

        payload = json.loads(self.json_text)
        payload.setdefault(
            "functions", [self._function_to_dict(fn) for fn in self.functions]
        )

        return {
            "metadata": {
                "name": self.report.metadata.name,
                "parent_class": self.report.metadata.parent_class,
                "cpp_class": self.report.metadata.cpp_class_name,
                "variables": len(self.report.variables),
                "graphs": len(self.report.graphs),
                "formats": AVAILABLE_FORMATS,
            },
            "markdown": self.markdown,
            "json": payload,
            "ai_summary": self.ai_summary,
            "cpp": {
                "header": self.cpp_header,
                "source": self.cpp_source,
                "header_path": self.cpp_header_path,
                "source_path": self.cpp_source_path,
            },
        }

    @staticmethod
    def _function_to_dict(function: FunctionSynopsis) -> Dict[str, object]:
        """Serialize function synopsis for bundles."""

        return {
            "name": function.name,
            "display_name": function.display_name,
            "category": function.category,
            "entry_points": function.entry_points,
            "calls": function.calls,
            "reads": function.reads,
            "writes": function.writes,
            "description": function.description,
            "access": function.access,
            "is_event": function.is_event,
        }
