"""
Generates viral short-form captions using the Claude API.
Falls back to template captions if ANTHROPIC_API_KEY is not set.
"""
from __future__ import annotations

import os
import logging
from typing import Optional

log = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        try:
            import anthropic
            key = os.getenv("ANTHROPIC_API_KEY", "")
            if key:
                _client = anthropic.Anthropic(api_key=key)
        except ImportError:
            log.warning("anthropic package not installed — using template captions")
    return _client


TEMPLATES = [
    "{title} 🔥 #shorts #viral #money",
    "This is CRAZY 😮 {title} #sidehustle #shorts",
    "Nobody talks about this 👀 {title} #makemoneyonline #shorts",
    "I made $500 doing THIS → {title} #passiveincome #shorts",
    "Watch this before they delete it 🚨 {title} #shorts",
]


def generate_caption(title: str, niche: str, index: int = 0) -> str:
    """Returns a viral caption string for the given video."""
    client = _get_client()

    if client is not None:
        try:
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=120,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Write a single viral TikTok/YouTube Shorts caption (max 120 chars) "
                        f"for a clip about: '{title}' in the '{niche}' niche. "
                        f"Include 2-3 relevant hashtags. Use curiosity, urgency, or FOMO. "
                        f"Output ONLY the caption text, nothing else."
                    ),
                }],
            )
            caption = msg.content[0].text.strip()
            if caption:
                return caption
        except Exception as e:
            log.warning("Claude caption failed: %s", e)

    # Template fallback
    tmpl = TEMPLATES[index % len(TEMPLATES)]
    short_title = title[:60] if len(title) > 60 else title
    return tmpl.format(title=short_title)
