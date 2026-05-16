"""
Tracks posts, estimated reach, and revenue in a local JSON ledger.
Also prints a daily dashboard to stdout.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Optional

from config import DATA_DIR

log = logging.getLogger(__name__)
LEDGER_PATH = DATA_DIR / "ledger.json"


def _load() -> dict:
    if LEDGER_PATH.exists():
        with open(LEDGER_PATH) as f:
            return json.load(f)
    return {"posts": [], "revenue_events": []}


def _save(data: dict) -> None:
    with open(LEDGER_PATH, "w") as f:
        json.dump(data, f, indent=2, default=str)


def record_post(
    platform: str,
    caption: str,
    video_path: str,
    result_id: Optional[str],
    source_url: str,
    niche: str,
) -> None:
    data = _load()
    data["posts"].append({
        "ts": datetime.utcnow().isoformat(),
        "platform": platform,
        "caption": caption,
        "video": video_path,
        "result_id": result_id,
        "source_url": source_url,
        "niche": niche,
    })
    _save(data)


def record_revenue(amount_usd: float, source: str, notes: str = "") -> None:
    data = _load()
    data["revenue_events"].append({
        "ts": datetime.utcnow().isoformat(),
        "amount_usd": amount_usd,
        "source": source,
        "notes": notes,
    })
    _save(data)
    log.info("💰 Revenue recorded: $%.2f from %s", amount_usd, source)


def daily_summary(day: Optional[date] = None) -> dict:
    today = (day or date.today()).isoformat()
    data = _load()

    posts_today = [p for p in data["posts"] if p["ts"].startswith(today)]
    revenue_today = sum(
        r["amount_usd"] for r in data["revenue_events"] if r["ts"].startswith(today)
    )
    revenue_total = sum(r["amount_usd"] for r in data["revenue_events"])

    by_platform: dict[str, int] = {}
    for p in posts_today:
        by_platform[p["platform"]] = by_platform.get(p["platform"], 0) + 1

    return {
        "date": today,
        "posts_today": len(posts_today),
        "by_platform": by_platform,
        "revenue_today_usd": revenue_today,
        "revenue_total_usd": revenue_total,
    }


def print_dashboard() -> None:
    s = daily_summary()
    total_posts = len(_load()["posts"])
    print("\n" + "═" * 50)
    print("  VIRAL AI REVENUE DASHBOARD")
    print("═" * 50)
    print(f"  Date          : {s['date']}")
    print(f"  Posts today   : {s['posts_today']}")
    print(f"  Total posts   : {total_posts}")
    print(f"  By platform   : {s['by_platform']}")
    print(f"  Revenue today : ${s['revenue_today_usd']:.2f}")
    print(f"  Revenue total : ${s['revenue_total_usd']:.2f}")
    print("═" * 50 + "\n")
