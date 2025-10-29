"""File I/O utilities with encoding detection and safe text handling.

Provides robust file reading/writing operations handling various encodings
commonly encountered in Unreal Engine blueprint files and general text data.
"""

from __future__ import annotations


def read_text_with_encoding_detection(path: str) -> str:
    """Load text file with automatic encoding detection.

    Handles UTF-16 (with BOM), UTF-8 with BOM, and falls back to UTF-8.
    Removes null bytes that may appear in some binary-exported text files.

    @param path: Absolute path to text file.
    @return: File contents as decoded string.
    """
    with open(path, "rb") as handle:
        payload = handle.read()

    encoding = detect_encoding_from_bom(payload)

    try:
        text = payload.decode(encoding)
    except UnicodeDecodeError:
        text = payload.decode("utf-16", errors="ignore")

    return text.replace("\x00", "")


def detect_encoding_from_bom(payload: bytes) -> str:
    """Identify encoding from byte order mark.

    @param payload: Raw file bytes.
    @return: Encoding name suitable for str.decode().
    """
    bom = payload[:2]
    if bom in {b"\xff\xfe", b"\xfe\xff"}:
        return "utf-16"
    if payload[:3] == b"\xef\xbb\xbf":
        return "utf-8-sig"
    return "utf-8"


def write_text_utf8(path: str, text: str) -> None:
    """Persist text to disk using UTF-8 encoding.

    @param path: Absolute path for output file.
    @param text: Content to write.
    """
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
