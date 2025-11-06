"""Public service entry points for blueprint cleaning."""

from __future__ import annotations

import commentjson
import os
import traceback
from typing import Callable, Optional

from ollama_service import generate_rolling_summary
from toolkit.console import print_processing_header, print_success_footer

from .artifacts import BlueprintArtifacts
from .formatters.json_output import render_json_output
from .formatters.markdown import format_as_markdown
from .formatters.unreal_cpp import generate_unreal_cpp
from .io_utils import print_report_summary, read_text_file, write_text_file
from .report import build_blueprint_report

SummaryFn = Callable[[str], str]
SUMMARY_REQUIRED_FORMATS = {"summary", "bundle"}
FORMAT_EXTENSIONS = {
    "markdown": ".md",
    "json": ".json",
    "bundle": ".bundle.json",
    "summary": ".summary.txt",
    "cpp-header": ".h",
    "cpp-source": ".cpp",
}


def generate_blueprint_artifacts(
    content: str,
    summariser: Optional[SummaryFn] = None,
    summary_chunk_size: int = 4000,
    debug: bool = False,
    format_type: str = "markdown",
) -> BlueprintArtifacts:
    """Produce all derived outputs for a blueprint."""

    report = build_blueprint_report(content, debug)
    markdown = format_as_markdown(report)
    json_text = render_json_output(report)

    cpp = generate_unreal_cpp(report)

    # Only generate AI summary if the format requires it
    summary = ""
    if format_type.lower() in SUMMARY_REQUIRED_FORMATS:
        summary = generate_rolling_summary(
            markdown,
            summariser or _default_summariser(),
            chunk_size=summary_chunk_size,
        )

    return BlueprintArtifacts(
        report=report,
        markdown=markdown,
        json_text=json_text,
        ai_summary=summary,
        cpp_header=cpp.header,
        cpp_source=cpp.source,
        cpp_header_path=cpp.header_path,
        cpp_source_path=cpp.source_path,
        functions=report.functions,
    )


def write_artifact_bundle(
    content: str,
    output_path: str,
    summariser: Optional[SummaryFn] = None,
    summary_chunk_size: int = 4000,
    debug: bool = False,
) -> None:
    """Generate artifacts and write bundle to disk."""

    # Bundle format requires AI summary
    if summariser is None:
        summariser = _default_summariser()

    artifacts = generate_blueprint_artifacts(
        content,
        summariser=summariser,
        summary_chunk_size=summary_chunk_size,
        debug=debug,
        format_type="bundle",
    )
    bundle_text = commentjson.dumps(artifacts.to_bundle(), indent=2)
    write_text_file(output_path, bundle_text)


def render_output(artifacts: BlueprintArtifacts, format_type: str) -> str:
    """Route to appropriate formatter based on format type."""

    fmt = format_type.lower()
    if fmt == "json":
        return artifacts.json_text
    if fmt == "bundle":
        return commentjson.dumps(artifacts.to_bundle(), indent=2)
    if fmt == "summary":
        return artifacts.ai_summary
    if fmt == "cpp-header":
        return artifacts.cpp_header
    if fmt == "cpp-source":
        return artifacts.cpp_source
    return artifacts.markdown


def clean_blueprint_file(
    input_file: str,
    output_file: str,
    chunk_size: int = 4000,
    format_type: str = "markdown",
    debug: bool = False,
    summariser: Optional[SummaryFn] = None,
) -> bool:
    """Generate AI-focused summary for a UE5 blueprint file."""

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return False

    print_processing_header(input_file, output_file, format_type)

    try:
        # Load blueprint content
        content = read_text_file(input_file)

        # Only provide summariser if the format requires AI summary
        summariser_to_use = summariser
        if format_type.lower() in SUMMARY_REQUIRED_FORMATS and summariser is None:
            summariser_to_use = _default_summariser()

        artifacts = generate_blueprint_artifacts(
            content,
            summariser=summariser_to_use,
            summary_chunk_size=chunk_size,
            debug=debug,
            format_type=format_type,
        )

        output_text = render_output(artifacts, format_type)
        write_text_file(output_file, output_text)
        print_report_summary(artifacts.report)
        print_success_footer(output_file)
        return True
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error processing file: {exc}")
        traceback.print_exc()
        return False


def clean_blueprint_directory(
    input_dir: str,
    output_dir: str,
    chunk_size: int = 4000,
    format_type: str = "markdown",
    debug: bool = False,
    fail_fast: bool = False,
    summariser: Optional[SummaryFn] = None,
) -> tuple[int, int]:
    """Process all .COPY files in a directory.

    @param input_dir: Directory containing .COPY files.
    @param output_dir: Directory for output files.
    @param chunk_size: Token limit for AI summary chunks.
    @param format_type: Output format (markdown, json, etc.).
    @param debug: Enable debug logging.
    @param fail_fast: Stop on first error if True.
    @param summariser: Optional summariser function.
    @return: Tuple of (successful_count, failed_count).
    """
    from .io_utils import find_copy_files

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return (0, 0)

    copy_files = find_copy_files(input_dir)
    if not copy_files:
        print(f"No .COPY files found in '{input_dir}'")
        return (0, 0)

    os.makedirs(output_dir, exist_ok=True)

    total = len(copy_files)
    successful = 0
    failed = 0

    print(f"\nFound {total} .COPY file{'s' if total != 1 else ''} to process\n")

    for index, input_file in enumerate(copy_files, start=1):
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        extension = FORMAT_EXTENSIONS.get(format_type, ".md")
        output_file = os.path.join(output_dir, f"{base_name}{extension}")

        print(f"[{index}/{total}] Processing {base_name}...")

        success = clean_blueprint_file(
            input_file,
            output_file,
            chunk_size,
            format_type,
            debug,
            summariser,
        )

        if success:
            successful += 1
        else:
            failed += 1
            if fail_fast:
                print("\n❌ Stopping due to error (--fail-fast enabled)")
                break

    summary_text = "Batch Processing Summary:"
    separator = "=" * len(summary_text)
    print(f"\n{separator}")
    print(summary_text)
    print(f"  ✓ Successful: {successful}/{total}")
    print(f"  ✗ Failed: {failed}/{total}")
    print(f"{separator}\n")

    return (successful, failed)


def _default_summariser() -> SummaryFn:
    """Create a summariser callback using the default LLM service.
    @return: Summariser function.
    """
    from ollama_service.client import ask_ollama_question
    from ollama_service.models import OllamaOptions

    # Keep the summary concise and cost-effective by limiting generation.
    # Tests assert this budget to be 320 tokens.
    options = OllamaOptions(num_predict=320)

    def _summarise(prompt: str) -> str:
        # TODO: This throws out an error
        return ask_ollama_question(prompt, options=options)

    return _summarise
