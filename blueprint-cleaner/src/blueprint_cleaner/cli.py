"""Command line interface for blueprint cleaner."""

from __future__ import annotations

import argparse
import os
import sys

from .pipeline import clean_blueprint_directory, clean_blueprint_file

SUPPORTED_FORMATS = [
    "markdown",
    "json",
    "bundle",
    "summary",
    "cpp-header",
    "cpp-source",
]


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""

    parser = argparse.ArgumentParser(
        description="Clean UE5 .COPY blueprint files for AI analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s input.copy\n"
            "  %(prog)s input.copy -o cleaned.md\n"
            "  %(prog)s input.copy --format json\n"
            "  %(prog)s data/in/ -o data/out/ --format markdown\n"
            "  %(prog)s input.copy -d  # debug mode with detailed logs\n"
            "  %(prog)s data/in/ -o data/out/ --fail-fast  # stop on first error"
        ),
    )
    parser.add_argument(
        "input",
        help="Input .COPY file path or directory containing .COPY files",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (for single file) or directory (for batch processing)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=SUPPORTED_FORMATS + ["text"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed logs",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop batch processing on first error",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Entry point invoked by console script."""

    parser = build_parser()
    args = parser.parse_args(argv)

    # Determine if input is a directory or file
    is_directory = os.path.isdir(args.input)
    format_choice = "markdown" if args.format == "text" else args.format

    if is_directory:
        # Batch processing mode
        output_dir = args.output
        if not output_dir:
            # Default output directory is input_cleaned/
            output_dir = f"{args.input.rstrip('/')}_cleaned"

        successful, failed = clean_blueprint_directory(
            args.input,
            output_dir,
            8192,
            format_choice,
            args.debug,
            args.fail_fast,
        )

        if failed == 0:
            print(f"✓ All files processed successfully")
            print(f"Output directory: {output_dir}")
            sys.exit(0)
        elif successful > 0:
            print(f"⚠ Some files failed to process")
            print(f"Output directory: {output_dir}")
            sys.exit(1)
        else:
            print(f"✗ All files failed to process")
            sys.exit(1)
    else:
        # Single file processing mode
        output_path = args.output
        if not output_path:
            base_name = os.path.splitext(args.input)[0]
            extension_map = {
                "markdown": ".md",
                "json": ".json",
                "bundle": ".bundle.json",
                "summary": ".summary.txt",
                "cpp-header": ".h",
                "cpp-source": ".cpp",
            }
            extension = extension_map.get(format_choice, ".md")
            output_path = f"{base_name}_cleaned{extension}"

        success = clean_blueprint_file(
            args.input,
            output_path,
            8192,
            format_choice,
            args.debug,
        )
        if success:
            print(f"\nOutput saved to: {output_path}")
            sys.exit(0)
        sys.exit(1)


if __name__ == "__main__":
    main()
