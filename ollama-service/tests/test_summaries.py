"""Tests for text summarization functionality."""

from __future__ import annotations

import pytest


def make_stub_summariser():
    """Create deterministic stub summariser for testing.
    
    @return: Tuple of (summariser_function, calls_list).
    """

    calls: list[str] = []

    def _summarise(prompt: str) -> str:
        calls.append(prompt)
        return f"<summary-{len(calls)}>"

    return _summarise, calls


def test_generate_rolling_summary_with_small_document():
    """Single-chunk documents should invoke summariser once."""

    from ollama_service import generate_rolling_summary

    summariser, calls = make_stub_summariser()
    summary = generate_rolling_summary(
        "Short document.",
        summariser=summariser,
        chunk_size=1000,
    )

    assert summary == "<summary-1>"
    assert len(calls) == 1


def test_generate_rolling_summary_with_large_document():
    """Multi-chunk documents should invoke summariser multiple times."""

    from ollama_service import generate_rolling_summary

    base_doc = "\n".join(f"Section {idx}: Content here." for idx in range(20))

    summariser, calls = make_stub_summariser()
    summary = generate_rolling_summary(
        base_doc,
        summariser=summariser,
        chunk_size=100,
    )

    assert summary.startswith("<summary-")
    assert len(calls) > 1, "Should have multiple summarization calls"


@pytest.mark.parametrize("chunk_size, expected_calls", [(80, 3), (400, 1)])
def test_rolling_summary_batches_respect_chunk_size(
    chunk_size: int, expected_calls: int
) -> None:
    """Rolling summaries should chunk long documents while keeping short ones single-pass."""

    from ollama_service import generate_rolling_summary

    base_doc = "\n".join(
        f"Section {idx}: Lorem ipsum dolor sit amet." for idx in range(12)
    )

    summariser, calls = make_stub_summariser()

    summary = generate_rolling_summary(
        base_doc,
        summariser=summariser,
        chunk_size=chunk_size,
    )

    assert summary.startswith("<summary-")
    assert len(calls) == expected_calls


def test_rolling_summary_with_empty_document():
    """Empty documents should return empty summary."""

    from ollama_service import generate_rolling_summary

    summariser, calls = make_stub_summariser()
    summary = generate_rolling_summary(
        "",
        summariser=summariser,
        chunk_size=1000,
    )

    assert summary == ""
    assert len(calls) == 0


def test_rolling_summary_with_invalid_chunk_size():
    """Invalid chunk sizes should raise ValueError."""

    from ollama_service import generate_rolling_summary

    summariser, _ = make_stub_summariser()

    with pytest.raises(ValueError, match="chunk_size must be positive"):
        generate_rolling_summary(
            "Some text",
            summariser=summariser,
            chunk_size=0,
        )

    with pytest.raises(ValueError, match="chunk_size must be positive"):
        generate_rolling_summary(
            "Some text",
            summariser=summariser,
            chunk_size=-100,
        )


def test_rolling_summary_with_negative_overlap():
    """Negative overlap should raise ValueError."""

    from ollama_service import generate_rolling_summary

    summariser, _ = make_stub_summariser()

    with pytest.raises(ValueError, match="overlap must be non-negative"):
        generate_rolling_summary(
            "Some text",
            summariser=summariser,
            chunk_size=1000,
            overlap=-1,
        )
