"""chalk: Lecture slide explainer CLI powered by Claude."""

from __future__ import annotations

import sys

from chalk.cli import run

__all__ = ["main", "run"]


def main() -> None:
    """Entry point for the chalk CLI."""
    sys.exit(run())
