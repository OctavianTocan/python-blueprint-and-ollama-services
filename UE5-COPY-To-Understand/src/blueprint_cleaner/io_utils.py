"""I/O helpers for blueprint cleaner."""

from __future__ import annotations

from typing import Optional

from .models import BlueprintReport


def read_text_file(path: str) -> str:
    """Load text while handling common UE blueprint encodings."""

    with open(path, "rb") as handle:
        payload = handle.read()

    bom = payload[:2]
    if bom in {b"\xff\xfe", b"\xfe\xff"}:
        encoding = "utf-16"
    elif payload[:3] == b"\xef\xbb\xbf":
        encoding = "utf-8-sig"
    else:
        encoding = "utf-8"

    try:
        text = payload.decode(encoding)
    except UnicodeDecodeError:
        text = payload.decode("utf-16", errors="ignore")

    return text.replace("\x00", "")


def write_text_file(path: str, text: str) -> None:
    """Persist text to disk using UTF-8 encoding."""

    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def print_report_summary(report: BlueprintReport) -> None:
    """Emit a concise console summary of the parsed blueprint."""

    print("\n✓ Extracted:")
    print(f"  - {len(report.variables)} variables")
    print(f"  - {len(report.graphs)} graphs")
    event_count = sum(1 for graph in report.graphs if "Event" in graph.category)
    print(f"  - {event_count} event-oriented graphs")
    total_calls = len({call for graph in report.graphs for call in graph.calls})
    print(f"  - {total_calls} unique function calls")
