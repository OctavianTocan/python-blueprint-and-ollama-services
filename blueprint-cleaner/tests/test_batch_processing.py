"""Tests for batch processing functionality."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest


MINIMAL_BLUEPRINT = """
Begin Object Class=/Script/Engine.BlueprintGeneratedClass Name="BP_Test"
End Object

ParentClass=Class'"/Script/Engine.Actor"'
""".strip()


def test_find_copy_files_returns_sorted_paths():
    """find_copy_files should recursively locate .COPY files."""
    from blueprint_cleaner.io_utils import find_copy_files

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test structure
        Path(tmpdir, "a.COPY").write_text(MINIMAL_BLUEPRINT, encoding="utf-8")
        Path(tmpdir, "subdir").mkdir()
        Path(tmpdir, "subdir", "b.COPY").write_text(MINIMAL_BLUEPRINT, encoding="utf-8")
        Path(tmpdir, "other.txt").write_text("not a blueprint", encoding="utf-8")

        files = find_copy_files(tmpdir)

        assert len(files) == 2
        assert all(f.endswith(".COPY") for f in files)
        assert files == sorted(files)


def test_find_copy_files_returns_empty_for_no_files():
    """find_copy_files should return empty list when no .COPY files exist."""
    from blueprint_cleaner.io_utils import find_copy_files

    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "other.txt").write_text("not a blueprint", encoding="utf-8")

        files = find_copy_files(tmpdir)

        assert files == []


def test_batch_processing_processes_multiple_files(tmp_path):
    """Batch processing should handle multiple .COPY files."""
    from blueprint_cleaner.pipeline import clean_blueprint_directory

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Create test files
    (input_dir / "BP_One.COPY").write_text(MINIMAL_BLUEPRINT, encoding="utf-8")
    (input_dir / "BP_Two.COPY").write_text(MINIMAL_BLUEPRINT, encoding="utf-8")

    successful, failed = clean_blueprint_directory(
        str(input_dir),
        str(output_dir),
        format_type="markdown",
        debug=False,
        fail_fast=False,
    )

    assert successful == 2
    assert failed == 0
    assert (output_dir / "BP_One.md").exists()
    assert (output_dir / "BP_Two.md").exists()


def test_batch_processing_creates_output_directory(tmp_path):
    """Batch processing should create output directory if it doesn't exist."""
    from blueprint_cleaner.pipeline import clean_blueprint_directory

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "nonexistent" / "output"
    input_dir.mkdir()

    (input_dir / "BP_Test.COPY").write_text(MINIMAL_BLUEPRINT, encoding="utf-8")

    successful, failed = clean_blueprint_directory(
        str(input_dir),
        str(output_dir),
        format_type="markdown",
        debug=False,
        fail_fast=False,
    )

    assert successful == 1
    assert failed == 0
    assert output_dir.exists()
    assert (output_dir / "BP_Test.md").exists()


def test_batch_processing_with_json_format(tmp_path):
    """Batch processing should support different output formats."""
    from blueprint_cleaner.pipeline import clean_blueprint_directory

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    (input_dir / "BP_Test.COPY").write_text(MINIMAL_BLUEPRINT, encoding="utf-8")

    successful, failed = clean_blueprint_directory(
        str(input_dir),
        str(output_dir),
        format_type="json",
        debug=False,
        fail_fast=False,
    )

    assert successful == 1
    assert failed == 0
    assert (output_dir / "BP_Test.json").exists()


def test_batch_processing_handles_nonexistent_directory():
    """Batch processing should handle nonexistent input directory."""
    from blueprint_cleaner.pipeline import clean_blueprint_directory

    successful, failed = clean_blueprint_directory(
        "/nonexistent/path",
        "/output/path",
        format_type="markdown",
        debug=False,
        fail_fast=False,
    )

    assert successful == 0
    assert failed == 0


def test_batch_processing_handles_empty_directory(tmp_path):
    """Batch processing should handle directory with no .COPY files."""
    from blueprint_cleaner.pipeline import clean_blueprint_directory

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    successful, failed = clean_blueprint_directory(
        str(input_dir),
        str(output_dir),
        format_type="markdown",
        debug=False,
        fail_fast=False,
    )

    assert successful == 0
    assert failed == 0


def test_batch_processing_fail_fast_stops_on_error(tmp_path):
    """Batch processing with fail_fast should stop on first error."""
    from blueprint_cleaner.pipeline import clean_blueprint_directory

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    # Create valid and invalid files
    (input_dir / "A_Valid.COPY").write_text(MINIMAL_BLUEPRINT, encoding="utf-8")
    (input_dir / "B_Invalid.COPY").write_text("invalid content", encoding="utf-8")
    (input_dir / "C_Valid.COPY").write_text(MINIMAL_BLUEPRINT, encoding="utf-8")

    successful, failed = clean_blueprint_directory(
        str(input_dir),
        str(output_dir),
        format_type="markdown",
        debug=False,
        fail_fast=True,
    )

    # Should stop after processing first two files (one success, one failure)
    assert successful + failed < 3
