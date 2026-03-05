"""Tests for arche package entry point."""

from __future__ import annotations

from unittest.mock import patch

from arche import main


@patch("arche.run", return_value=0)
def test_main_calls_run_and_exits(mock_run: object) -> None:
    with patch("arche.sys.exit") as mock_exit:
        main()
        mock_exit.assert_called_once_with(0)
