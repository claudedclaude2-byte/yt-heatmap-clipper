"""
Finds trending YouTube videos in configured niches using the YouTube Data API v3.
Falls back to yt-dlp search if no API key is set.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import requests
import yt_dlp

from config import cfg

log = logging.getLogger(__name__)

YT_SEARCH = "https://www.googleapis.com/youtube/v3/search"
YT_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"


@dataclass
class VideoResult:
    url: str
    title: str
    view_count: int
    duration_sec: int
    channel: str


def _api_search(query: str, max_results: int = 10) -> list[VideoResult]:
    if not cfg.youtube_api_key:
        return []

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "videoDuration": "medium",   # 4–20 min — good source material
        "order": "viewCount",
        "maxResults": max_results,
        "key": cfg.youtube_api_key,
    }
    r = requests.get(YT_SEARCH, params=params, timeout=15)
    r.raise_for_status()
    items = r.json().get("items", [])
    video_ids = [i["id"]["videoId"] for i in items]
    if not video_ids:
        return []

    # Fetch statistics + contentDetails in one batch call
    stats_r = requests.get(YT_VIDEOS, params={
        "part": "statistics,contentDetails,snippet",
        "id": ",".join(video_ids),
        "key": cfg.youtube_api_key,
    }, timeout=15)
    stats_r.raise_for_status()

    results = []
    for v in stats_r.json().get("items", []):
        vid_id = v["id"]
        stats = v.get("statistics", {})
        snippet = v.get("snippet", {})
        cd = v.get("contentDetails", {})

        view_count = int(stats.get("viewCount", 0))
        duration = _iso8601_to_sec(cd.get("duration", "PT0S"))

        results.append(VideoResult(
            url=f"https://www.youtube.com/watch?v={vid_id}",
            title=snippet.get("title", ""),
            view_count=view_count,
            duration_sec=duration,
            channel=snippet.get("channelTitle", ""),
        ))

    return sorted(results, key=lambda v: v.view_count, reverse=True)


def _ydl_search(query: str, max_results: int = 5) -> list[VideoResult]:
    """Fallback: use yt-dlp's ytsearch without an API key."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    search_query = f"ytsearch{max_results}:{query}"
    results = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(search_query, download=False)
        except Exception as e:
            log.warning("yt-dlp search failed: %s", e)
            return []
        for entry in (info.get("entries") or []):
            if not entry:
                continue
            results.append(VideoResult(
                url=entry.get("webpage_url") or f"https://www.youtube.com/watch?v={entry['id']}",
                title=entry.get("title", ""),
                view_count=entry.get("view_count") or 0,
                duration_sec=entry.get("duration") or 0,
                channel=entry.get("uploader") or "",
            ))
    return results


def _iso8601_to_sec(s: str) -> int:
    """Convert PT4M30S → 270."""
    import re
    h = int((re.search(r"(\d+)H", s) or [0, 0])[1])
    m = int((re.search(r"(\d+)M", s) or [0, 0])[1])
    sec = int((re.search(r"(\d+)S", s) or [0, 0])[1])
    return h * 3600 + m * 60 + sec


def find_trending(
    niches: Optional[list[str]] = None,
    per_niche: Optional[int] = None,
) -> list[VideoResult]:
    """
    Returns a combined list of trending VideoResults across all configured niches.
    Sorted by view count descending. Deduped by URL.
    """
    queries = niches or cfg.niches
    n = per_niche or cfg.videos_per_niche_per_run

    seen: set[str] = set()
    all_results: list[VideoResult] = []

    for q in queries:
        log.info("Searching niche: %s", q)
        found = _api_search(q, max_results=n) or _ydl_search(q, max_results=n)
        for r in found:
            if r.url not in seen and r.duration_sec >= 60:
                seen.add(r.url)
                all_results.append(r)

    return sorted(all_results, key=lambda v: v.view_count, reverse=True)
