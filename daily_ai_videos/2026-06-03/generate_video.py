"""
Daily AI Video Generator v2 — June 3, 2026
Voice  : espeak-ng + mbrola-en1 (soft British English, much less robotic)
Timing : character-weighted subtitle estimation (Whisper models unavailable)
Video  : PIL slides + ffmpeg zoompan (Ken Burns motion) + xfade transitions
Outro  : Sources + Repos end card
"""

import os
import subprocess
import textwrap
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import AudioFileClip

# ── Paths ──────────────────────────────────────────────────────────────────
OUT_DIR = Path(__file__).parent
AUDIO_FILE = OUT_DIR / "narration.mp3"
FINAL_VIDEO = OUT_DIR / "final_video.mp4"
SRT_FILE = OUT_DIR / "subtitles.srt"
WORK_DIR = OUT_DIR / "_work"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FFMPEG = __import__("imageio_ffmpeg").get_ffmpeg_exe()

# ── Video config ───────────────────────────────────────────────────────────
W, H = 720, 1280
FPS = 25
FADE_DUR = 0.45    # crossfade between segments (seconds)

# ── Sources / Repos for end card ───────────────────────────────────────────
SOURCES = [
    "buildfastwithai.com  — MS Build recap",
    "devblogs.microsoft.com — Agent Framework",
    "cnbc.com — Anthropic IPO S-1",
    "techcrunch.com — Claude Mythos expansion",
    "firecrawl.dev/blog — GitHub repos 2026",
]
REPOS = [
    "github.com/perplexity-ai/bumblebee",
    "github.com/microsoft/windows-agent-framework",
    "github.com/langflow-ai/langflow",
]

# ── Script segments ────────────────────────────────────────────────────────
SEGMENTS = [
    (
        "TODAY",
        (
            "Three things happened in AI today, and one of them "
            "could change how you build software."
        ),
        [
            ("3 AI updates", "xl"),
            ("that actually", "xl"),
            ("matter today.", "xl"),
            ("", "gap"),
            ("June 3, 2026", "tag"),
        ],
        (0, 190, 255),
    ),
    (
        "MICROSOFT BUILD",
        (
            "At Microsoft Build, the company open-sourced the Windows Agent Framework "
            "under an MIT license. "
            "Any developer can now build autonomous agents that run natively on Windows, "
            "no Azure required. "
            "They also announced Project Polaris, Microsoft's own AI model, "
            "which will replace GPT-4 in GitHub Copilot starting August. "
            "And Foundry Local hit general availability: "
            "full AI inference on-device, without touching the cloud."
        ),
        [
            ("Microsoft Build 2026", "lg"),
            ("", "gap"),
            ("Windows Agent Framework", "md"),
            ("open-sourced · MIT license", "sm"),
            ("", "gap"),
            ("Project Polaris replaces", "md"),
            ("GPT-4 in Copilot", "sm"),
            ("→ August 2026", "accent"),
            ("", "gap"),
            ("Foundry Local → GA", "md"),
            ("Full AI inference on-device", "sm"),
        ],
        (80, 105, 255),
    ),
    (
        "ANTHROPIC",
        (
            "Anthropic quietly filed a confidential IPO with the SEC, "
            "targeting a listing in October at a valuation near a trillion dollars. "
            "But the bigger story is Claude Mythos. "
            "Anthropic just expanded their cybersecurity AI to 150 organizations "
            "across fifteen countries, covering power grids, hospitals, and water systems. "
            "In early testing, Mythos found over ten thousand high-severity vulnerabilities "
            "that humans missed."
        ),
        [
            ("Anthropic files IPO", "lg"),
            ("Oct 2026 · ~$965B", "sm"),
            ("", "gap"),
            ("Claude Mythos expanded:", "md"),
            ("150 orgs · 15 countries", "sm"),
            ("Power · Water · Healthcare", "sm"),
            ("", "gap"),
            ("10,000+ critical vulns", "accent"),
            ("found by AI, missed by humans", "sm"),
        ],
        (235, 75, 135),
    ),
    (
        "REPO OF THE DAY",
        (
            "And the GitHub repo worth checking today: Bumblebee, by Perplexity AI. "
            "It's a supply chain scanner written in Go with zero dependencies "
            "that checks your packages, MCP servers, and editor extensions "
            "for suspicious or compromised code. "
            "With supply chain attacks on the rise, this one is actually useful."
        ),
        [
            ("Repo of the Day", "lg"),
            ("", "gap"),
            ("Bumblebee", "xl"),
            ("by Perplexity AI", "sm"),
            ("", "gap"),
            ("Supply chain scanner", "md"),
            ("Go · Zero dependencies", "sm"),
            ("", "gap"),
            ("Checks: packages,", "sm"),
            ("MCP servers, extensions", "sm"),
        ],
        (35, 205, 105),
    ),
    (
        "FOLLOW",
        "Follow for daily AI tools, repos, and automation updates dropped every day.",
        [
            ("Follow for daily", "xl"),
            ("AI tools · repos", "xl"),
            ("automation updates", "xl"),
            ("", "gap"),
            ("dropped every day.", "md"),
        ],
        (155, 85, 255),
    ),
]

# ── Audio ──────────────────────────────────────────────────────────────────
def generate_audio():
    full = " ".join(seg[1] for seg in SEGMENTS)
    wav = str(OUT_DIR / "_narration_raw.wav")
    subprocess.run(
        ["espeak-ng", "-v", "mb-en1",
         "-s", "138",   # wpm — relaxed, podcasty pace
         "-p", "50",    # pitch (0-99)
         "-a", "180",   # amplitude
         "-g", "10",    # word gap (ms)
         "-w", wav, full],
        check=True, capture_output=True,
    )
    # Normalise + upsample to 44.1kHz with gentle warmth EQ
    subprocess.run(
        [FFMPEG, "-y", "-i", wav,
         "-af", "loudnorm=I=-16:TP=-2:LRA=9,aresample=44100",
         "-ar", "44100", "-ab", "128k", str(AUDIO_FILE)],
        check=True, capture_output=True,
    )
    os.remove(wav)
    dur = AudioFileClip(str(AUDIO_FILE)).duration
    print(f"  Audio: {dur:.2f}s  |  {os.path.getsize(AUDIO_FILE)//1024}KB")
    return dur


# ── Timing ─────────────────────────────────────────────────────────────────
def compute_durations(narrations, total_dur):
    """Distribute total duration proportionally by character count."""
    lens = [len(n) for n in narrations]
    total = sum(lens)
    raw = [max(3.0, (l / total) * total_dur) for l in lens]
    scale = total_dur / sum(raw)
    return [d * scale for d in raw]


def build_srt(narrations, durations):
    """Build SRT subtitle file using character-weighted timing per chunk."""
    lines = []
    idx = 1
    global_t = 0.0
    for narration, seg_dur in zip(narrations, durations):
        words = narration.split()
        chunk_size = 8
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i:i + chunk_size]))
        # Distribute seg_dur by character count across chunks
        char_lens = [len(c) for c in chunks]
        total_chars = sum(char_lens)
        chunk_durs = [max(0.8, (cl / total_chars) * seg_dur) for cl in char_lens]
        scale = seg_dur / sum(chunk_durs)
        chunk_durs = [d * scale for d in chunk_durs]

        for chunk, dur in zip(chunks, chunk_durs):
            start = global_t
            end = global_t + dur
            lines.append(f"{idx}")
            lines.append(f"{_srt_ts(start)} --> {_srt_ts(end)}")
            wrapped = textwrap.fill(chunk, width=34)
            lines.append(wrapped)
            lines.append("")
            idx += 1
            global_t += dur

    SRT_FILE.write_text("\n".join(lines))
    print(f"  SRT: {idx-1} subtitle entries → {SRT_FILE.name}")


def _srt_ts(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t - int(t)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


# ── Colour helpers ──────────────────────────────────────────────────────────
def darken(c, f=0.10): return tuple(max(0, int(x * f)) for x in c)
def lighten(c, a=80):  return tuple(min(255, x + a) for x in c)
def blend(c1, c2, t):  return tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))
def alpha_blend(base, over, a): return tuple(int(b*(1-a)+o*a) for b,o in zip(base,over))


# ── Slide renderer ──────────────────────────────────────────────────────────
def _font(path, size):
    try:    return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()


def render_slide(label, lines, accent, w=W, h=H):
    """Render one beautiful slide as PIL Image."""
    # Deep gradient background
    bg_top = darken(accent, 0.09)
    bg_mid = tuple(max(0, int(x*0.05)) for x in accent)
    bg_bot = (3, 3, 14)
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        # 3-stop gradient for more depth
        if t < 0.5:
            c = blend(bg_top, bg_mid, t * 2)
        else:
            c = blend(bg_mid, bg_bot, (t - 0.5) * 2)
        draw.line([(0, y), (w, y)], fill=c)

    # Vignette overlay (dark edges → cinematic feel)
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(80):
        alpha = int(120 * (1 - i / 80) ** 2)
        vd.rectangle([i, i, w - i, h - i], outline=(0, 0, 0, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), vig).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Decorative dot grid (subtle)
    dot_color = tuple(min(255, x + 18) for x in bg_mid)
    for gx in range(40, w, 60):
        for gy in range(80, h, 60):
            draw.ellipse([(gx - 1, gy - 1), (gx + 1, gy + 1)], fill=dot_color)

    # Top accent bar with glow
    bar_y = int(h * 0.052)
    for i in range(5, 0, -1):
        glow = tuple(max(0, min(255, int(c * (0.3 + i * 0.1)))) for c in accent)
        draw.rectangle([(55, bar_y - i), (w - 55, bar_y + 8 + i)], fill=(*glow, 60))
    draw.rectangle([(55, bar_y), (w - 55, bar_y + 7)], fill=accent)

    # Label chip
    chip_f = _font(FONT_BOLD, 28)
    chip_y = bar_y + 22
    chip_text = f"  {label}  "
    bbox = draw.textbbox((58, chip_y), chip_text, font=chip_f)
    draw.rounded_rectangle(
        [bbox[0]-6, bbox[1]-6, bbox[2]+6, bbox[3]+6], radius=7, fill=accent)
    draw.text((58, chip_y), chip_text, font=chip_f, fill=(0, 0, 0))

    # Content text
    y = chip_y + (bbox[3] - bbox[1]) + 52
    LEFT = 62
    size_map = {
        "xl":     (_font(FONT_BOLD, 82), (255, 255, 255)),
        "lg":     (_font(FONT_BOLD, 66), (255, 255, 255)),
        "md":     (_font(FONT_BOLD, 52), (228, 234, 255)),
        "sm":     (_font(FONT_REG,  42), (175, 188, 214)),
        "accent": (_font(FONT_BOLD, 52), lighten(accent, 100)),
        "tag":    (_font(FONT_BOLD, 36), lighten(accent, 60)),
        "gap":    (None, None),
    }
    for text, style in lines:
        if style == "gap":
            y += 18
            continue
        f, color = size_map.get(style, size_map["sm"])
        # Multi-layer shadow for legibility
        for ox, oy, a in [(-2,-2,200),(2,-2,200),(-2,2,200),(2,2,200),(0,3,180)]:
            draw.text((LEFT+ox, y+oy), text, font=f, fill=(0, 0, 0))
        draw.text((LEFT, y), text, font=f, fill=color)
        bb = draw.textbbox((LEFT, y), text, font=f)
        y += (bb[3] - bb[1]) + 16

    # Bottom accent dots
    dot_y = h - 85
    for i, dc in enumerate([accent, lighten(accent, 55), lighten(accent, 110)]):
        dx = w // 2 - 24 + i * 24
        for r in range(10, 0, -2):
            glow_a = int(40 * r / 10)
            draw.ellipse([(dx-r, dot_y-r), (dx+r, dot_y+r)],
                         fill=(*tuple(min(255,c+glow_a) for c in dc),))
        draw.ellipse([(dx-8, dot_y-8), (dx+8, dot_y+8)], fill=dc)

    return img


def render_endcard(w=W, h=H):
    """Render the Sources + Repos end card."""
    accent = (255, 200, 50)
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        c = blend((20, 15, 50), (5, 3, 20), t)
        draw.line([(0, y), (w, y)], fill=c)

    # Vignette
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(60):
        vd.rectangle([i, i, w-i, h-i], outline=(0, 0, 0, int(100*(1-i/60)**2)))
    img = Image.alpha_composite(img.convert("RGBA"), vig).convert("RGB")
    draw = ImageDraw.Draw(img)

    hdr_f  = _font(FONT_BOLD, 52)
    item_f = _font(FONT_MONO, 30)
    sm_f   = _font(FONT_REG,  34)

    y = 90
    LEFT = 58

    def section(title, items, color):
        nonlocal y
        # Section header bar
        draw.rectangle([(LEFT, y), (w - LEFT, y + 4)], fill=color)
        y += 14
        draw.text((LEFT, y), title, font=hdr_f, fill=color)
        y += 62
        for item in items:
            # Bullet
            draw.text((LEFT, y), "•", font=sm_f, fill=color)
            # Truncate long URLs to fit
            trimmed = item if len(item) <= 38 else item[:35] + "…"
            draw.text((LEFT + 24, y), trimmed, font=item_f, fill=(210, 220, 240))
            y += 40
        y += 18

    section("Sources", SOURCES, (0, 190, 255))
    section("Repos", REPOS, (35, 205, 105))

    # CTA at bottom
    y = h - 200
    draw.rectangle([(LEFT, y), (w - LEFT, y + 3)], fill=accent)
    y += 16
    draw.text((LEFT, y), "Full links in description ↓", font=sm_f, fill=accent)
    y += 48
    draw.text((LEFT, y), "Follow for daily updates", font=sm_f, fill=(200, 200, 220))

    return img


# ── ffmpeg zoompan clip ─────────────────────────────────────────────────────
ZOOM_STYLES = [
    "z='min(zoom+0.0018,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",    # zoom in centre
    "z='if(lte(zoom,1.0),1.0+0.002*on,zoom)':x='iw/2-(iw/zoom/2)':y='0'",     # zoom in top
    "z='min(zoom+0.0020,1.18)':x='iw/2-(iw/zoom/2)':y='ih-(ih/zoom)'",         # zoom in bottom
    "z='min(zoom+0.0015,1.12)':x='0':y='ih/2-(ih/zoom/2)'",                    # drift right
    "z='min(zoom+0.0015,1.12)':x='iw-(iw/zoom)':y='ih/2-(ih/zoom/2)'",        # drift left
    "z='max(zoom-0.0015,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",     # slow zoom out
]


def make_segment_clip(slide_path, duration, seg_idx, out_path):
    """Apply zoompan Ken Burns effect to a slide image → short video clip."""
    style = ZOOM_STYLES[seg_idx % len(ZOOM_STYLES)]
    nframes = int(duration * FPS) + 5
    vf = (
        f"zoompan={style}:d={nframes}:s={W}x{H}:fps={FPS},"
        "format=yuv420p"
    )
    subprocess.run(
        [FFMPEG, "-y",
         "-loop", "1", "-i", str(slide_path),
         "-t", f"{duration:.4f}",
         "-vf", vf,
         "-c:v", "libx264", "-preset", "fast", "-crf", "21",
         "-pix_fmt", "yuv420p",
         str(out_path)],
        check=True, capture_output=True,
    )


# ── xfade chain ─────────────────────────────────────────────────────────────
def xfade_concat(clip_paths, durations, out_path):
    """Concatenate clip_paths with crossfade transitions."""
    if len(clip_paths) == 1:
        shutil.copy(clip_paths[0], out_path)
        return

    inputs = []
    for p in clip_paths:
        inputs += ["-i", str(p)]

    # Build filter graph
    filters = []
    offset = 0.0
    prev_label = "[0:v]"
    for i in range(1, len(clip_paths)):
        offset += durations[i - 1] - FADE_DUR
        curr_label = f"[xf{i}]"
        filters.append(
            f"{prev_label}[{i}:v]xfade=transition=fade:"
            f"duration={FADE_DUR}:offset={offset:.4f}{curr_label}"
        )
        prev_label = curr_label

    filter_str = ";".join(filters)
    out_label = prev_label  # last produced label

    subprocess.run(
        [FFMPEG, "-y"] + inputs + [
            "-filter_complex", filter_str,
            "-map", out_label,
            "-c:v", "libx264", "-preset", "fast", "-crf", "21",
            "-pix_fmt", "yuv420p",
            str(out_path)],
        check=True, capture_output=True,
    )


# ── Final mux: video + audio + burned subtitles ─────────────────────────────
def mux_final(video_path, audio_path, srt_path, out_path):
    """Add audio and burn in SRT subtitles."""
    subs_style = (
        "FontName=DejaVu Sans Bold,"
        "FontSize=38,"
        "PrimaryColour=&H00FFFFFF,"  # white
        "OutlineColour=&H00000000,"  # black outline
        "BackColour=&H80000000,"     # semi-transparent bg
        "Outline=3,"
        "Shadow=1,"
        "Alignment=2,"               # bottom-centre
        "MarginV=90"
    )
    subprocess.run(
        [FFMPEG, "-y",
         "-i", str(video_path),
         "-i", str(audio_path),
         "-c:v", "libx264", "-preset", "fast", "-crf", "21",
         "-vf", f"subtitles={srt_path}:force_style='{subs_style}'",
         "-c:a", "aac", "-b:a", "128k",
         "-map", "0:v", "-map", "1:a",
         "-movflags", "+faststart",
         "-t", f"{AudioFileClip(str(audio_path)).duration:.3f}",
         str(out_path)],
        check=True,
    )


# ── Main ────────────────────────────────────────────────────────────────────
def produce_video():
    print("=== Daily AI Video v2 — June 3, 2026 ===\n")
    WORK_DIR.mkdir(exist_ok=True)

    # 1. Audio
    print("Step 1: Generating narration (espeak-ng + mbrola-en1)...")
    if AUDIO_FILE.exists():
        print("  (cached)")
        audio_dur = AudioFileClip(str(AUDIO_FILE)).duration
    else:
        audio_dur = generate_audio()

    # 2. Timing
    print("Step 2: Computing segment timing...")
    narrations = [seg[1] for seg in SEGMENTS]
    endcard_dur = 6.0
    video_dur = audio_dur - endcard_dur  # last 6 s = end card (no narration for it)
    durations = compute_durations(narrations, max(video_dur, audio_dur - endcard_dur))
    # Add end card segment duration
    all_durations = durations + [endcard_dur]
    for seg, d in zip(SEGMENTS, durations):
        print(f"  {seg[0]}: {d:.1f}s")
    print(f"  END CARD: {endcard_dur:.1f}s")

    # 3. SRT subtitles (only for narrated segments)
    print("Step 3: Building SRT subtitles...")
    build_srt(narrations, durations)

    # 4. Render slides
    print("Step 4: Rendering slides...")
    slide_paths = []
    for i, seg in enumerate(SEGMENTS):
        label, _, lines, accent = seg
        img = render_slide(label, lines, accent)
        p = WORK_DIR / f"slide_{i:02d}.png"
        img.save(p, "PNG", optimize=False)
        slide_paths.append(p)
        print(f"  slide_{i:02d}.png ✓")

    # End card slide
    endcard_img = render_endcard()
    endcard_path = WORK_DIR / "slide_endcard.png"
    endcard_img.save(endcard_path, "PNG")
    slide_paths.append(endcard_path)
    print(f"  slide_endcard.png ✓")

    # 5. Apply zoompan to each slide
    print("Step 5: Applying Ken Burns motion to each segment...")
    clip_paths = []
    for i, (slide_path, dur) in enumerate(zip(slide_paths, all_durations)):
        out = WORK_DIR / f"clip_{i:02d}.mp4"
        make_segment_clip(slide_path, dur, i, out)
        clip_paths.append(out)
        print(f"  clip_{i:02d}.mp4  ({dur:.1f}s) ✓")

    # 6. Concatenate with crossfade
    print("Step 6: Concatenating with xfade transitions...")
    combined = WORK_DIR / "combined.mp4"
    xfade_concat(clip_paths, all_durations, combined)

    # 7. Mux audio + subtitles
    print("Step 7: Muxing audio + burning subtitles...")
    mux_final(combined, AUDIO_FILE, SRT_FILE, FINAL_VIDEO)

    # Cleanup
    shutil.rmtree(WORK_DIR, ignore_errors=True)

    size_mb = os.path.getsize(FINAL_VIDEO) / (1024 * 1024)
    print(f"\n=== DONE ===")
    print(f"Video : {FINAL_VIDEO}")
    print(f"Size  : {size_mb:.1f} MB  |  {W}x{H} (9:16)  |  {audio_dur:.1f}s")


if __name__ == "__main__":
    produce_video()
