#!/usr/bin/env python3
"""Compute due dates and flag overdue/upcoming FOIA requests from a tracked-requests JSON file.

Usage:
    python3 extension_tracker.py tracked_requests.sample.json
    python3 extension_tracker.py tracked_requests.sample.json --within-days 7
"""
import argparse
import json
import sys
from datetime import date, datetime, timedelta


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def compute_due_date(entry: dict) -> date:
    submitted = parse_date(entry["date_submitted"])
    days = entry["statutory_response_days"]
    if entry.get("extension_granted_days"):
        days += entry["extension_granted_days"]
    return submitted + timedelta(days=days)


def status_for(entry: dict, today: date, within_days: int) -> str:
    if entry.get("status") in ("closed", "produced", "appeal_resolved"):
        return "done"
    due = compute_due_date(entry)
    if due < today:
        return "overdue"
    if due <= today + timedelta(days=within_days):
        return "due_soon"
    return "tracking"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tracked_file", help="Path to a tracked-requests JSON file")
    parser.add_argument("--within-days", type=int, default=7, help="Window for 'due soon' (default 7)")
    parser.add_argument("--today", help="Override today's date (YYYY-MM-DD), for testing")
    args = parser.parse_args()

    with open(args.tracked_file) as f:
        data = json.load(f)

    today = parse_date(args.today) if args.today else date.today()

    rows = []
    for entry in data["requests"]:
        due = compute_due_date(entry)
        rows.append((status_for(entry, today, args.within_days), due, entry))

    order = {"overdue": 0, "due_soon": 1, "tracking": 2, "done": 3}
    rows.sort(key=lambda r: (order[r[0]], r[1]))

    print(f"FOIA MACHINE -- EXTENSION/DEADLINE REPORT ({today.isoformat()})")
    print("=" * 70)
    for status, due, entry in rows:
        if status == "done":
            continue
        label = {"overdue": "OVERDUE", "due_soon": "DUE SOON", "tracking": "tracking"}[status]
        print(f"[{label:9}] {entry['agency']:35} due {due.isoformat()}  ref={entry['reference']}")

    overdue_count = sum(1 for s, _, _ in rows if s == "overdue")
    due_soon_count = sum(1 for s, _, _ in rows if s == "due_soon")
    print("=" * 70)
    print(f"Overdue: {overdue_count}  Due within {args.within_days}d: {due_soon_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
