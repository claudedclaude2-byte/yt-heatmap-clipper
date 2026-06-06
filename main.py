#!/usr/bin/env python3
"""
Entry point. Run this first.

  python main.py                  # prints monetization guide
  python main.py --run            # execute one full viral loop cycle now
  python main.py --schedule       # start the 24/7 posting scheduler
  python main.py --dashboard      # show revenue dashboard
  python main.py --clip URL       # clip a single video URL manually
"""
import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)


def main():
    parser = argparse.ArgumentParser(description="Viral AI Revenue System")
    parser.add_argument("--run", action="store_true", help="Run one viral loop cycle")
    parser.add_argument("--schedule", action="store_true", help="Start 24/7 scheduler")
    parser.add_argument("--dashboard", action="store_true", help="Show revenue dashboard")
    parser.add_argument("--clip", metavar="URL", help="Clip a single YouTube URL")
    args = parser.parse_args()

    if args.dashboard:
        from revenue_tracker import print_dashboard
        print_dashboard()

    elif args.run:
        from viral_loop import run_one_cycle
        stats = run_one_cycle()
        print(f"\nCycle complete: {stats}")
        from revenue_tracker import print_dashboard
        print_dashboard()

    elif args.schedule:
        from scheduler import run_scheduler
        run_scheduler()

    elif args.clip:
        from clipper import clip_video
        from composer import batch_compose
        clips = clip_video(args.clip)
        if not clips:
            print("No clips produced.")
            sys.exit(1)
        composed = batch_compose(clips)
        print(f"Composed clips:")
        for p in composed:
            print(f"  {p}")

    else:
        from monetization_guide import main as guide
        guide()


if __name__ == "__main__":
    main()
