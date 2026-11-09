"""Tests for CLI functionality."""

from __future__ import annotations

import pytest

from blueprint_cleaner.cli import (
    ensure_correct_extension,
    get_extension_for_format,
)


class TestExtensionHelpers:
    """Test helper functions for file extension handling."""

    def test_get_extension_for_format_markdown(self):
        """Markdown format should return .md extension."""
        assert get_extension_for_format("markdown") == ".md"

    def test_get_extension_for_format_json(self):
        """JSON format should return .json extension."""
        assert get_extension_for_format("json") == ".json"

    def test_get_extension_for_format_bundle(self):
        """Bundle format should return .bundle.json extension."""
        assert get_extension_for_format("bundle") == ".bundle.json"

    def test_get_extension_for_format_summary(self):
        """Summary format should return .summary.txt extension."""
        assert get_extension_for_format("summary") == ".summary.txt"

    def test_get_extension_for_format_cpp_header(self):
        """CPP header format should return .h extension."""
        assert get_extension_for_format("cpp-header") == ".h"

    def test_get_extension_for_format_cpp_source(self):
        """CPP source format should return .cpp extension."""
        assert get_extension_for_format("cpp-source") == ".cpp"

    def test_get_extension_for_format_unknown(self):
        """Unknown format should default to .md extension."""
        assert get_extension_for_format("unknown") == ".md"


class TestEnsureCorrectExtension:
    """Test ensure_correct_extension function."""

    def test_appends_md_when_missing(self):
        """Should append .md extension to output path without extension."""
        assert ensure_correct_extension("output", "markdown") == "output.md"

    def test_keeps_md_when_present(self):
        """Should not modify output path that already has .md extension."""
        assert ensure_correct_extension("output.md", "markdown") == "output.md"

    def test_appends_json_when_missing(self):
        """Should append .json extension to output path without extension."""
        assert ensure_correct_extension("output", "json") == "output.json"

    def test_keeps_json_when_present(self):
        """Should not modify output path that already has .json extension."""
        assert ensure_correct_extension("output.json", "json") == "output.json"

    def test_appends_bundle_json_when_missing(self):
        """Should append .bundle.json extension to output path."""
        assert (
            ensure_correct_extension("output", "bundle") == "output.bundle.json"
        )

    def test_keeps_bundle_json_when_present(self):
        """Should not modify output path with .bundle.json extension."""
        assert (
            ensure_correct_extension("output.bundle.json", "bundle")
            == "output.bundle.json"
        )

    def test_appends_summary_txt_when_missing(self):
        """Should append .summary.txt extension to output path."""
        assert (
            ensure_correct_extension("output", "summary") == "output.summary.txt"
        )

    def test_keeps_summary_txt_when_present(self):
        """Should not modify output path with .summary.txt extension."""
        assert (
            ensure_correct_extension("output.summary.txt", "summary")
            == "output.summary.txt"
        )

    def test_appends_h_when_missing(self):
        """Should append .h extension to output path."""
        assert ensure_correct_extension("output", "cpp-header") == "output.h"

    def test_keeps_h_when_present(self):
        """Should not modify output path that already has .h extension."""
        assert ensure_correct_extension("output.h", "cpp-header") == "output.h"

    def test_appends_cpp_when_missing(self):
        """Should append .cpp extension to output path."""
        assert ensure_correct_extension("output", "cpp-source") == "output.cpp"

    def test_keeps_cpp_when_present(self):
        """Should not modify output path that already has .cpp extension."""
        assert ensure_correct_extension("output.cpp", "cpp-source") == "output.cpp"

    def test_appends_extension_to_path_with_directory(self):
        """Should append extension to full path including directories."""
        assert (
            ensure_correct_extension("/path/to/output", "markdown")
            == "/path/to/output.md"
        )

    def test_keeps_extension_in_path_with_directory(self):
        """Should not modify full path that already has correct extension."""
        assert (
            ensure_correct_extension("/path/to/output.md", "markdown")
            == "/path/to/output.md"
        )

    def test_replaces_wrong_extension(self):
        """Should append correct extension even if wrong one exists."""
        # This is the current behavior: it appends rather than replacing
        assert (
            ensure_correct_extension("output.txt", "markdown") == "output.txt.md"
        )
