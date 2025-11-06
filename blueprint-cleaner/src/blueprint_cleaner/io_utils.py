"""I/O helpers for blueprint cleaner.

Wraps toolkit file I/O functions with blueprint-specific operations.
"""

from __future__ import annotations

import os
from pathlib import Path

from toolkit.console import print_metric_summary
from toolkit.file_io import read_text_with_encoding_detection, write_text_utf8

from .models import BlueprintReport


def read_text_file(path: str) -> str:
    """Load text while handling common UE blueprint encodings.

    @param path: Path to blueprint file.
    @return: Decoded text content.
    """
    return read_text_with_encoding_detection(path)


def write_text_file(path: str, text: str) -> None:
    """Persist text to disk using UTF-8 encoding.

    @param path: Output file path.
    @param text: Content to write.
    """
    write_text_utf8(path, text)


def print_report_summary(report: BlueprintReport) -> None:
    """Emit concise console summary of parsed blueprint.

    @param report: Blueprint report to summarize.
    """
    print("\n✓ Extracted:")
    print_metric_summary("variables", len(report.variables))
    print_metric_summary("graphs", len(report.graphs))

    event_count = sum(1 for graph in report.graphs if "Event" in graph.category)
    print_metric_summary("event-oriented graphs", event_count)

    total_calls = len({call for graph in report.graphs for call in graph.calls})
    print_metric_summary("unique function calls", total_calls)


def find_copy_files(directory: str) -> list[str]:
    """Recursively find all .COPY files in a directory.

    @param directory: Root directory to search.
    @return: Sorted list of absolute paths to .COPY files.
    """
    copy_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".COPY"):
                copy_files.append(os.path.join(root, file))
    return sorted(copy_files)
