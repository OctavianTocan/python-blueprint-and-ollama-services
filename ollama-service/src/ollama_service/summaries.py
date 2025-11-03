"""Text summarization using rolling window strategy."""

from __future__ import annotations

import math
from collections import deque
from typing import Callable, Deque, Iterable, Iterator, List

SummaryFn = Callable[[str], str]


def generate_rolling_summary(
    document: str,
    summariser: SummaryFn,
    chunk_size: int = 4000,
    overlap: int = 200,
) -> str:
    """Summarise large document using rolling window strategy.
    
    @param document: Text to summarise.
    @param summariser: Function that summarises a chunk of text.
    @param chunk_size: Maximum size of each chunk.
    @param overlap: Number of characters to overlap between chunks.
    @return: Final summary text.
    @raises ValueError: If chunk_size is not positive or overlap is negative.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")

    chunks = list(_chunk_document(document, chunk_size, overlap))
    if not chunks:
        return ""

    summary = ""
    for chunk in chunks:
        prompt = _build_summary_prompt(summary, chunk)
        summary = summariser(prompt).strip()
    return summary


def _chunk_document(document: str, chunk_size: int, overlap: int) -> Iterable[str]:
    """Yield chunked segments respecting paragraph and word boundaries.
    
    @param document: Text to chunk.
    @param chunk_size: Maximum size of each chunk.
    @param overlap: Number of characters to overlap.
    @return: Iterator of text chunks.
    """

    cleaned = document.strip()
    if not cleaned:
        return

    total_length = len(cleaned)
    max_chunk = _determine_max_chunk(total_length, chunk_size)
    effective_overlap = max(0, min(overlap, max(1, chunk_size // 4)))

    paragraphs = _prepare_paragraphs(document, max_chunk)
    if not paragraphs:
        yield cleaned
        return

    buffer: Deque[str] = deque()
    current_length = 0

    for paragraph in paragraphs:
        paragraph_text = paragraph if paragraph.endswith("\n") else f"{paragraph}\n"
        paragraph_length = len(paragraph_text)

        if current_length and current_length + paragraph_length > max_chunk:
            yield "".join(buffer).strip()
            _apply_overlap(buffer, effective_overlap)
            current_length = sum(len(item) for item in buffer)

        buffer.append(paragraph_text)
        current_length += paragraph_length

    if buffer:
        yield "".join(buffer).strip()


def _determine_max_chunk(total_length: int, chunk_size: int) -> int:
    """Calculate adaptive chunk ceiling based on document size.
    
    @param total_length: Total length of document.
    @param chunk_size: Base chunk size.
    @return: Adjusted maximum chunk size.
    """

    base_size = max(chunk_size, 1)
    target_chunks = max(1, math.ceil(total_length / (base_size * 2)))
    target_length = math.ceil((total_length / target_chunks) * 1.1)
    return max(base_size, target_length)


def _prepare_paragraphs(document: str, max_segment: int) -> List[str]:
    """Split document into paragraphs, breaking long ones as needed.
    
    @param document: Text to split.
    @param max_segment: Maximum paragraph size.
    @return: List of paragraph strings.
    """

    raw_paragraphs = [
        paragraph.strip() for paragraph in document.split("\n\n") if paragraph.strip()
    ]
    if not raw_paragraphs:
        raw_paragraphs = [document.strip()]

    paragraphs: List[str] = []
    for paragraph in raw_paragraphs:
        if len(paragraph) <= max_segment:
            paragraphs.append(paragraph)
            continue
        paragraphs.extend(_split_long_paragraph(paragraph, max_segment))

    return paragraphs


def _split_long_paragraph(paragraph: str, max_segment: int) -> Iterator[str]:
    """Break long paragraph into smaller segments without cutting words.
    
    @param paragraph: Text to split.
    @param max_segment: Maximum segment size.
    @return: Iterator of paragraph segments.
    """

    remaining = paragraph
    while len(remaining) > max_segment:
        break_index = remaining.rfind(" ", 0, max_segment)
        if break_index == -1 or break_index < max_segment // 2:
            break_index = max_segment
        segment = remaining[:break_index].strip()
        if not segment:
            break
        yield segment
        remaining = remaining[break_index:].lstrip()

    if remaining:
        yield remaining


def _apply_overlap(buffer: Deque[str], overlap: int) -> None:
    """Retain trailing content to provide continuity between chunks.
    
    @param buffer: Deque buffer to modify in place.
    @param overlap: Number of characters to retain.
    """

    if overlap <= 0:
        buffer.clear()
        return

    tail_text = "".join(buffer)[-overlap:]
    buffer.clear()
    if tail_text:
        buffer.append(tail_text)


def _build_summary_prompt(previous: str, chunk: str) -> str:
    """Compose prompt for summarising a specific chunk.
    
    @param previous: Previous summary text.
    @param chunk: Current chunk to summarise.
    @return: Prompt string for summariser.
    """

    header = (
        "You are an expert summarization assistant helping condense "
        "documents into concise summaries for LLM consumption."
    )

    if previous:
        return (
            f"{header}\n\nPrevious summary:\n{previous}\n\n"
            f"New content:\n{chunk}\n\nUpdate the summary with key information."
        )

    return (
        f"{header}\n\n"
        f"Content:\n{chunk}\n\n"
        "Produce a concise summary capturing the key points."
    )
