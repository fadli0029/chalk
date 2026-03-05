"""Tests for chalk.llm module."""

from __future__ import annotations

import base64
from unittest.mock import MagicMock, patch

from chalk.llm import build_content_blocks, stream_explanation


class TestBuildContentBlocks:
    def test_single_image(self) -> None:
        png_data = b"\x89PNG\r\n\x1a\nfakedata"
        blocks = build_content_blocks([png_data], "Explain this.")
        assert len(blocks) == 2
        assert blocks[0]["type"] == "image"
        source = blocks[0]["source"]
        assert isinstance(source, dict)
        assert source["type"] == "base64"
        assert source["media_type"] == "image/png"
        assert source["data"] == base64.standard_b64encode(png_data).decode("ascii")
        assert blocks[1] == {"type": "text", "text": "Explain this."}

    def test_multiple_images_have_labels(self) -> None:
        images = [b"img1", b"img2", b"img3"]
        blocks = build_content_blocks(images, "Explain.")
        # 3 labels + 3 images + 1 text prompt = 7 blocks
        assert len(blocks) == 7
        assert blocks[0] == {"type": "text", "text": "Slide 1:"}
        assert blocks[1]["type"] == "image"
        assert blocks[2] == {"type": "text", "text": "Slide 2:"}
        assert blocks[3]["type"] == "image"
        assert blocks[4] == {"type": "text", "text": "Slide 3:"}
        assert blocks[5]["type"] == "image"
        assert blocks[6] == {"type": "text", "text": "Explain."}

    def test_single_image_no_label(self) -> None:
        blocks = build_content_blocks([b"img"], "prompt")
        # No "Slide 1:" label for single images
        assert blocks[0]["type"] == "image"


class TestStreamExplanation:
    @patch("chalk.llm.anthropic.Anthropic")
    def test_streams_text_to_stdout(
        self, mock_anthropic_cls: MagicMock, capsys: MagicMock
    ) -> None:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_stream.text_stream = iter(["Hello", " world"])
        mock_client.messages.stream.return_value = mock_stream

        stream_explanation(
            [b"fake_png"],
            system_prompt="You are a prof.",
            user_prompt="Explain.",
        )

        mock_client.messages.stream.assert_called_once()
        call_kwargs = mock_client.messages.stream.call_args[1]
        assert call_kwargs["model"] == "claude-sonnet-4-6"
        assert call_kwargs["max_tokens"] == 8192
        assert call_kwargs["system"] == "You are a prof."

    @patch("chalk.llm.anthropic.Anthropic")
    def test_custom_model_and_tokens(self, mock_anthropic_cls: MagicMock) -> None:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        mock_stream = MagicMock()
        mock_stream.__enter__ = MagicMock(return_value=mock_stream)
        mock_stream.__exit__ = MagicMock(return_value=False)
        mock_stream.text_stream = iter([])
        mock_client.messages.stream.return_value = mock_stream

        stream_explanation(
            [b"fake_png"],
            system_prompt="sys",
            user_prompt="usr",
            model="claude-opus-4-6",
            max_tokens=4096,
        )

        call_kwargs = mock_client.messages.stream.call_args[1]
        assert call_kwargs["model"] == "claude-opus-4-6"
        assert call_kwargs["max_tokens"] == 4096
