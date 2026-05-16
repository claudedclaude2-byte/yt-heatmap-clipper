"""
Post-production: adds captions, hook text, progress bar, affiliate CTA,
and crops/pads to 9:16 vertical for Shorts/Reels/TikTok.
"""
from __future__ import annotations

import logging
import subprocess
import uuid
from pathlib import Path
from typing import Optional

from config import cfg, COMPOSED_DIR

log = logging.getLogger(__name__)

# Hook lines proven to drive watch-time on short-form video
HOOKS = [
    "Nobody talks about this 🤫",
    "This changed everything for me 👇",
    "Stop scrolling — this is important",
    "I wish I knew this sooner...",
    "They don't want you to see this",
    "This made people $500 in a day",
    "Most people quit right before this",
    "Wait until the end 👀",
]


def _hook_line(index: int = 0) -> str:
    return HOOKS[index % len(HOOKS)]


def _build_drawtext(text: str, y_expr: str, fontsize: int = 52, color: str = "white") -> str:
    escaped = text.replace("'", "\\'").replace(":", "\\:")
    return (
        f"drawtext=text='{escaped}'"
        f":fontsize={fontsize}"
        f":fontcolor={color}"
        f":borderw=3:bordercolor=black"
        f":x=(w-text_w)/2"
        f":y={y_expr}"
        f":font=DejaVu Sans Bold"
    )


def compose(
    clip_path: Path,
    hook_index: int = 0,
    caption: Optional[str] = None,
    add_progress_bar: bool = True,
) -> Path:
    """
    Takes a raw MP4 clip and returns a composed, vertical, ready-to-post MP4.
    """
    out = COMPOSED_DIR / f"composed_{uuid.uuid4().hex[:8]}.mp4"

    hook = _hook_line(hook_index)
    cta = cfg.affiliate_label if cfg.affiliate_link else "Follow for more 🔥"

    # Build a chain of ffmpeg video filters:
    # 1. crop + pad to 9:16  2. hook text top  3. CTA bottom  4. progress bar
    vf_parts = [
        # Vertical crop: take centre 9:16 from whatever source aspect ratio
        "scale=iw*min(1080/iw\\,1920/ih):ih*min(1080/iw\\,1920/ih),"
        "pad=1080:1920:(1080-iw)/2:(1920-ih)/2:black",
    ]

    # Hook at top
    vf_parts.append(_build_drawtext(hook, "80", fontsize=56))

    # Optional middle caption
    if caption:
        vf_parts.append(_build_drawtext(caption, "(h-text_h)/2", fontsize=44, color="yellow"))

    # CTA at bottom
    vf_parts.append(_build_drawtext(cta, "h-120", fontsize=46, color="#FFD700"))

    # Progress bar: thin green bar growing left→right over the clip duration
    if add_progress_bar:
        vf_parts.append(
            "drawbox=x=0:y=h-8:w=iw*t/duration:h=8:color=lime:t=fill"
        )

    vf_chain = ",".join(vf_parts)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(clip_path),
        "-vf", vf_chain,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(out),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg compose failed:\n{result.stderr}")

    log.info("Composed → %s", out)
    return out


def batch_compose(clip_paths: list[Path], caption: Optional[str] = None) -> list[Path]:
    return [
        compose(p, hook_index=i, caption=caption)
        for i, p in enumerate(clip_paths)
    ]
