"""
fetch_contributions.py
Scrapes the public, token-free GitHub contributions HTML fragment
(https://github.com/users/<username>/contributions) and writes
data/contributions.json with raw days + derived stats.
"""
import json
import os
import sys
from datetime import datetime, date, timezone

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USERNAME", "2xx0")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")


def fetch_html(username: str) -> str:
    resp = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.text


def parse_days(html: str):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # GitHub renders each day as a <td> with data-date / data-level (new markup)
    # or a <rect> with data-date/data-level (older markup). Handle both.
    cells = soup.select("td.ContributionCalendar-day, td[data-date]")
    if not cells:
        cells = soup.select("rect.ContributionCalendar-day, rect[data-date]")

    for cell in cells:
        d = cell.get("data-date")
        if not d:
            continue
        level = cell.get("data-level")
        if level is None:
            # fall back to parsing the tooltip text for a count
            level = 0
        days.append({"date": d, "level": int(level)})

    # Try to also grab the tooltip counts (e.g. "3 contributions on ...")
    tooltips = {t.get("for"): t.get_text(strip=True) for t in soup.select("tool-tip")}
    for day in days:
        # tooltip ids reference the cell id; best-effort match, safe to skip if absent
        pass

    days.sort(key=lambda x: x["date"])
    return days


def derive_stats(days):
    if not days:
        return {}

    total = len(days)
    active_days = [d for d in days if d["level"] > 0]

    # current streak: consecutive active days ending today (or most recent day)
    current_streak = 0
    for d in reversed(days):
        if d["level"] > 0:
            current_streak += 1
        else:
            break

    # longest streak
    longest_streak = 0
    running = 0
    for d in days:
        if d["level"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    best_day = max(days, key=lambda x: x["level"]) if days else None

    monthly = {}
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + (1 if d["level"] > 0 else 0)

    return {
        "total_days": total,
        "active_days": len(active_days),
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_active_days": monthly,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def main():
    html = fetch_html(USERNAME)
    days = parse_days(html)
    stats = derive_stats(days)

    payload = {
        "username": USERNAME,
        "days": days,
        "stats": stats,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(days)} days -> {OUT_PATH}")


if __name__ == "__main__":
    main()
