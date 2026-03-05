"""PDF page extraction and rendering."""

from __future__ import annotations

__all__ = ["extract_pages_as_png", "parse_page_spec"]

from typing import TYPE_CHECKING

import pymupdf

if TYPE_CHECKING:
    from pathlib import Path


def parse_page_spec(spec: str, total_pages: int) -> list[int]:
    """Parse a 1-based page specification into sorted, deduplicated 0-based indices.

    Supported formats: "5", "3-7", "1,3,5", "1-3,5,7-9".

    Raises:
        ValueError: For out-of-range pages, reversed ranges, or invalid input.
    """
    if total_pages <= 0:
        msg = f"PDF has no pages (total_pages={total_pages})"
        raise ValueError(msg)

    indices: set[int] = set()
    for raw_part in spec.split(","):
        part = raw_part.strip()
        if not part:
            msg = "Empty page specification segment"
            raise ValueError(msg)

        if "-" in part:
            pieces = part.split("-", maxsplit=1)
            if len(pieces) != 2 or not pieces[0].strip() or not pieces[1].strip():
                msg = f"Invalid range: {part!r}"
                raise ValueError(msg)
            try:
                start = int(pieces[0])
                end = int(pieces[1])
            except ValueError:
                msg = f"Non-integer in range: {part!r}"
                raise ValueError(msg) from None
            if start > end:
                msg = f"Reversed range: {part!r} (start {start} > end {end})"
                raise ValueError(msg)
            for page_num in range(start, end + 1):
                _validate_page_num(page_num, total_pages)
                indices.add(page_num - 1)
        else:
            try:
                page_num = int(part)
            except ValueError:
                msg = f"Non-integer page number: {part!r}"
                raise ValueError(msg) from None
            _validate_page_num(page_num, total_pages)
            indices.add(page_num - 1)

    return sorted(indices)


def _validate_page_num(page_num: int, total_pages: int) -> None:
    if page_num < 1 or page_num > total_pages:
        msg = f"Page {page_num} out of range (1-{total_pages})"
        raise ValueError(msg)


def extract_pages_as_png(
    pdf_path: Path,
    page_indices: list[int],
    *,
    max_long_edge: int = 1568,
) -> list[bytes]:
    """Render PDF pages to PNG bytes, scaled so the long edge <= max_long_edge.

    Args:
        pdf_path: Path to the PDF file.
        page_indices: 0-based page indices to extract.
        max_long_edge: Maximum pixels for the longer edge (default 1568,
            Claude's optimal max to avoid server-side downscaling).

    Returns:
        List of PNG bytes, one per requested page.

    Raises:
        FileNotFoundError: If pdf_path does not exist.
        ValueError: If the file is not a valid PDF or a rendered image exceeds 5 MB.
    """
    if not pdf_path.exists():
        msg = f"File not found: {pdf_path}"
        raise FileNotFoundError(msg)

    try:
        doc = pymupdf.open(pdf_path)  # type: ignore[no-untyped-call]
    except Exception as exc:
        msg = f"Not a valid PDF: {pdf_path}"
        raise ValueError(msg) from exc
    try:
        if not doc.is_pdf:
            msg = f"Not a valid PDF: {pdf_path}"
            raise ValueError(msg)

        results: list[bytes] = []
        for idx in page_indices:
            page = doc[idx]
            rect = page.rect  # type: ignore[attr-defined]
            long_edge = max(rect.width, rect.height)
            scale = min(max_long_edge / long_edge, 1.0) if long_edge > 0 else 1.0
            matrix = pymupdf.Matrix(scale, scale)  # type: ignore[no-untyped-call]
            pixmap = page.get_pixmap(matrix=matrix)  # type: ignore[attr-defined]
            png_bytes = pixmap.tobytes("png")

            max_size = 5 * 1024 * 1024
            if len(png_bytes) > max_size:
                msg = (
                    f"Page {idx + 1} rendered to {len(png_bytes)} bytes, "
                    f"exceeding 5 MB limit"
                )
                raise ValueError(msg)

            results.append(png_bytes)
    finally:
        doc.close()  # type: ignore[no-untyped-call]

    return results
