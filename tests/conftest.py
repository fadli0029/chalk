"""Shared test fixtures."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pymupdf
import pytest

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Create a minimal 3-page PDF for testing."""
    pdf_path = tmp_path / "test.pdf"
    doc = pymupdf.open()
    for i in range(3):
        page = doc.new_page(width=612, height=792)
        text_point = pymupdf.Point(72, 72)
        page.insert_text(text_point, f"Page {i + 1}")
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path
