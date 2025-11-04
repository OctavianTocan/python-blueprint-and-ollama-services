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
    """Aggregate outputs generated from a blueprint report.

    This dataclass serves as a container for all artifacts produced during the
    blueprint generation process. It includes the original report, various text
    representations (markdown, JSON), AI-generated summaries, and C++ source files.

    Attributes:
        report: The original blueprint report containing metadata and structure information
        markdown: Markdown-formatted representation of the blueprint
        json_text: JSON string representation of the blueprint data
        ai_summary: AI-generated textual summary of the blueprint
        cpp_header: Generated C++ header file content
        cpp_source: Generated C++ source file content
        cpp_header_path: File path where the C++ header should be saved
        cpp_source_path: File path where the C++ source should be saved
        functions: List of function synopsis objects describing blueprint functions
    """

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
        """Convert artifacts into a JSON-serialisable dictionary.

        Creates a comprehensive bundle containing all blueprint artifacts in a
        structured format suitable for JSON serialization. This bundle includes
        metadata, formatted outputs, and code generation results.

        Returns:
            Dict[str, object]: A dictionary containing:
                - metadata: Blueprint identification and statistics
                - markdown: Markdown representation
                - json: Parsed JSON data with function information
                - ai_summary: AI-generated summary text
                - cpp: Dictionary containing C++ source files and paths

        Note:
            The function information is merged into the existing JSON payload
            to ensure all function data is included in the bundle.
        """

        # Parse the JSON text to create a mutable payload
        payload = json.loads(self.json_text)
        

        # Ensure functions are included in the payload, adding them if not present
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
        """Serialize function synopsis for bundles.

        Converts a FunctionSynopsis object into a dictionary representation
        suitable for JSON serialization. This method extracts all relevant
        function metadata and relationships.

        Args:
            function: FunctionSynopsis object containing function metadata

        Returns:
            Dict[str, object]: A dictionary containing:
                - name: Internal function name
                - display_name: User-friendly function name
                - category: Function categorization
                - entry_points: List of function entry points
                - calls: Functions called by this function
                - reads: Variables read by this function
                - writes: Variables written by this function
                - description: Function documentation/description
                - access: Access level (public, private, protected)
                - is_event: Boolean indicating if this is an event handler
        """

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
