"""PDF slide extraction to PNG files for Claude Code integration."""

from __future__ import annotations

__all__ = ["extract_to_dir", "run_extract"]

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

import pymupdf

from chalk.pdf import extract_pages_as_png, parse_page_spec


def extract_to_dir(
    pdf_path: Path,
    page_spec: str,
    output_dir: Path,
    *,
    max_long_edge: int = 1568,
) -> list[Path]:
    """Extract PDF pages as PNGs into a directory.

    Args:
        pdf_path: Path to the PDF file.
        page_spec: 1-based page specification (e.g. "3-7", "1,3,5").
        output_dir: Directory to write PNG files into.
        max_long_edge: Maximum pixels for the longer edge.

    Returns:
        List of written PNG file paths, sorted by page number.

    Raises:
        FileNotFoundError: If pdf_path does not exist.
        ValueError: If page_spec is invalid or the PDF cannot be opened.
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
        total_pages = len(doc)
    finally:
        doc.close()  # type: ignore[no-untyped-call]

    page_indices = parse_page_spec(page_spec, total_pages)
    png_images = extract_pages_as_png(
        pdf_path, page_indices, max_long_edge=max_long_edge
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for idx, png_bytes in zip(page_indices, png_images, strict=True):
        filename = f"slide_{idx + 1:03d}.png"
        file_path = output_dir / filename
        file_path.write_bytes(png_bytes)
        paths.append(file_path)

    return paths


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chalk.extract",
        description="Extract PDF pages as PNG files.",
    )
    parser.add_argument(
        "pdf",
        type=Path,
        help="Path to the PDF file.",
    )
    parser.add_argument(
        "pages",
        type=str,
        help='1-based page specification: "5", "3-7", "1,3,5", or "1-3,5,7-9".',
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: auto-created temp dir).",
    )
    parser.add_argument(
        "--cleanup",
        type=Path,
        default=None,
        help="Remove the specified directory and exit.",
    )
    return parser


def run_extract(argv: list[str] | None = None) -> int:
    """Run the extraction CLI. Returns 0 on success, 1 on error."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    cleanup_dir: Path | None = args.cleanup
    if cleanup_dir is not None:
        tmp_root = Path(tempfile.gettempdir())
        try:
            resolved = cleanup_dir.resolve()
            resolved.relative_to(tmp_root)
        except ValueError:
            sys.stderr.write(f"Error: cleanup path must be inside {tmp_root}\n")
            return 1
        if not resolved.name.startswith("chalk-slides-"):
            sys.stderr.write(
                "Error: cleanup path must be an chalk-slides-* directory\n"
            )
            return 1
        try:
            shutil.rmtree(cleanup_dir)
        except Exception as exc:
            sys.stderr.write(f"Error: cleanup failed: {exc}\n")
            return 1
        return 0

    pdf_path: Path = args.pdf
    output_dir: Path | None = args.output_dir

    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="chalk-slides-"))

    try:
        paths = extract_to_dir(pdf_path, args.pages, output_dir)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1

    sys.stdout.write(f"{output_dir}\n")
    for p in paths:
        sys.stdout.write(f"{p}\n")

    return 0


def _main() -> None:
    """Entry point for the chalk-extract CLI."""
    sys.exit(run_extract())


if __name__ == "__main__":
    _main()
