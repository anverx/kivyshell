"""Generic daily-streak logic (ported/generalized from yaque's calendar_logic).

Pure functions over a set of ISO date strings — no game specifics, no DB. The
consecutive-day core is here; yaque's streak-protection milestones (banked at 10
and 30 consecutive days) are ported verbatim during the extraction phase and
plug in via `protections`.
"""

from __future__ import annotations

from datetime import date, timedelta


def compute_streak(played_dates: set[str], ref_date: date | None = None) -> int:
    """Length of the consecutive-day run ending at ref_date (today), with a
    one-day grace period (a streak stays alive if yesterday was played)."""
    if not played_dates:
        return 0
    ref = ref_date or date.today()
    if ref.isoformat() in played_dates:
        cur = ref
    elif (ref - timedelta(days=1)).isoformat() in played_dates:
        cur = ref - timedelta(days=1)
    else:
        return 0
    length = 0
    while cur.isoformat() in played_dates:
        length += 1
        cur -= timedelta(days=1)
    return length


def format_streak_text(streak: int) -> str:
    if streak <= 0:
        return "Start a streak!"
    return f"Streak: {streak} day{'s' if streak != 1 else ''}"
