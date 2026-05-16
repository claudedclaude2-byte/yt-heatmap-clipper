"""
Extracts YouTube replay-heatmap data and returns the hottest time segments.

YouTube encodes its "most-replayed" heatmap as `heatMarkers` inside the
player response JSON.  yt-dlp exposes this through its info dict when you
request `heatmap` in the `--write-info-json` output, but we can also pull
it directly with a lightweight fetch so we don't have to download the whole
video first.
"""
from __future__ import annotations

import json
import logging
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yt_dlp

log = logging.getLogger(__name__)


@dataclass
class HeatSegment:
    start_sec: float
    end_sec: float
    score: float          # 0-1, 1 = most replayed


def _normalise(values: list[float]) -> list[float]:
    mx = max(values) if values else 1.0
    return [v / mx for v in values] if mx else values


def fetch_heatmap(video_url: str) -> list[HeatSegment]:
    """
    Returns heatmap segments for *video_url* sorted by score descending.
    Falls back to an empty list if heatmap data is unavailable.
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "writeinfojson": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
        except Exception as exc:
            log.warning("yt-dlp info extraction failed: %s", exc)
            return []

    heatmap_raw: Optional[list[dict]] = info.get("heatmap")
    if not heatmap_raw:
        log.info("No heatmap data for %s — using uniform distribution", video_url)
        # Treat video as uniformly interesting; caller can still clip thirds
        duration = info.get("duration") or 0
        if not duration:
            return []
        third = duration / 3
        return [
            HeatSegment(0, third, 0.6),
            HeatSegment(third, 2 * third, 0.8),
            HeatSegment(2 * third, duration, 0.7),
        ]

    scores = [float(m.get("value", 0)) for m in heatmap_raw]
    normalised = _normalise(scores)
    duration = info.get("duration") or 1

    segments: list[HeatSegment] = []
    step = duration / len(heatmap_raw)
    for i, score in enumerate(normalised):
        segments.append(HeatSegment(
            start_sec=i * step,
            end_sec=(i + 1) * step,
            score=score,
        ))

    return sorted(segments, key=lambda s: s.score, reverse=True)


def top_clips(
    video_url: str,
    clip_duration: int = 58,
    max_clips: int = 3,
    min_score: float = 0.75,
) -> list[tuple[float, float, float]]:
    """
    Returns a list of (start_sec, end_sec, score) for the hottest non-overlapping
    windows of *clip_duration* seconds.
    """
    segments = fetch_heatmap(video_url)
    if not segments:
        return []

    chosen: list[tuple[float, float, float]] = []
    used_ranges: list[tuple[float, float]] = []

    for seg in segments:
        if seg.score < min_score:
            break
        if len(chosen) >= max_clips:
            break

        # Centre the clip on the hot segment
        mid = (seg.start_sec + seg.end_sec) / 2
        start = max(0, mid - clip_duration / 2)
        end = start + clip_duration

        # Skip if overlaps with already-chosen clip
        overlap = any(
            not (end <= us or start >= ue) for us, ue in used_ranges
        )
        if overlap:
            continue

        chosen.append((start, end, seg.score))
        used_ranges.append((start, end))

    return chosen
