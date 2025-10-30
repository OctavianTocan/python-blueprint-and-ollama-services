"""Data structures representing blueprint output artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict

from .models import BlueprintReport, FunctionSynopsis


@dataclass
class BlueprintArtifacts:
    """Aggregate outputs generated from a blueprint report."""

    report: BlueprintReport
    markdown: str
    json_text: str
    ai_summary: str
    cpp_header: str
    cpp_source: str
    functions: list[FunctionSynopsis] = field(default_factory=list)

    def to_bundle(self) -> Dict[str, object]:
        """Convert artifacts into a JSON-serialisable dictionary."""

        payload = json.loads(self.json_text)
        payload.setdefault("functions", [self._function_to_dict(fn) for fn in self.functions])

        return {
            "metadata": {
                "name": self.report.metadata.name,
                "parent_class": self.report.metadata.parent_class,
                "variables": len(self.report.variables),
                "graphs": len(self.report.graphs),
            },
            "markdown": self.markdown,
            "json": payload,
            "ai_summary": self.ai_summary,
            "cpp": {
                "header": self.cpp_header,
                "source": self.cpp_source,
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