"""
make_ascii_logo_svg.py
Renders a big block-style ASCII-art wordmark (e.g. "2xx0") as a
monochrome, self-typing SVG -- no personal photo needed. Uses
pyfiglet for the letterforms, then wraps each row in a clip-path
wipe animation staggered top to bottom, like a terminal printing
a banner.
"""
import os
import pyfiglet

TEXT = os.environ.get("LOGO_TEXT", "2xx0")
FONT = os.environ.get("LOGO_FONT", "slant")  # try 'slant', 'big', 'standard'
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "ascii-logo.svg")

CHAR_W = 9.2
CHAR_H = 18
FONT_SIZE = 16
COLOR = "#39d353"  # terminal green, monochrome


def get_ascii_rows(text: str, font: str):
    art = pyfiglet.figlet_format(text, font=font)
    rows = art.rstrip("\n").split("\n")
    # trim fully-blank rows at the edges but keep internal spacing
    while rows and rows[0].strip() == "":
        rows.pop(0)
    while rows and rows[-1].strip() == "":
        rows.pop()
    max_len = max(len(r) for r in rows) if rows else 0
    rows = [r.ljust(max_len) for r in rows]
    return rows


def escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(rows):
    n_rows = len(rows)
    n_cols = max(len(r) for r in rows) if rows else 0

    width = int(n_cols * CHAR_W) + 24
    height = int(n_rows * CHAR_H) + 32

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace">'
    )

    parts.append(f'''
    <style>
      .bg {{ fill: #0d1117; }}
      .row {{ fill: {COLOR}; font-size: {FONT_SIZE}px; white-space: pre; }}
      .cursor {{ fill: {COLOR}; }}
      .clip-row {{
        animation: wipe-in 0.5s steps(40, end) forwards;
      }}
      @keyframes wipe-in {{
        from {{ clip-path: inset(0 100% 0 0); }}
        to   {{ clip-path: inset(0 0 0 0); }}
      }}
    </style>
    ''')

    parts.append(f'<rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="8"/>')

    for i, row in enumerate(rows):
        y = 24 + i * CHAR_H
        delay = i * 0.09
        row_width = len(row) * CHAR_W + 16
        safe_row = escape(row)
        parts.append(
            f'<g class="clip-row" style="animation-delay:{delay:.2f}s">'
            f'<text class="row" x="12" y="{y}">{safe_row}</text>'
            f'</g>'
        )

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    rows = get_ascii_rows(TEXT, FONT)
    svg = build_svg(rows)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
