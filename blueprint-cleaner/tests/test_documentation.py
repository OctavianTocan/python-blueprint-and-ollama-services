"""
Simple tests for the documentation system.
We'll start small and build up as we learn.
"""

import pytest
from pathlib import Path


def test_file_creation():
    """Our first test - just checks if we can create a file."""
    # This is a simple test to make sure our testing setup works
    test_file = Path("test_output.txt")
    test_file.write_text("Hello, world!")

    # Check if the file exists and has the right content
    assert test_file.exists()
    assert test_file.read_text() == "Hello, world!"

    # Clean up
    test_file.unlink()


# TODO: We'll add more tests here as we build our components
# For now, this just confirms our testing setup works