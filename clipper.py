"""
Downloads a YouTube video (best quality ≤ 1080p) and cuts viral clips
using ffmpeg based on heatmap segments.
"""
from __future__ import annotations

import logging
import subprocess
import uuid
from pathlib import Path

import yt_dlp

from config import cfg, CLIPS_DIR
from heatmap import top_clips

log = logging.getLogger(__name__)


def _ydl_opts(out_template: str) -> dict:
    return {
        "format": "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }


def download_video(url: str, dest_dir: Path = CLIPS_DIR) -> Path:
    uid = uuid.uuid4().hex[:8]
    out_template = str(dest_dir / f"raw_{uid}.%(ext)s")
    with yt_dlp.YoutubeDL(_ydl_opts(out_template)) as ydl:
        ydl.download([url])

    matches = list(dest_dir.glob(f"raw_{uid}.*"))
    if not matches:
        raise FileNotFoundError(f"Download produced no file for {url}")
    return matches[0]


def _ffmpeg_cut(src: Path, start: float, end: float, dest: Path) -> None:
    duration = end - start
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start),
        "-i", str(src),
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        str(dest),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg cut failed:\n{result.stderr}")


def clip_video(
    url: str,
    clip_duration: int | None = None,
    max_clips: int | None = None,
    min_score: float | None = None,
) -> list[Path]:
    """
    Downloads *url* and returns a list of Paths to the cut clip files.
    """
    dur = clip_duration or cfg.clip_duration_sec
    mc = max_clips or cfg.max_clips_per_video
    ms = min_score or cfg.min_heatmap_score

    log.info("Fetching heatmap for %s", url)
    windows = top_clips(url, clip_duration=dur, max_clips=mc, min_score=ms)

    if not windows:
        log.warning("No hot clips found for %s", url)
        return []

    log.info("Downloading video: %s", url)
    raw_path = download_video(url)

    clip_paths: list[Path] = []
    uid = uuid.uuid4().hex[:6]
    for i, (start, end, score) in enumerate(windows):
        out = CLIPS_DIR / f"clip_{uid}_{i}_score{score:.2f}.mp4"
        log.info("Cutting clip %d  %.1f-%.1f s  (score %.2f)", i + 1, start, end, score)
        _ffmpeg_cut(raw_path, start, end, out)
        clip_paths.append(out)

    raw_path.unlink(missing_ok=True)
    return clip_paths
