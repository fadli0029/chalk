"""Command-line interface for chalk."""

from __future__ import annotations

__all__ = ["build_parser", "run"]

import argparse
import importlib.resources
import os
import shutil
import sys
from pathlib import Path

import pymupdf

from chalk.llm import stream_explanation
from chalk.pdf import extract_pages_as_png, parse_page_spec
from chalk.prompt import DEFAULT_SYSTEM_PROMPT


def _install_skill() -> int:
    """Install the /slides skill to ~/.claude/skills/slides/SKILL.md."""
    dest = Path.home() / ".claude" / "skills" / "slides" / "SKILL.md"
    dest.parent.mkdir(parents=True, exist_ok=True)

    source = importlib.resources.files("chalk").joinpath("data/SKILL.md")
    with importlib.resources.as_file(source) as src_path:
        shutil.copy2(src_path, dest)

    sys.stdout.write(f"Installed /slides skill to {dest}\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for chalk."""
    parser = argparse.ArgumentParser(
        prog="chalk",
        description="Explain lecture slides using Claude's vision API.",
    )
    parser.add_argument(
        "--install-skill",
        action="store_true",
        help="Install the /slides skill for Claude Code and exit.",
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        help="Path to the PDF file containing lecture slides.",
    )
    parser.add_argument(
        "pages",
        nargs="?",
        type=str,
        help=('1-based page specification: "5", "3-7", "1,3,5", or "1-3,5,7-9".'),
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6",
        help="Claude model to use (default: claude-sonnet-4-6).",
    )
    parser.add_argument(
        "--prompt",
        default="Explain these slides.",
        dest="user_prompt",
        help="User prompt to send with the slides (default: 'Explain these slides.').",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=8192,
        help="Maximum tokens in the response (default: 8192).",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    """Run the chalk CLI. Returns 0 on success, 1 on user error, 2 on API error."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.install_skill:
        return _install_skill()

    if args.pdf is None or args.pages is None:
        parser.error("the following arguments are required: pdf, pages")

    pdf_path: Path = args.pdf
    if not pdf_path.exists():
        sys.stderr.write(f"Error: file not found: {pdf_path}\n")
        return 1

    try:
        doc = pymupdf.open(pdf_path)  # type: ignore[no-untyped-call]
        total_pages = len(doc)
        doc.close()  # type: ignore[no-untyped-call]
    except Exception as exc:
        sys.stderr.write(f"Error: could not open PDF: {exc}\n")
        return 1

    try:
        page_indices = parse_page_spec(args.pages, total_pages)
    except ValueError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1

    # Build context range: pages 1 through the last requested page.
    # Slides build on prior material, so the model needs the full
    # narrative up to the target pages for accurate explanations.
    max_page_0based = max(page_indices)
    context_indices = list(range(max_page_0based + 1))

    try:
        png_images = extract_pages_as_png(pdf_path, context_indices)
    except (ValueError, FileNotFoundError) as exc:
        sys.stderr.write(f"Error: {exc}\n")
        return 1

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.stderr.write(
            "Error: ANTHROPIC_API_KEY environment variable is not set.\n"
            "Get an API key at https://console.anthropic.com/ and export it:\n"
            '  export ANTHROPIC_API_KEY="sk-ant-..."\n'
        )
        return 1

    try:
        stream_explanation(
            png_images,
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            user_prompt=args.user_prompt,
            model=args.model,
            max_tokens=args.max_tokens,
        )
    except Exception as exc:
        sys.stderr.write(f"Error: API call failed: {exc}\n")
        return 2

    return 0
