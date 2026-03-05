"""Claude API interaction for lecture slide explanations."""

from __future__ import annotations

__all__ = ["build_content_blocks", "stream_explanation"]

import base64
import sys

import anthropic
from anthropic.types import ImageBlockParam, TextBlockParam

ContentBlock = TextBlockParam | ImageBlockParam


def build_content_blocks(
    png_images: list[bytes],
    user_prompt: str,
) -> list[ContentBlock]:
    """Build message content blocks with base64-encoded images and a text prompt.

    Images are placed before the text prompt per Anthropic's recommendation.
    When multiple images are provided, each is labeled with "Slide N:".
    """
    blocks: list[ContentBlock] = []
    multi = len(png_images) > 1

    for i, png_data in enumerate(png_images):
        if multi:
            blocks.append(
                TextBlockParam(
                    type="text",
                    text=f"Slide {i + 1}:",
                )
            )
        blocks.append(
            ImageBlockParam(
                type="image",
                source={
                    "type": "base64",
                    "media_type": "image/png",
                    "data": base64.standard_b64encode(png_data).decode("ascii"),
                },
            )
        )

    blocks.append(TextBlockParam(type="text", text=user_prompt))
    return blocks


def stream_explanation(
    png_images: list[bytes],
    *,
    system_prompt: str,
    user_prompt: str,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 8192,
) -> None:
    """Stream a lecture explanation from Claude to stdout.

    Creates an Anthropic client (reads ANTHROPIC_API_KEY from env),
    sends the images and prompt, and writes text chunks to stdout as
    they arrive.
    """
    client = anthropic.Anthropic()
    content = build_content_blocks(png_images, user_prompt)

    with client.messages.stream(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": content}],
    ) as stream:
        for text in stream.text_stream:
            sys.stdout.write(text)
            sys.stdout.flush()
    sys.stdout.write("\n")
    sys.stdout.flush()
