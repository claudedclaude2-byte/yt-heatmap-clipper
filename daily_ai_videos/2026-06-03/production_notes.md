# Production Notes — June 3, 2026

## Setup
- MoneyPrinterTurbo cloned from GitHub (harry0703/MoneyPrinterTurbo)
- Pexels/Pixabay API keys not configured → using custom Python pipeline
- edge_tts (Microsoft): blocked by environment proxy (403 on WSS endpoint)
- Switched to espeak-ng (local, offline TTS, no network needed)
- Video generation: moviepy + PIL (no external video API needed)
- FFmpeg: bundled via imageio_ffmpeg (v7.0.2)

## Technical Stack
- Python 3.11.15
- moviepy 2.2.1
- Pillow (PIL) 11.3.0
- espeak-ng 1.51 (local TTS)
- FFmpeg 7.0.2 (via imageio_ffmpeg)
- Fonts: DejaVu Sans Bold (system fonts)

## Why Custom Pipeline vs MoneyPrinterTurbo API
MoneyPrinterTurbo requires:
1. Pexels or Pixabay API key for stock video (not configured)
2. LLM API key for script generation (can bypass with manual script)
3. Working TTS endpoint (edge_tts blocked by proxy)

Custom pipeline advantages:
- No external API keys required
- Fully local and reproducible
- Script quality controlled manually
- Faster iteration

## Voice Quality Note
espeak-ng produces robotic TTS. For production use, consider:
- ElevenLabs API (highest quality)
- OpenAI TTS API
- Azure Neural TTS (if accessible outside this environment)
- Coqui TTS (local, higher quality than espeak)

## Video Style
- 9:16 vertical (1080×1920)
- Dark gradient backgrounds with accent colors per segment
- DejaVu Sans Bold typography
- Subtitle overlays at bottom (white with black shadow)
- No stock video needed — all text/graphic slides

## Improvements for Next Video
1. Install Coqui TTS for better voice quality (local, no network)
2. Add animated transitions between slides (fade or slide)
3. Add background music (royalty-free lofi/tech track)
4. Consider fetching GitHub trending data programmatically
5. Set up Pexels API key for actual stock footage
6. Use MoneyPrinterTurbo API once Pexels key is configured

## News Research Process
- Searched for "AI news June 2026 last 24 hours"
- Searched for "Microsoft Build 2026 announcements"
- Searched for "Anthropic IPO Claude Mythos"
- Searched for "trending GitHub repos AI June 2026"
- Selected 3 strongest stories by: developer impact, viral potential, recency
- Dropped: Trump AI EO, NVIDIA JetPack 7.2, Pentagon contract
