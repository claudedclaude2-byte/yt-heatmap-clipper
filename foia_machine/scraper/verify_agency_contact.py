#!/usr/bin/env python3
"""Verify an agency's FOIA/records-request contact info by rendering the live page.

Some agency sites obfuscate their contact email from plain HTTP fetches/search-result
snippets (Cloudflare email protection, JS-rendered contact blocks, etc. -- this is what
happened with the Arizona DPS lookup in agencies.json). Rendering the page in a real
browser resolves that; Camoufox is used here for its stealth fingerprint so verification
runs don't get blocked as a bot.

SETUP (one-time, needs normal internet access -- see note below):
    pip install camoufox[geoip]
    python3 -m camoufox fetch

NETWORK NOTE: this script cannot run inside a network-sandboxed session with an
allowlisted egress proxy (confirmed while building this: github.com and arbitrary
external sites both return 403 there, so `camoufox fetch` can't even download the
browser binary). Run it somewhere with normal internet access -- e.g. wherever the
FOIA Machine's own cron job already runs.

Usage:
    python3 verify_agency_contact.py <url> [--agency-id ID]
"""
import argparse
import json
import re
import sys

from camoufox.sync_api import Camoufox

MAILTO_RE = re.compile(r"mailto:([^\"'?]+)")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def extract_contacts(url: str) -> dict:
    with Camoufox(headless=True) as browser:
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        html = page.content()
        text = page.inner_text("body")

    mailtos = sorted(set(MAILTO_RE.findall(html)))
    emails_in_text = sorted(set(EMAIL_RE.findall(text)))
    return {"url": url, "mailto_links": mailtos, "emails_in_text": emails_in_text}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url")
    parser.add_argument("--agency-id", help="If set, print a suggested agencies.json patch for this id")
    args = parser.parse_args()

    result = extract_contacts(args.url)
    print(json.dumps(result, indent=2))

    if args.agency_id:
        best_guess = (result["mailto_links"] or result["emails_in_text"] or [None])[0]
        print(f"\nSuggested patch for agencies.json id={args.agency_id!r} (review before applying):")
        print(json.dumps({
            "submission_email": best_guess,
            "notes": f"Verified via {args.url} on {{today's date}} -- confirm before use.",
        }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
