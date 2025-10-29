"""Console output helpers for progress and summary reporting.

Provides standardized terminal output functions for displaying processing
status, metrics, and summaries with consistent formatting.
"""

from __future__ import annotations


def print_processing_header(input_path: str, output_path: str, format_type: str) -> None:
    """Display processing configuration to console.

    @param input_path: Path to input file being processed.
    @param output_path: Path where output will be written.
    @param format_type: Output format identifier (e.g., "markdown", "json").
    """
    print(f"Processing: {input_path}")
    print(f"Output: {output_path}")
    print(f"Format: {format_type}")


def print_success_footer(output_path: str) -> None:
    """Display successful completion message.

    @param output_path: Path where output was written.
    """
    print(f"\nOutput saved to: {output_path}")


def print_metric_summary(label: str, value: int, indent: int = 2) -> None:
    """Print a single metric line with consistent formatting.

    @param label: Description of the metric.
    @param value: Numeric value to display.
    @param indent: Number of spaces to indent the line.
    """
    prefix = " " * indent
    print(f"{prefix}- {label}: {value}")
