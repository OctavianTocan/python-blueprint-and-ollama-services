"""Public service entry points for blueprint cleaning."""

from __future__ import annotations

import os
import traceback

from .formatters import render_output
from .io_utils import print_report_summary, read_text_file, write_text_file
from .report import build_blueprint_report


def clean_blueprint_file(
    input_file: str,
    output_file: str,
    chunk_size: int = 8192,  # Legacy compatibility
    format_type: str = "markdown",
    debug: bool = False,
) -> bool:
    """Generate an AI-focused summary for a UE5 blueprint file."""

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False

    print(f"Processing: {input_file}")
    print(f"Output: {output_file}")
    print(f"Format: {format_type}")

    try:
        content = read_text_file(input_file)
        report = build_blueprint_report(content, debug)
        output_text = render_output(report, format_type)
        write_text_file(output_file, output_text)
        print_report_summary(report)
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error processing file: {exc}")
        traceback.print_exc()
        return False
