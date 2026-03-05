"""Tests for arche.extract module."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

from arche.extract import extract_to_dir, run_extract

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class TestExtractToDir:
    """Tests for extract_to_dir()."""

    def test_single_page(self, sample_pdf: Path, tmp_path: Path) -> None:
        out = tmp_path / "out"
        paths = extract_to_dir(sample_pdf, "1", out)
        assert len(paths) == 1
        assert paths[0].name == "slide_001.png"
        assert paths[0].read_bytes()[:8] == PNG_MAGIC

    def test_multi_page(self, sample_pdf: Path, tmp_path: Path) -> None:
        out = tmp_path / "out"
        paths = extract_to_dir(sample_pdf, "1-3", out)
        assert len(paths) == 3
        assert [p.name for p in paths] == [
            "slide_001.png",
            "slide_002.png",
            "slide_003.png",
        ]
        for p in paths:
            assert p.read_bytes()[:8] == PNG_MAGIC

    def test_creates_output_dir(self, sample_pdf: Path, tmp_path: Path) -> None:
        out = tmp_path / "nested" / "dir"
        paths = extract_to_dir(sample_pdf, "2", out)
        assert out.is_dir()
        assert len(paths) == 1

    def test_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="File not found"):
            extract_to_dir(tmp_path / "nope.pdf", "1", tmp_path / "out")

    def test_invalid_page_spec(self, sample_pdf: Path, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="out of range"):
            extract_to_dir(sample_pdf, "99", tmp_path / "out")


class TestRunExtract:
    """Tests for run_extract() CLI wrapper."""

    def test_success_with_output_dir(
        self, sample_pdf: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        out = tmp_path / "out"
        result = run_extract([str(sample_pdf), "1-2", "--output-dir", str(out)])
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert lines[0] == str(out)
        assert len(lines) == 3  # dir + 2 files

    def test_success_temp_dir(
        self, sample_pdf: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        result = run_extract([str(sample_pdf), "1"])
        assert result == 0
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert "arche-slides-" in lines[0]
        shutil.rmtree(lines[0], ignore_errors=True)

    def test_cleanup(self, sample_pdf: Path) -> None:
        target = Path(tempfile.mkdtemp(prefix="arche-slides-"))
        (target / "file.txt").write_text("data")

        result = run_extract([str(sample_pdf), "1", "--cleanup", str(target)])
        assert result == 0
        assert not target.exists()

    def test_cleanup_rejects_arbitrary_path(
        self, tmp_path: Path, sample_pdf: Path
    ) -> None:
        target = tmp_path / "to_remove"
        target.mkdir()
        result = run_extract([str(sample_pdf), "1", "--cleanup", str(target)])
        assert result == 1
        assert target.exists()

    def test_cleanup_rejects_non_arche_temp_dir(self, sample_pdf: Path) -> None:
        target = Path(tempfile.mkdtemp(prefix="other-"))
        try:
            result = run_extract([str(sample_pdf), "1", "--cleanup", str(target)])
            assert result == 1
            assert target.exists()
        finally:
            shutil.rmtree(target, ignore_errors=True)

    def test_error_missing_pdf(self, tmp_path: Path) -> None:
        result = run_extract([str(tmp_path / "nope.pdf"), "1"])
        assert result == 1

    def test_error_invalid_pages(self, sample_pdf: Path) -> None:
        result = run_extract([str(sample_pdf), "99"])
        assert result == 1
