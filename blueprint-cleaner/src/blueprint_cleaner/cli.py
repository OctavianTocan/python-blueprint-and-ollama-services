"""Command line interface for blueprint cleaner."""

from __future__ import annotations

import argparse
import os
import sys

from .pipeline import clean_blueprint_file


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
            "  %(prog)s input.copy -d  # debug mode with detailed logs"
        ),
    )
    parser.add_argument("input", help="Input .COPY file path")
    parser.add_argument(
        "-o",
        "--output",
        help="Output file path (default: input_cleaned.md/json)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["markdown", "text", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed logs",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Entry point invoked by console script."""

    parser = build_parser()
    args = parser.parse_args(argv)

    output_path = args.output
    if not output_path:
        base_name = os.path.splitext(args.input)[0]
        extension = ".json" if args.format == "json" else ".md"
        output_path = f"{base_name}_cleaned{extension}"

    format_choice = "markdown" if args.format == "text" else args.format
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
