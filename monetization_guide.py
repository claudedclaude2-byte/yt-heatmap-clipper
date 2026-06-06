"""
Prints the exact monetization playbook for Days 1-4.
Run:  python monetization_guide.py
"""

GUIDE = """
╔══════════════════════════════════════════════════════════════════════╗
║          VIRAL AI REVENUE SYSTEM — MONETIZATION PLAYBOOK            ║
╚══════════════════════════════════════════════════════════════════════╝

REVENUE STREAMS (fastest to slowest to activate)
─────────────────────────────────────────────────
 A. Affiliate links (Day 1)
    • Amazon Associates, ClickBank, Digistore24, Impact.com
    • Put YOUR link in bio on every platform
    • Set AFFILIATE_LINK= in .env — the system bakes a CTA into every clip

 B. Digital product (Day 2-3)
    • Create a $27 PDF/Notion template on Gumroad
      e.g. "7 AI Tools That Pay You $500/day (PDF)"
    • One landing page, zero inventory, instant delivery
    • Link all profiles to it

 C. TikTok / YouTube Shorts creator funds (passive, Day 3+)
    • TikTok Series: paywall your best content at $2-$5/view
    • YouTube Partner Program: 1 000 subs + 4 000 watch-hours OR
      500 subs + 3 public Shorts in last 90 days (lower tier)

 D. Sponsorship DMs (Day 4+)
    • At 1k+ followers DM tool brands in your niche
    • Typical rate: $50-$200/post for micro-influencers

═══════════════════════════════════════════════════════════════════════

DAY-BY-DAY RAMP
────────────────
 DAY 1 — Target: $0-$50
  ✓ Set up accounts on TikTok, YouTube, Instagram
  ✓ Add affiliate link to all bios
  ✓ Run:  python scheduler.py --now
  ✓ System posts 3-5 clips per platform automatically
  ✓ Promote clips in 2-3 relevant Facebook Groups / Reddit threads
    (share value, not spam — link in comments if allowed)

 DAY 2 — Target: $50-$200
  ✓ Scheduler runs 4x per day automatically
  ✓ Identify your top-performing clip (most views/engagement)
  ✓ Duplicate that NICHE in config.py — go deeper
  ✓ Create Gumroad product ($17-$27 PDF) and update AFFILIATE_LINK

 DAY 3 — Target: $200-$500
  ✓ 12-16 clips live across platforms
  ✓ Engage in comments — ask a question → replies → algorithmic boost
  ✓ Repurpose: download your own best TikTok → repost to Shorts & Reels
  ✓ Add faceless AI voiceover with ElevenLabs / TTS for longer clips

 DAY 4 — Target: $500-$1 000+
  ✓ Scale: add 2 more niches to config.py niches list
  ✓ Add second affiliate program (higher CPA = more $$)
  ✓ DM 10 brands in your niche offering a paid post deal
  ✓ Enable YouTube monetisation if threshold met

═══════════════════════════════════════════════════════════════════════

VIRAL LOOP MECHANICS
─────────────────────
  Trending video (10M+ views)
       │
       ▼
  Heatmap → hottest 58-second segment extracted
       │
       ▼
  Hook text + progress bar + affiliate CTA baked in
       │
       ▼
  Posted to TikTok + YouTube Shorts + Instagram Reels simultaneously
       │
       ├─ If >500 views in 1 h → comment to boost
       ├─ Save to Drafts → re-post in 3 days (TikTok allows this)
       └─ Add to Google Sheet to track CTR on affiliate link

  ALGORITHM HACK: Post within 30 min of your platform's peak hours:
    TikTok     → 7am, 12pm, 7pm, 9pm (local to target audience)
    YouTube    → 12pm-3pm Tue/Wed/Thu
    Instagram  → 9am-11am, 6pm-8pm

═══════════════════════════════════════════════════════════════════════

SETUP CHECKLIST
────────────────
 [ ] cp .env.example .env && fill in keys
 [ ] Set AFFILIATE_LINK in .env
 [ ] Create TikTok Developer account → get access token
 [ ] Enable YouTube Data API → download client_secrets.json
 [ ] pip install -r requirements.txt
 [ ] sudo apt install ffmpeg  (or brew install ffmpeg on Mac)
 [ ] python scheduler.py --now   ← first run

═══════════════════════════════════════════════════════════════════════
"""


def main():
    print(GUIDE)


if __name__ == "__main__":
    main()
