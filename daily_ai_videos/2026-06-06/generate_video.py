"""
Daily AI Video Generator — June 6, 2026 (v2 — Copilot Controversy Angle)
Topic  : GitHub Copilot $750/Month → 5 FREE Alternatives
Niche  : AI Coding Tools × Developer Controversy ($15–22 CPM)
Hook   : Controversy drives 3–5× higher CTR than generic list videos
New    : scripthook — **keyword** markers → yellow captions + hl slide chips
Thumb  : See title_description_hashtags.txt for Canva links
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip

# Import scripthook from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripthook import strip_markers, build_ass_subs

OUT_DIR     = Path(__file__).parent
AUDIO_FILE  = OUT_DIR / "narration.mp3"
FINAL_VIDEO = OUT_DIR / "final_video.mp4"
ASS_FILE    = OUT_DIR / "subtitles.ass"
WORK_DIR    = OUT_DIR / "_work"
FONT_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO   = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FFMPEG      = __import__("imageio_ffmpeg").get_ffmpeg_exe()

W, H     = 720, 1280
FPS      = 25
FADE_DUR = 0.40

# ── Sources / Tools endcard ────────────────────────────────────────────────
SOURCES = [
    "techcrunch.com/2026/05/30  — Copilot billing backlash",
    "github.com/orgs/community  — Discussion #192948",
    "techjournal.org            — 10x–50x cost reports",
    "dev.to/akaranjkar08        — Full cost guide + alternatives",
]
TOOLS = [
    "codeium.com      — Free forever, 70+ editors",
    "continue.dev     — Open-source self-hosted",
    "claude.ai        — Anthropic free tier",
    "aws.amazon.com/q — Amazon Q Developer (free)",
    "tabnine.com      — Local, private, no cloud",
]

# ── Script segments ────────────────────────────────────────────────────────
# Narration: **word** marks highlighted keywords
#   strip_markers()  → plain TTS text
#   build_ass_subs() → yellow-highlighted captions
SEGMENTS = [
    (
        "BREAKING",
        "**GitHub Copilot** just went from **$29** to **$750 a month**. "
        "Here are **5 completely free** AI coding tools that do the same thing.",
        [
            ("GitHub Copilot", "hl"),
            ("$29 → $750/month", "xl"),
            ("", "gap"),
            ("5 FREE", "hl"),
            ("Alternatives", "xl"),
            ("", "gap"),
            ("June 6, 2026", "tag"),
        ],
        (220, 50, 50),
    ),
    (
        "#1 CODEIUM",
        "Number one: **Codeium** — **free forever** for individual developers. "
        "Autocompletes code in **70 different editors** including VS Code and JetBrains, "
        "has a **1 million token** context window, and over **800,000 developers** "
        "have already switched away from Copilot.",
        [
            ("#1  CODEIUM", "lg"),
            ("Free forever · 70+ editors", "sm"),
            ("", "gap"),
            ("1 million token context", "md"),
            ("VS Code · JetBrains · Vim", "sm"),
            ("", "gap"),
            ("800K devs switched", "hl"),
            ("from Copilot", "sm"),
        ],
        (0, 200, 150),
    ),
    (
        "#2 CONTINUE.DEV",
        "Number two: **Continue.dev**. It's **open-source** and self-hosted — "
        "**no subscription, no token billing, no data leaving your machine**. "
        "Plug in any model — Claude, GPT-4, Llama — "
        "and you have a **private Copilot** running inside VS Code.",
        [
            ("#2  CONTINUE", "lg"),
            (".dev  (open-source)", "sm"),
            ("", "gap"),
            ("Self-hosted · No cloud", "md"),
            ("Any model: Claude · GPT · Llama", "sm"),
            ("", "gap"),
            ("$0/month, forever", "hl"),
            ("your code stays local", "sm"),
        ],
        (80, 130, 255),
    ),
    (
        "#3 CLAUDE FREE",
        "Number three: **Claude by Anthropic**, **free tier**. "
        "It handles full files, complex refactors, and **architecture reviews** "
        "that Copilot can't touch. "
        "Paste your entire codebase, describe the bug — Claude gives you the fix. "
        "**No IDE plugin, no token bill.**",
        [
            ("#3  CLAUDE AI", "lg"),
            ("Anthropic — free tier", "sm"),
            ("", "gap"),
            ("Full-file refactors", "md"),
            ("Architecture reviews", "sm"),
            ("", "gap"),
            ("No token bill", "hl"),
            ("paste your full codebase", "sm"),
        ],
        (255, 120, 50),
    ),
    (
        "#4 AMAZON Q",
        "Number four: **Amazon Q Developer** — **free for individuals**, forever. "
        "Inline code completions, CLI assistance, and **security vulnerability scans**. "
        "If you're in the **AWS ecosystem**, this is an immediate swap.",
        [
            ("#4  AMAZON Q", "lg"),
            ("Developer — free forever", "sm"),
            ("", "gap"),
            ("Inline completions + CLI", "md"),
            ("Security vulnerability scans", "sm"),
            ("", "gap"),
            ("Free for individuals", "hl"),
            ("official AWS product", "sm"),
        ],
        (255, 150, 30),
    ),
    (
        "#5 TABNINE",
        "And number five: **Tabnine**. Runs **locally on your machine** — "
        "no cloud, no token costs, ever. "
        "Lightweight, private, supports every major language. "
        "**Your code never leaves your computer.**",
        [
            ("#5  TABNINE", "lg"),
            ("Runs locally · No cloud", "sm"),
            ("", "gap"),
            ("No token bill, ever", "md"),
            ("Every major language", "sm"),
            ("", "gap"),
            ("100% private", "hl"),
            ("your code stays on-device", "sm"),
        ],
        (140, 80, 255),
    ),
    (
        "FOLLOW",
        "Follow now — every single day you get one tool, one niche, "
        "and exactly how to use it.",
        [
            ("Follow now.", "xl"),
            ("", "gap"),
            ("Daily: 1 tool · 1 niche", "md"),
            ("exactly how to use it.", "md"),
            ("", "gap"),
            ("Every. Single. Day.", "accent"),
        ],
        (255, 200, 50),
    ),
]

# ── Audio ──────────────────────────────────────────────────────────────────
def generate_audio():
    plain_text = " ".join(strip_markers(seg[1]) for seg in SEGMENTS)
    wav = str(OUT_DIR / "_narration_raw.wav")
    subprocess.run(
        ["espeak-ng", "-v", "mb-en1",
         "-s", "138", "-p", "50", "-a", "180", "-g", "10",
         "-w", wav, plain_text],
        check=True, capture_output=True,
    )
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
    lens = [len(n) for n in narrations]
    total = sum(lens)
    raw = [max(3.0, (l / total) * total_dur) for l in lens]
    scale = total_dur / sum(raw)
    return [d * scale for d in raw]


# ── Colour helpers ──────────────────────────────────────────────────────────
def darken(c, f=0.10):  return tuple(max(0, int(x * f)) for x in c)
def lighten(c, a=80):   return tuple(min(255, x + a) for x in c)
def blend(c1, c2, t):   return tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3))


# ── Font helper ─────────────────────────────────────────────────────────────
def _font(path, size):
    try:    return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()


# ── Slide renderer (adds "hl" style: yellow background chip) ──────────────
def render_slide(label, lines, accent, w=W, h=H):
    bg_top = darken(accent, 0.09)
    bg_mid = tuple(max(0, int(x * 0.05)) for x in accent)
    bg_bot = (3, 3, 14)
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        c = blend(bg_top, bg_mid, t * 2) if t < 0.5 else blend(bg_mid, bg_bot, (t - 0.5) * 2)
        draw.line([(0, y), (w, y)], fill=c)

    # Vignette
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(80):
        vd.rectangle([i, i, w-i, h-i], outline=(0, 0, 0, int(120*(1-i/80)**2)))
    img = Image.alpha_composite(img.convert("RGBA"), vig).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Dot grid
    dot_color = tuple(min(255, x + 18) for x in bg_mid)
    for gx in range(40, w, 60):
        for gy in range(80, h, 60):
            draw.ellipse([(gx-1, gy-1), (gx+1, gy+1)], fill=dot_color)

    # Top accent bar
    bar_y = int(h * 0.052)
    for i in range(5, 0, -1):
        glow = tuple(max(0, min(255, int(c * (0.3 + i * 0.1)))) for c in accent)
        draw.rectangle([(55, bar_y-i), (w-55, bar_y+8+i)], fill=(*glow, 60))
    draw.rectangle([(55, bar_y), (w-55, bar_y+7)], fill=accent)

    # Label chip
    chip_f = _font(FONT_BOLD, 28)
    chip_y = bar_y + 22
    chip_text = f"  {label}  "
    bbox = draw.textbbox((58, chip_y), chip_text, font=chip_f)
    draw.rounded_rectangle([bbox[0]-6, bbox[1]-6, bbox[2]+6, bbox[3]+6], radius=7, fill=accent)
    draw.text((58, chip_y), chip_text, font=chip_f, fill=(0, 0, 0))

    y = chip_y + (bbox[3] - bbox[1]) + 52
    LEFT = 62
    size_map = {
        "xl":     (_font(FONT_BOLD, 82), (255, 255, 255),   None),
        "lg":     (_font(FONT_BOLD, 66), (255, 255, 255),   None),
        "md":     (_font(FONT_BOLD, 52), (228, 234, 255),   None),
        "sm":     (_font(FONT_REG,  42), (175, 188, 214),   None),
        "accent": (_font(FONT_BOLD, 52), lighten(accent, 100), None),
        "tag":    (_font(FONT_BOLD, 36), lighten(accent, 60),  None),
        # "hl" — physical yellow-highlighter chip: dark text on vivid yellow bg
        "hl":     (_font(FONT_BOLD, 86), (12, 10, 8),       (255, 230, 0)),
        "gap":    (None, None, None),
    }

    for text, style in lines:
        if style == "gap":
            y += 20
            continue
        f, color, bg = size_map.get(style, size_map["sm"])
        bb = draw.textbbox((LEFT, y), text, font=f)
        if bg is not None:
            pad_x, pad_y = 10, 5
            draw.rounded_rectangle(
                [bb[0]-pad_x, bb[1]-pad_y, bb[2]+pad_x, bb[3]+pad_y],
                radius=8, fill=bg,
            )
        # Shadow layers
        shadow = (0, 0, 0) if bg is None else (80, 60, 0)
        for ox, oy in [(-2,-2),(2,-2),(-2,2),(2,2),(0,3)]:
            draw.text((LEFT+ox, y+oy), text, font=f, fill=shadow)
        draw.text((LEFT, y), text, font=f, fill=color)
        bb2 = draw.textbbox((LEFT, y), text, font=f)
        y += (bb2[3] - bb2[1]) + 18

    # Bottom dots
    dot_y = h - 85
    for i, dc in enumerate([accent, lighten(accent, 55), lighten(accent, 110)]):
        dx = w // 2 - 24 + i * 24
        draw.ellipse([(dx-8, dot_y-8), (dx+8, dot_y+8)], fill=dc)

    return img


def render_endcard(w=W, h=H):
    accent = (255, 200, 50)
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        c = blend((20, 15, 50), (5, 3, 20), y / (h - 1))
        draw.line([(0, y), (w, y)], fill=c)

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
        draw.rectangle([(LEFT, y), (w - LEFT, y + 4)], fill=color)
        y += 14
        draw.text((LEFT, y), title, font=hdr_f, fill=color)
        y += 62
        for item in items:
            draw.text((LEFT, y), "•", font=sm_f, fill=color)
            trimmed = item if len(item) <= 38 else item[:35] + "…"
            draw.text((LEFT + 24, y), trimmed, font=item_f, fill=(210, 220, 240))
            y += 40
        y += 18

    section("Research", SOURCES, (0, 190, 255))
    section("Tools in this video", TOOLS, (100, 200, 80))

    y = h - 200
    draw.rectangle([(LEFT, y), (w - LEFT, y + 3)], fill=accent)
    y += 16
    draw.text((LEFT, y), "All links in description ↓", font=sm_f, fill=accent)
    y += 48
    draw.text((LEFT, y), "Follow for daily money tools", font=sm_f, fill=(200, 200, 220))

    return img


# ── ffmpeg zoompan (Ken Burns) ─────────────────────────────────────────────
ZOOM_STYLES = [
    "z='min(zoom+0.0018,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
    "z='if(lte(zoom,1.0),1.0+0.002*on,zoom)':x='iw/2-(iw/zoom/2)':y='0'",
    "z='min(zoom+0.0020,1.18)':x='iw/2-(iw/zoom/2)':y='ih-(ih/zoom)'",
    "z='min(zoom+0.0015,1.12)':x='0':y='ih/2-(ih/zoom/2)'",
    "z='min(zoom+0.0015,1.12)':x='iw-(iw/zoom)':y='ih/2-(ih/zoom/2)'",
    "z='max(zoom-0.0015,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
]


def make_segment_clip(slide_path, duration, seg_idx, out_path):
    style = ZOOM_STYLES[seg_idx % len(ZOOM_STYLES)]
    nframes = int(duration * FPS) + 5
    vf = f"zoompan={style}:d={nframes}:s={W}x{H}:fps={FPS},format=yuv420p"
    subprocess.run(
        [FFMPEG, "-y",
         "-loop", "1", "-i", str(slide_path),
         "-t", f"{duration:.4f}",
         "-vf", vf,
         "-c:v", "libx264", "-preset", "fast", "-crf", "21",
         "-pix_fmt", "yuv420p", str(out_path)],
        check=True, capture_output=True,
    )


# ── xfade chain ─────────────────────────────────────────────────────────────
def xfade_concat(clip_paths, durations, out_path):
    if len(clip_paths) == 1:
        shutil.copy(clip_paths[0], out_path)
        return
    inputs = []
    for p in clip_paths:
        inputs += ["-i", str(p)]
    filters, offset, prev = [], 0.0, "[0:v]"
    for i in range(1, len(clip_paths)):
        offset += durations[i - 1] - FADE_DUR
        curr = f"[xf{i}]"
        filters.append(
            f"{prev}[{i}:v]xfade=transition=fade:"
            f"duration={FADE_DUR}:offset={offset:.4f}{curr}"
        )
        prev = curr
    subprocess.run(
        [FFMPEG, "-y"] + inputs + [
            "-filter_complex", ";".join(filters),
            "-map", prev,
            "-c:v", "libx264", "-preset", "fast", "-crf", "21",
            "-pix_fmt", "yuv420p", str(out_path)],
        check=True, capture_output=True,
    )


# ── Mux: video + audio + ASS subtitles ────────────────────────────────────
def mux_final(video_path, audio_path, ass_path, out_path):
    """Burn ASS subtitles (yellow highlights via scripthook) into final video."""
    subprocess.run(
        [FFMPEG, "-y",
         "-i", str(video_path),
         "-i", str(audio_path),
         "-c:v", "libx264", "-preset", "fast", "-crf", "21",
         "-vf", f"subtitles={ass_path}",
         "-c:a", "aac", "-b:a", "128k",
         "-map", "0:v", "-map", "1:a",
         "-movflags", "+faststart",
         "-t", f"{AudioFileClip(str(audio_path)).duration:.3f}",
         str(out_path)],
        check=True,
    )


# ── Main ────────────────────────────────────────────────────────────────────
def produce_video():
    print("=== Daily AI Video — June 6, 2026 ===")
    print("Niche: AI Tools × Make Money Online ($15–20 CPM)\n")
    WORK_DIR.mkdir(exist_ok=True)

    print("Step 1: Generating narration (espeak-ng + mbrola-en1)...")
    if AUDIO_FILE.exists():
        print("  (cached)")
        audio_dur = AudioFileClip(str(AUDIO_FILE)).duration
    else:
        audio_dur = generate_audio()

    print("Step 2: Computing segment timing...")
    narrations = [seg[1] for seg in SEGMENTS]
    endcard_dur = 6.0
    durations = compute_durations(narrations, audio_dur - endcard_dur)
    all_durations = durations + [endcard_dur]
    for seg, d in zip(SEGMENTS, durations):
        print(f"  {seg[0]}: {d:.1f}s")
    print(f"  END CARD: {endcard_dur:.1f}s")

    print("Step 3: Building ASS subtitles (scripthook — yellow highlights)...")
    ass_content = build_ass_subs(narrations, durations)
    ASS_FILE.write_text(ass_content)
    print(f"  subtitles.ass written ✓")

    print("Step 4: Rendering slides (hl chips + Ken Burns)...")
    slide_paths = []
    for i, (label, _, lines, accent) in enumerate(SEGMENTS):
        img = render_slide(label, lines, accent)
        p = WORK_DIR / f"slide_{i:02d}.png"
        img.save(p, "PNG")
        slide_paths.append(p)
        print(f"  slide_{i:02d}.png ✓")
    endcard_path = WORK_DIR / "slide_endcard.png"
    render_endcard().save(endcard_path, "PNG")
    slide_paths.append(endcard_path)

    print("Step 5: Applying Ken Burns motion...")
    clip_paths = []
    for i, (slide_path, dur) in enumerate(zip(slide_paths, all_durations)):
        out = WORK_DIR / f"clip_{i:02d}.mp4"
        make_segment_clip(slide_path, dur, i, out)
        clip_paths.append(out)
        print(f"  clip_{i:02d}.mp4 ({dur:.1f}s) ✓")

    print("Step 6: Concatenating with xfade transitions...")
    combined = WORK_DIR / "combined.mp4"
    xfade_concat(clip_paths, all_durations, combined)

    print("Step 7: Muxing audio + burning ASS subtitles...")
    mux_final(combined, AUDIO_FILE, ASS_FILE, FINAL_VIDEO)

    shutil.rmtree(WORK_DIR, ignore_errors=True)

    size_mb = os.path.getsize(FINAL_VIDEO) / (1024 * 1024)
    print(f"\n=== DONE ===")
    print(f"Video  : {FINAL_VIDEO}")
    print(f"Size   : {size_mb:.1f} MB  |  {W}x{H} (9:16)  |  {audio_dur:.1f}s")
    print(f"Thumb  : See title_description_hashtags.txt for Canva link")


if __name__ == "__main__":
    produce_video()
