"""
scripthook.py — Viral script generator with highlighted keyword captions.

Mark emphasis words in your script strings with **double asterisks**.
  · strip_markers(text)              → plain text for TTS narration
  · to_ass_text(text)                → ASS-formatted text, yellow highlights
  · build_ass_subs(narrations, durs) → full .ass subtitle file content

The "hl" slide style (used in SEGMENTS slide_lines) renders a yellow
background chip behind the text — the physical-highlighter look.
"""

import re

# ASS color format: &HAABBGGRR& (note: reversed channel order vs RGB)
_YELLOW = "&H0000FFFF&"   # bright yellow  (A=00 B=00 G=FF R=FF)
_WHITE  = "&H00FFFFFF&"   # white / reset  (A=00 B=FF G=FF R=FF)

HOOKS = [
    "These **5 AI tools** are making people **$500 a day** — completely **free**.",
    "Most people are broke online because they never found these **5 AI tools**.",
    "I tested **30 AI tools** — only **5** actually pay you. Here they are.",
    "Stop sleeping on **AI** — these **5 free tools** print money in 2026.",
    "If you're not using these **5 AI tools** yet, you're leaving **thousands** behind.",
]


def strip_markers(text: str) -> str:
    """Remove **...** markers → plain text for TTS narration."""
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text)


def to_ass_text(text: str) -> str:
    """Convert **word** markers → ASS color override codes (yellow on white reset)."""
    def _sub(m):
        return f"{{\\c{_YELLOW}}}{m.group(1)}{{\\c{_WHITE}}}"
    return re.sub(r"\*\*(.+?)\*\*", _sub, text)


def _ass_ts(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


_ASS_HEADER = """\
[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans Bold,38,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,10,10,90,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""


def build_ass_subs(narrations: list[str], durations: list[float]) -> str:
    """
    Build .ass subtitle content from marked narration strings.

    narrations : list of script strings with **keyword** markers
    durations  : per-segment durations in seconds (same length as narrations)
    Returns    : complete .ass file as a string
    """
    cues = [_ASS_HEADER]
    t = 0.0
    chunk_n = 8  # words per subtitle cue

    for narration, seg_dur in zip(narrations, durations):
        words = narration.split()
        chunks, i = [], 0
        while i < len(words):
            chunks.append(" ".join(words[i : i + chunk_n]))
            i += chunk_n

        char_lens = [len(c) for c in chunks]
        total = max(sum(char_lens), 1)
        raw = [max(0.8, (cl / total) * seg_dur) for cl in char_lens]
        scale = seg_dur / sum(raw)
        cdurs = [d * scale for d in raw]

        for chunk, dur in zip(chunks, cdurs):
            cues.append(
                f"Dialogue: 0,{_ass_ts(t)},{_ass_ts(t + dur)},"
                f"Default,,0,0,0,,{to_ass_text(chunk)}"
            )
            t += dur

    return "\n".join(cues)
