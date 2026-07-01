"""Tests for the pure streak logic (no kivy)."""

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kivyshell.shell import compute_streak, format_streak_text  # noqa: E402


class TestStreak(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(compute_streak(set()), 0)

    def test_consecutive_ending_today(self):
        today = date.today()
        played = {(today - timedelta(days=i)).isoformat() for i in range(5)}
        self.assertEqual(compute_streak(played), 5)

    def test_grace_period_yesterday(self):
        today = date.today()
        played = {(today - timedelta(days=i)).isoformat() for i in range(1, 4)}  # not today
        self.assertEqual(compute_streak(played), 3)

    def test_broken_streak(self):
        today = date.today()
        played = {(today - timedelta(days=i)).isoformat() for i in (0, 1, 4, 5)}
        self.assertEqual(compute_streak(played), 2)  # today + yesterday, gap at 2/3

    def test_stale_streak_is_zero(self):
        played = {"2000-01-01", "2000-01-02"}
        self.assertEqual(compute_streak(played), 0)

    def test_format(self):
        self.assertEqual(format_streak_text(0), "Start a streak!")
        self.assertEqual(format_streak_text(1), "Streak: 1 day")
        self.assertEqual(format_streak_text(3), "Streak: 3 days")


if __name__ == "__main__":
    unittest.main()
