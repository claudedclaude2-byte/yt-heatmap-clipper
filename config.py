"""
Central configuration. Copy .env.example to .env and fill in your keys.
"""
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

ROOT = Path(__file__).parent
CLIPS_DIR = ROOT / "clips"
COMPOSED_DIR = ROOT / "composed"
LOGS_DIR = ROOT / "logs"
DATA_DIR = ROOT / "data"

for _d in (CLIPS_DIR, COMPOSED_DIR, LOGS_DIR, DATA_DIR):
    _d.mkdir(exist_ok=True)


@dataclass
class Config:
    # ── YouTube Data API ──────────────────────────────────────────────────────
    youtube_api_key: str = field(default_factory=lambda: os.getenv("YOUTUBE_API_KEY", ""))

    # ── TikTok (upload via TikTok for Developers) ─────────────────────────────
    tiktok_access_token: str = field(default_factory=lambda: os.getenv("TIKTOK_ACCESS_TOKEN", ""))

    # ── Instagram Graph API ───────────────────────────────────────────────────
    instagram_access_token: str = field(default_factory=lambda: os.getenv("INSTAGRAM_ACCESS_TOKEN", ""))
    instagram_account_id: str = field(default_factory=lambda: os.getenv("INSTAGRAM_ACCOUNT_ID", ""))

    # ── YouTube upload (for Shorts) ───────────────────────────────────────────
    youtube_client_secrets_file: str = field(
        default_factory=lambda: os.getenv("YOUTUBE_CLIENT_SECRETS", str(ROOT / "client_secrets.json"))
    )

    # ── Affiliate / Revenue ───────────────────────────────────────────────────
    affiliate_link: str = field(default_factory=lambda: os.getenv("AFFILIATE_LINK", ""))
    affiliate_label: str = field(default_factory=lambda: os.getenv("AFFILIATE_LABEL", "💰 Link in bio"))

    # ── Clip settings ─────────────────────────────────────────────────────────
    clip_duration_sec: int = 58          # keep under 60 s for Shorts/Reels/TikTok
    max_clips_per_video: int = 3
    min_heatmap_score: float = 0.75      # only clip segments with replay score ≥ this

    # ── Niche / content ───────────────────────────────────────────────────────
    niches: list = field(default_factory=lambda: [
        "money making tips 2024",
        "passive income ideas",
        "AI tools that pay you",
        "side hustle ideas",
        "how to make money online",
    ])

    # ── Posting schedule (24-h hours, UTC) ───────────────────────────────────
    post_hours_utc: list = field(default_factory=lambda: [7, 12, 18, 21])

    # ── Viral loop ────────────────────────────────────────────────────────────
    videos_per_niche_per_run: int = 5
    days_to_scale: int = 4


cfg = Config()
