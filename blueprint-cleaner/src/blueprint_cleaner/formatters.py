"""Output rendering orchestration.

Routes blueprint reports to appropriate formatter based on format type.
"""

from __future__ import annotations

from .formatters.json_output import render_json_output
from .formatters.markdown import format_as_markdown
from .models import BlueprintReport


def render_output(report: BlueprintReport, format_type: str) -> str:
    """Render blueprint report in requested format.

    @param report: Structured blueprint data.
    @param format_type: Output format ("markdown", "json").
    @return: Formatted output string.
    """
    fmt = format_type.lower()
    if fmt == "json":
        return render_json_output(report)
    return format_as_markdown(report)

