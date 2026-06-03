"""
Daily AI Video Generator — June 3, 2026
Fast pipeline: PIL renders all frames → ffmpeg encodes
Output: vertical 9:16 MP4 ready for TikTok/Reels/Shorts/X
"""

import os
import subprocess
import textwrap
import tempfile
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip

# ── Paths ──────────────────────────────────────────────────────────────────
OUT_DIR = Path(__file__).parent
AUDIO_FILE = OUT_DIR / "narration.mp3"
FINAL_VIDEO = OUT_DIR / "final_video.mp4"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FFMPEG = __import__("imageio_ffmpeg").get_ffmpeg_exe()

# ── Video config ───────────────────────────────────────────────────────────
WIDTH, HEIGHT = 720, 1280    # 9:16, efficient for encoding
FPS = 24

# ── Script segments ────────────────────────────────────────────────────────
# (label, narration_spoken, display_lines, accent_rgb)
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
            ("June 3, 2026", "sm"),
        ],
        (0, 195, 255),
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
            ("open-sourced · MIT", "sm"),
            ("", "gap"),
            ("Project Polaris replaces", "md"),
            ("GPT-4 in GitHub Copilot", "sm"),
            ("→ August 2026", "accent"),
            ("", "gap"),
            ("Foundry Local → GA", "md"),
            ("Full AI on-device, no cloud", "sm"),
        ],
        (90, 110, 255),
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
            ("found in infrastructure audit", "sm"),
        ],
        (240, 80, 140),
    ),
    (
        "REPO OF THE DAY",
        (
            "And the GitHub repo worth checking today: Bumblebee, by Perplexity AI. "
            "It's a supply chain scanner, written in Go with zero dependencies, "
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
            ("Scans: packages", "sm"),
            ("MCP servers, extensions", "sm"),
        ],
        (40, 210, 110),
    ),
    (
        "FOLLOW",
        (
            "Follow for daily AI tools, repos, and automation updates, "
            "dropped every day."
        ),
        [
            ("Follow for daily", "xl"),
            ("AI tools · repos", "xl"),
            ("automation updates", "xl"),
            ("", "gap"),
            ("dropped every day.", "md"),
        ],
        (160, 90, 255),
    ),
]


# ── Audio ─────────────────────────────────────────────────────────────────
def generate_audio():
    full_script = " ".join(seg[1] for seg in SEGMENTS)
    wav_path = str(OUT_DIR / "narration_raw.wav")
    subprocess.run(
        ["espeak-ng", "-v", "en-us", "-s", "148", "-p", "38",
         "-a", "180", "-g", "8", "-w", wav_path, full_script],
        check=True, capture_output=True,
    )
    subprocess.run(
        [FFMPEG, "-y", "-i", wav_path, "-ar", "44100", "-ab", "128k", str(AUDIO_FILE)],
        check=True, capture_output=True,
    )
    os.remove(wav_path)
    duration = AudioFileClip(str(AUDIO_FILE)).duration
    print(f"  Audio: {duration:.2f}s  ({os.path.getsize(AUDIO_FILE):,} bytes)")
    return duration


# ── Colour helpers ─────────────────────────────────────────────────────────
def darken(c, f=0.10):
    return tuple(max(0, int(x * f)) for x in c)

def lighten(c, a=70):
    return tuple(min(255, x + a) for x in c)

def blend(c1, c2, t):
    return tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))


# ── Slide renderer ─────────────────────────────────────────────────────────
def render_slide(label, lines, accent, subtitle_text="", w=WIDTH, h=HEIGHT):
    """Render one complete slide as PIL Image, subtitles baked in."""
    # Gradient background
    bg_top = darken(accent, 0.10)
    bg_bot = (4, 4, 16)
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        draw.line([(0, y), (w, y)], fill=blend(bg_top, bg_bot, t))

    # Fonts
    def font(path, size):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            return ImageFont.load_default()

    xl_f  = font(FONT_BOLD, 82)
    lg_f  = font(FONT_BOLD, 66)
    md_f  = font(FONT_BOLD, 54)
    sm_f  = font(FONT_REG,  42)
    ac_f  = font(FONT_BOLD, 54)
    co_f  = font(FONT_MONO, 36)
    chip_f = font(FONT_BOLD, 30)
    sub_f = font(FONT_BOLD, 42)

    size_map = {
        "xl": (xl_f, (255, 255, 255)),
        "lg": (lg_f, (255, 255, 255)),
        "md": (md_f, (225, 232, 255)),
        "sm": (sm_f, (185, 195, 215)),
        "accent": (ac_f, lighten(accent, 90)),
        "code": (co_f, lighten(accent, 60)),
        "gap": (None, None),
    }

    # Top accent bar
    bar_y = int(h * 0.055)
    draw.rectangle([(60, bar_y), (w - 60, bar_y + 6)], fill=accent)

    # Label chip
    chip_y = bar_y + 22
    chip_text = f"  {label}  "
    bbox = draw.textbbox((60, chip_y), chip_text, font=chip_f)
    draw.rounded_rectangle(
        [bbox[0] - 6, bbox[1] - 6, bbox[2] + 6, bbox[3] + 6], radius=6, fill=accent
    )
    draw.text((60, chip_y), chip_text, font=chip_f, fill=(0, 0, 0))

    # Main content
    y = chip_y + (bbox[3] - bbox[1]) + 48
    LEFT = 65
    for text, style in lines:
        if style == "gap":
            y += 20
            continue
        f, color = size_map.get(style, (sm_f, (200, 200, 220)))
        # shadow
        draw.text((LEFT + 2, y + 2), text, font=f, fill=(0, 0, 0))
        draw.text((LEFT, y), text, font=f, fill=color)
        bb = draw.textbbox((LEFT, y), text, font=f)
        y += (bb[3] - bb[1]) + 14

    # Bottom dots
    dot_y = h - 90
    for i, dc in enumerate([accent, lighten(accent, 50), (255, 255, 255)]):
        dx = w // 2 - 22 + i * 22
        draw.ellipse([(dx - 7, dot_y - 7), (dx + 7, dot_y + 7)], fill=dc)

    # Subtitle (baked in)
    if subtitle_text:
        wrapped = textwrap.fill(subtitle_text, width=30)
        sub_lines = wrapped.split("\n")
        line_h = 52
        total_h = len(sub_lines) * line_h + 24
        sub_y_start = h - 190 - total_h
        # Semi-transparent background box
        box_pad = 14
        box_x0, box_y0 = 40, sub_y_start - box_pad
        box_x1 = w - 40
        box_y1 = sub_y_start + total_h + box_pad
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ov_draw = ImageDraw.Draw(overlay)
        ov_draw.rounded_rectangle(
            [box_x0, box_y0, box_x1, box_y1], radius=10, fill=(0, 0, 0, 160)
        )
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay).convert("RGB")
        draw = ImageDraw.Draw(img)
        for li, line in enumerate(sub_lines):
            lx = w // 2 - draw.textbbox((0, 0), line, font=sub_f)[2] // 2
            ly = sub_y_start + li * line_h
            for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
                draw.text((lx + ox, ly + oy), line, font=sub_f, fill=(0, 0, 0))
            draw.text((lx, ly), line, font=sub_f, fill=(255, 255, 255))

    return img


# ── Segment timing ─────────────────────────────────────────────────────────
def compute_durations(narrations, total_dur):
    wcs = [len(n.split()) for n in narrations]
    total_w = sum(wcs)
    durations = [max(3.0, (wc / total_w) * total_dur) for wc in wcs]
    scale = total_dur / sum(durations)
    return [d * scale for d in durations]


# ── Fast ffmpeg-based assembly ─────────────────────────────────────────────
def assemble_with_ffmpeg(frames_dir, durations, audio_path, output_path):
    """
    Write a concat list and use ffmpeg to assemble static images → video with audio.
    Much faster than moviepy's per-frame Python loop.
    """
    concat_file = frames_dir / "concat.txt"
    with open(concat_file, "w") as f:
        for i, dur in enumerate(durations):
            f.write(f"file 'slide_{i:02d}.png'\n")
            f.write(f"duration {dur:.6f}\n")
        # ffmpeg concat requires the last file repeated without duration
        f.write(f"file 'slide_{len(durations)-1:02d}.png'\n")

    # Measure audio duration to set explicit output length
    audio_dur = AudioFileClip(str(audio_path)).duration

    subprocess.run(
        [
            FFMPEG, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-i", str(audio_path),
            "-t", f"{audio_dur:.3f}",    # cap at exact audio length
            "-vf", f"scale={WIDTH}:{HEIGHT}:flags=lanczos",
            "-c:v", "libx264",
            "-crf", "22",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            str(output_path),
        ],
        check=True,
    )


# ── Production pipeline ─────────────────────────────────────────────────────
def produce_video():
    print("=== Daily AI Video Generator — June 3, 2026 ===\n")

    # Audio
    print("Step 1: Generating narration (espeak-ng)...")
    if AUDIO_FILE.exists():
        print("  (using cached narration.mp3)")
        duration = AudioFileClip(str(AUDIO_FILE)).duration
    else:
        duration = generate_audio()

    # Timing
    print("Step 2: Computing segment durations...")
    narrations = [seg[1] for seg in SEGMENTS]
    durations = compute_durations(narrations, duration)
    for seg, dur in zip(SEGMENTS, durations):
        print(f"  {seg[0]}: {dur:.2f}s")

    # Render slides
    print("Step 3: Rendering slides...")
    frames_dir = OUT_DIR / "_frames"
    frames_dir.mkdir(exist_ok=True)

    for i, (seg, dur) in enumerate(zip(SEGMENTS, durations)):
        label, narration, lines, accent = seg
        # Choose a subtitle chunk for the slide (first ~8 words of narration)
        words = narration.split()
        subtitle = " ".join(words[:8]) + ("..." if len(words) > 8 else "")
        img = render_slide(label, lines, accent, subtitle_text=subtitle)
        path = frames_dir / f"slide_{i:02d}.png"
        img.save(path, "PNG")
        print(f"  Slide {i+1}/{len(SEGMENTS)}: {path.name}")

    # Assemble
    print("Step 4: Assembling video with ffmpeg...")
    assemble_with_ffmpeg(frames_dir, durations, AUDIO_FILE, FINAL_VIDEO)

    # Cleanup temp frames
    shutil.rmtree(frames_dir, ignore_errors=True)

    size_mb = os.path.getsize(FINAL_VIDEO) / (1024 * 1024)
    print(f"\n=== DONE ===")
    print(f"Video : {FINAL_VIDEO}")
    print(f"Size  : {size_mb:.1f} MB")
    print(f"Length: {duration:.1f}s  |  {WIDTH}x{HEIGHT} (9:16 vertical)")
    return str(FINAL_VIDEO)


if __name__ == "__main__":
    produce_video()
