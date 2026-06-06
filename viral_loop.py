"""
The core viral loop:
  1. Find trending videos across configured niches
  2. Extract heatmap → cut hot clips
  3. Compose to vertical short-form
  4. Generate AI captions
  5. Upload to all platforms
  6. Record in ledger
"""
from __future__ import annotations

import logging
from pathlib import Path

from config import cfg
from trend_finder import find_trending, VideoResult
from clipper import clip_video
from composer import batch_compose
from caption_ai import generate_caption
from uploader import upload_all
from revenue_tracker import record_post

log = logging.getLogger(__name__)


def _process_video(video: VideoResult, niche: str) -> int:
    """Returns the number of clips successfully posted."""
    log.info("Processing: %s (%d views)", video.title, video.view_count)

    try:
        raw_clips = clip_video(video.url)
    except Exception as e:
        log.error("Clip failed for %s: %s", video.url, e)
        return 0

    if not raw_clips:
        log.warning("No clips produced for %s", video.url)
        return 0

    try:
        caption = generate_caption(video.title, niche)
        composed = batch_compose(raw_clips, caption=None)  # hook text is baked in by composer
    except Exception as e:
        log.error("Compose failed: %s", e)
        return 0

    posted = 0
    for i, comp_path in enumerate(composed):
        cap = generate_caption(video.title, niche, index=i)
        try:
            results = upload_all(comp_path, cap)
        except Exception as e:
            log.error("Upload failed: %s", e)
            continue

        for platform, result_id in results.items():
            record_post(
                platform=platform,
                caption=cap,
                video_path=str(comp_path),
                result_id=result_id,
                source_url=video.url,
                niche=niche,
            )
            if result_id:
                posted += 1
                log.info("✅ Posted to %s: %s", platform, result_id)

    # Clean up composed files to save disk space
    for p in composed:
        try:
            p.unlink()
        except Exception:
            pass

    return posted


def run_one_cycle(
    niches: list[str] | None = None,
    per_niche: int | None = None,
) -> dict:
    """
    Runs one full cycle of the viral loop.
    Returns summary stats.
    """
    queries = niches or cfg.niches
    n = per_niche or cfg.videos_per_niche_per_run

    log.info("=== VIRAL LOOP CYCLE START ===")
    log.info("Niches: %s | Videos per niche: %d", queries, n)

    videos = find_trending(niches=queries, per_niche=n)
    log.info("Found %d candidate videos", len(videos))

    total_posted = 0
    for video in videos:
        # determine which niche this video matched (best-effort)
        niche = queries[0]
        for q in queries:
            kw = q.split()[0].lower()
            if kw in video.title.lower() or kw in video.channel.lower():
                niche = q
                break

        count = _process_video(video, niche)
        total_posted += count

    log.info("=== CYCLE COMPLETE — %d clips posted ===", total_posted)
    return {"videos_processed": len(videos), "clips_posted": total_posted}
