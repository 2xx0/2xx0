"""
make_info_card.py
Hand-authored neofetch-style SVG panel: title bar + key/value rows
that fade/slide in line by line, staggered. STATIC=1 emits a frozen
frame (no animation) for local previews.
"""
import os

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "info-card.svg")
STATIC = os.environ.get("STATIC") == "1"

BG = "#0d1117"
PANEL = "#161b22"
ACCENT = "#39d353"
TEXT = "#c9d1d9"
DIM = "#6e7681"
TITLE_BAR = "#21262d"

ROWS = [
    ("user", "Mohammed Sholy (nexo)"),
    ("role", "Data Analysis & AI Student"),
    ("uni", "Amman Arab University (2025-2029)"),
    ("stack", "Python | Java | C++ | React"),
    ("tools", "ChatGPT | Gemini | Claude | Grok | Burp Suite"),
    ("focus", "API reverse engineering, browser automation, data analysis"),
    ("builds", "Moodle AI Assistant, Multi-LLM Discord Bot, API research tools"),
    ("status", "Focused on studies right now — open later"),
]

WIDTH = 460
ROW_H = 26
TOP_PAD = 58
PADDING_BOTTOM = 20
HEIGHT = TOP_PAD + len(ROWS) * ROW_H + PADDING_BOTTOM


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg():
    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace">'
    )

    anim_css = "" if STATIC else '''
      .line {
        opacity: 0;
        transform: translateX(-8px);
        animation: fade-in 0.4s ease-out forwards;
      }
      @keyframes fade-in {
        to { opacity: 1; transform: translateX(0); }
      }
    '''
    parts.append(f'''
    <style>
      .panel {{ fill: {PANEL}; stroke: #30363d; stroke-width: 1; }}
      .titlebar {{ fill: {TITLE_BAR}; }}
      .dot {{ }}
      .key {{ fill: {ACCENT}; font-size: 13px; font-weight: bold; }}
      .val {{ fill: {TEXT}; font-size: 13px; }}
      .title-text {{ fill: {DIM}; font-size: 12px; }}
      {anim_css}
    </style>
    ''')

    # panel background
    parts.append(f'<rect class="panel" x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="8"/>')

    # title bar
    parts.append(f'<path class="titlebar" d="M0.5,8.5 a8,8 0 0 1 8,-8 h{WIDTH-17} a8,8 0 0 1 8,8 v20 h-{WIDTH-1} z"/>')
    for i, color in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle class="dot" cx="{18 + i*16}" cy="18" r="5" fill="{color}"/>')
    parts.append(f'<text class="title-text" x="{WIDTH/2}" y="22" text-anchor="middle">2xx0 — neofetch</text>')

    # divider
    parts.append(f'<line x1="16" y1="44" x2="{WIDTH-16}" y2="44" stroke="#30363d" stroke-width="1"/>')

    for i, (key, val) in enumerate(ROWS):
        y = TOP_PAD + i * ROW_H
        delay = i * 0.09
        cls = "line" if not STATIC else ""
        style = f' style="animation-delay:{delay:.2f}s"' if not STATIC else ""
        safe_val = escape(val)
        parts.append(
            f'<g class="{cls}"{style}>'
            f'<text class="key" x="24" y="{y}">{key}</text>'
            f'<text class="val" x="110" y="{y}">{safe_val}</text>'
            f'</g>'
        )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    svg = build_svg()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
