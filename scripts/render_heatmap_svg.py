"""
render_heatmap_svg.py
Reads data/contributions.json and draws the classic 53-week x 7-day
calendar as rounded boxes in a terminal green ramp. Boxes reveal with
a diagonal slide-down animation (CSS keyframes) that plays once on
load and then freezes -- no infinite looping.
"""
import json
import os
from collections import defaultdict
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

# Terminal green ramp: background -> brightest neon green
PALETTE = ["#0d1117", "#0e4429", "#006d32", "#26a641", "#39d353", "#7CFFB2"]

BOX = 11          # box size in px
GAP = 3           # gap between boxes
LEFT_PAD = 34      # room for day labels
TOP_PAD = 34       # room for month labels
LEGEND_H = 26
STATS_H = 26


def load_data():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def bucket_by_week(days):
    """Group ISO-date/level dicts into columns (weeks) of 7 rows (Sun-Sat)."""
    weeks = []
    current_week = [None] * 7

    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        dow = (dt.weekday() + 1) % 7  # convert Mon=0..Sun=6 -> Sun=0..Sat=6
        if dow == 0 and any(c is not None for c in current_week):
            weeks.append(current_week)
            current_week = [None] * 7
        current_week[dow] = {"date": d["date"], "level": d["level"], "dt": dt}

    if any(c is not None for c in current_week):
        weeks.append(current_week)

    return weeks


def month_labels(weeks):
    labels = []
    last_month = None
    for i, week in enumerate(weeks):
        first_valid = next((c for c in week if c), None)
        if not first_valid:
            continue
        m = first_valid["dt"].strftime("%b")
        if m != last_month:
            labels.append((i, m))
            last_month = m
    return labels


def build_svg(payload):
    days = payload["days"]
    stats = payload.get("stats", {})
    username = payload.get("username", "")

    weeks = bucket_by_week(days)
    n_weeks = len(weeks)

    width = LEFT_PAD + n_weeks * (BOX + GAP) + 10
    height = TOP_PAD + 7 * (BOX + GAP) + LEGEND_H + STATS_H + 20

    total_active = stats.get("active_days", 0)
    current_streak = stats.get("current_streak", 0)
    longest_streak = stats.get("longest_streak", 0)

    svg_parts = []
    svg_parts.append(
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="Consolas, Menlo, monospace">'
    )

    svg_parts.append(f'''
    <style>
      .bg {{ fill: #0d1117; }}
      .box {{
        opacity: 0;
        transform: translate(-6px, -6px);
        animation: reveal 0.35s ease-out forwards;
      }}
      .lbl {{ fill: #6e7681; font-size: 9px; }}
      .stat {{ fill: #39d353; font-size: 11px; }}
      .stat-dim {{ fill: #8b949e; font-size: 11px; }}
      @keyframes reveal {{
        to {{ opacity: 1; transform: translate(0, 0); }}
      }}
    </style>
    ''')

    svg_parts.append(f'<rect class="bg" x="0" y="0" width="{width}" height="{height}" rx="6"/>')

    # month labels
    for week_idx, label in month_labels(weeks):
        x = LEFT_PAD + week_idx * (BOX + GAP)
        svg_parts.append(f'<text class="lbl" x="{x}" y="{TOP_PAD - 10}">{label}</text>')

    # day-of-week labels (Mon, Wed, Fri)
    day_names = {1: "Mon", 3: "Wed", 5: "Fri"}
    for dow, name in day_names.items():
        y = TOP_PAD + dow * (BOX + GAP) + BOX - 2
        svg_parts.append(f'<text class="lbl" x="0" y="{y}">{name}</text>')

    # boxes, diagonal stagger delay = week_idx + dow (in 18ms steps)
    for week_idx, week in enumerate(weeks):
        for dow, cell in enumerate(week):
            if cell is None:
                continue
            level = min(cell["level"], 4)
            color = PALETTE[level + 1] if level > 0 else PALETTE[0]
            fill = color if level > 0 else "#161b22"
            x = LEFT_PAD + week_idx * (BOX + GAP)
            y = TOP_PAD + dow * (BOX + GAP)
            delay = (week_idx + dow) * 0.012
            svg_parts.append(
                f'<rect class="box" x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" '
                f'fill="{fill}" style="animation-delay:{delay:.3f}s"/>'
            )

    # legend
    legend_y = TOP_PAD + 7 * (BOX + GAP) + 16
    svg_parts.append(f'<text class="lbl" x="{LEFT_PAD}" y="{legend_y}">Less</text>')
    lx = LEFT_PAD + 32
    for i, color in enumerate(PALETTE):
        svg_parts.append(
            f'<rect x="{lx + i * (BOX + 2)}" y="{legend_y - 9}" width="{BOX-2}" height="{BOX-2}" '
            f'rx="2" fill="{color}"/>'
        )
    svg_parts.append(f'<text class="lbl" x="{lx + len(PALETTE)*(BOX+2)+4}" y="{legend_y}">More</text>')

    # stats footer
    stats_y = legend_y + 22
    svg_parts.append(
        f'<text x="{LEFT_PAD}" y="{stats_y}">'
        f'<tspan class="stat">{total_active}</tspan><tspan class="stat-dim"> active days</tspan>'
        f'<tspan class="stat-dim">   |   </tspan>'
        f'<tspan class="stat">{current_streak}</tspan><tspan class="stat-dim"> current streak</tspan>'
        f'<tspan class="stat-dim">   |   </tspan>'
        f'<tspan class="stat">{longest_streak}</tspan><tspan class="stat-dim"> longest streak</tspan>'
        f'</text>'
    )

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def main():
    payload = load_data()
    svg = build_svg(payload)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
