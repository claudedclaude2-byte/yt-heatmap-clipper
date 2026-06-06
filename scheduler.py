"""
Posting scheduler — runs the full viral loop on a cron-like timer.
Designed to run as a long-lived process (screen / tmux / systemd).

Usage:
    python scheduler.py              # runs on cfg.post_hours_utc schedule
    python scheduler.py --now        # run one iteration immediately then exit
"""
from __future__ import annotations

import argparse
import logging
import time
from datetime import datetime, timezone

from config import cfg
from viral_loop import run_one_cycle
from revenue_tracker import print_dashboard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def _minutes_until_next_slot(hours_utc: list[int]) -> float:
    now = datetime.now(timezone.utc)
    now_min = now.hour * 60 + now.minute
    slots_min = sorted(h * 60 for h in hours_utc)

    for s in slots_min:
        if s > now_min:
            return s - now_min

    # wrap to next day
    return (24 * 60 - now_min) + slots_min[0]


def run_scheduler() -> None:
    log.info("Scheduler started — posting slots (UTC): %s", cfg.post_hours_utc)
    while True:
        wait = _minutes_until_next_slot(cfg.post_hours_utc)
        log.info("Next post in %.0f minutes", wait)
        time.sleep(wait * 60)

        try:
            run_one_cycle()
        except Exception as exc:
            log.error("Cycle failed: %s", exc, exc_info=True)

        print_dashboard()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--now", action="store_true", help="Run one cycle immediately")
    args = parser.parse_args()

    if args.now:
        run_one_cycle()
        print_dashboard()
    else:
        run_scheduler()
