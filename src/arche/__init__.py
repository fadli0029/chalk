"""arche: Lecture slide explainer CLI powered by Claude."""

from __future__ import annotations

import sys

from arche.cli import run

__all__ = ["main", "run"]


def main() -> None:
    """Entry point for the arche CLI."""
    sys.exit(run())
