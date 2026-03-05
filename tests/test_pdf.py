"""Tests for chalk.pdf module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from chalk.pdf import extract_pages_as_png, parse_page_spec


class TestParsePageSpec:
    def test_single_page(self) -> None:
        assert parse_page_spec("3", 10) == [2]

    def test_page_range(self) -> None:
        assert parse_page_spec("2-4", 10) == [1, 2, 3]

    def test_comma_separated(self) -> None:
        assert parse_page_spec("1,3,5", 10) == [0, 2, 4]

    def test_mixed_spec(self) -> None:
        assert parse_page_spec("1-3,5,7-9", 10) == [0, 1, 2, 4, 6, 7, 8]

    def test_deduplication(self) -> None:
        assert parse_page_spec("1,1,2", 5) == [0, 1]

    def test_single_page_range(self) -> None:
        assert parse_page_spec("3-3", 5) == [2]

    def test_whitespace_handling(self) -> None:
        assert parse_page_spec(" 1 , 3 ", 5) == [0, 2]

    def test_out_of_range_high(self) -> None:
        with pytest.raises(ValueError, match="out of range"):
            parse_page_spec("11", 10)

    def test_out_of_range_zero(self) -> None:
        with pytest.raises(ValueError, match="out of range"):
            parse_page_spec("0", 10)

    def test_reversed_range(self) -> None:
        with pytest.raises(ValueError, match="Reversed range"):
            parse_page_spec("5-3", 10)

    def test_non_integer(self) -> None:
        with pytest.raises(ValueError, match="Non-integer"):
            parse_page_spec("abc", 10)

    def test_non_integer_range(self) -> None:
        with pytest.raises(ValueError, match="Non-integer"):
            parse_page_spec("a-b", 10)

    def test_empty_segment(self) -> None:
        with pytest.raises(ValueError, match="Empty"):
            parse_page_spec("1,,3", 10)

    def test_zero_total_pages(self) -> None:
        with pytest.raises(ValueError, match="no pages"):
            parse_page_spec("1", 0)


class TestExtractPagesAsPng:
    def test_extract_single_page(self, sample_pdf: Path) -> None:
        results = extract_pages_as_png(sample_pdf, [0])
        assert len(results) == 1
        assert results[0][:8] == b"\x89PNG\r\n\x1a\n"

    def test_extract_multiple_pages(self, sample_pdf: Path) -> None:
        results = extract_pages_as_png(sample_pdf, [0, 1, 2])
        assert len(results) == 3
        for png in results:
            assert png[:8] == b"\x89PNG\r\n\x1a\n"

    def test_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="File not found"):
            extract_pages_as_png(tmp_path / "nonexistent.pdf", [0])

    def test_not_a_pdf(self, tmp_path: Path) -> None:
        txt_file = tmp_path / "not_a.pdf"
        txt_file.write_text("not a pdf")
        with pytest.raises(ValueError, match="Not a valid PDF"):
            extract_pages_as_png(txt_file, [0])

    def test_respects_max_long_edge(self, sample_pdf: Path) -> None:
        results = extract_pages_as_png(sample_pdf, [0], max_long_edge=100)
        assert len(results) == 1
        assert results[0][:8] == b"\x89PNG\r\n\x1a\n"
