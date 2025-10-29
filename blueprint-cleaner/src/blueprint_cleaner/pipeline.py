"""Public service entry points for blueprint cleaning.

Orchestrates the full pipeline from reading input files to writing formatted output.
"""

from __future__ import annotations

import os
import traceback

from toolkit.console import print_processing_header, print_success_footer

from .formatters.markdown import format_as_markdown
from .formatters.json_output import render_json_output
from .io_utils import print_report_summary, read_text_file, write_text_file
from .report import build_blueprint_report


def render_output(report, format_type: str) -> str:
    """Route to appropriate formatter based on format type."""
    fmt = format_type.lower()
    if fmt == "json":
        return render_json_output(report)
    return format_as_markdown(report)


def clean_blueprint_file(
    input_file: str,
    output_file: str,
    chunk_size: int = 8192,  # Legacy compatibility
    format_type: str = "markdown",
    debug: bool = False,
) -> bool:
    """Generate AI-focused summary for a UE5 blueprint file.

    @param input_file: Path to input .COPY file.
    @param output_file: Path for output file.
    @param chunk_size: Unused legacy parameter for compatibility.
    @param format_type: Output format ("markdown", "json").
    @param debug: Enable debug output.
    @return: True if successful, False on error.
    """
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False

    print_processing_header(input_file, output_file, format_type)

    try:
        content = read_text_file(input_file)
        report = build_blueprint_report(content, debug)
        output_text = render_output(report, format_type)
        write_text_file(output_file, output_text)
        print_report_summary(report)
        print_success_footer(output_file)
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error processing file: {exc}")
        traceback.print_exc()
        return False
