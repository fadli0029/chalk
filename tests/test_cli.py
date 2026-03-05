"""Tests for arche.cli module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from arche.cli import run


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure ANTHROPIC_API_KEY is set for all CLI tests."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")


class TestRun:
    def test_file_not_found(self, tmp_path: Path, capsys: MagicMock) -> None:
        result = run([str(tmp_path / "nonexistent.pdf"), "1"])
        assert result == 1

    def test_invalid_page_spec(self, sample_pdf: Path) -> None:
        result = run([str(sample_pdf), "0"])
        assert result == 1

    def test_page_out_of_range(self, sample_pdf: Path) -> None:
        result = run([str(sample_pdf), "99"])
        assert result == 1

    def test_missing_api_key(
        self, sample_pdf: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY")
        result = run([str(sample_pdf), "1"])
        assert result == 1

    @patch("arche.cli.stream_explanation")
    def test_success(self, mock_stream: MagicMock, sample_pdf: Path) -> None:
        result = run([str(sample_pdf), "1"])
        assert result == 0
        mock_stream.assert_called_once()

    @patch("arche.cli.stream_explanation")
    def test_success_range(self, mock_stream: MagicMock, sample_pdf: Path) -> None:
        result = run([str(sample_pdf), "1-3"])
        assert result == 0
        mock_stream.assert_called_once()

    @patch("arche.cli.stream_explanation", side_effect=RuntimeError("API down"))
    def test_api_error(self, mock_stream: MagicMock, sample_pdf: Path) -> None:
        result = run([str(sample_pdf), "1"])
        assert result == 2

    @patch("arche.cli.stream_explanation")
    def test_custom_model(self, mock_stream: MagicMock, sample_pdf: Path) -> None:
        result = run([str(sample_pdf), "1", "--model", "claude-opus-4-6"])
        assert result == 0
        call_kwargs = mock_stream.call_args[1]
        assert call_kwargs["model"] == "claude-opus-4-6"

    @patch("arche.cli.stream_explanation")
    def test_custom_prompt(self, mock_stream: MagicMock, sample_pdf: Path) -> None:
        result = run([str(sample_pdf), "1", "--prompt", "Summarize."])
        assert result == 0
        call_kwargs = mock_stream.call_args[1]
        assert call_kwargs["user_prompt"] == "Summarize."

    @patch("arche.cli.stream_explanation")
    def test_custom_max_tokens(self, mock_stream: MagicMock, sample_pdf: Path) -> None:
        result = run([str(sample_pdf), "1", "--max-tokens", "4096"])
        assert result == 0
        call_kwargs = mock_stream.call_args[1]
        assert call_kwargs["max_tokens"] == 4096
