"""Tests for the generic SQLite StorageAdapter (no kivy)."""

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from kivyshell.shell import Completion, PlayRecord, SqliteStore  # noqa: E402


class TestSqliteStore(unittest.TestCase):
    def setUp(self):
        self.s = SqliteStore()
        self.s.open(":memory:")

    def tearDown(self):
        self.s.close()

    def _play(self, variant, chdate, code, complete=True, duration=1000):
        cid = self.s.record_challenge(variant, chdate, code, meta={"note": "x"})
        pid = self.s.start_play(cid)
        if complete:
            self.s.complete_play(pid, duration)
        return cid, pid

    def _backdate_ontime(self, variant, chdate, code):
        """Insert a play completed on its own date (can't do that via the public
        API, which stamps now()) — needed to simulate a historical streak."""
        cid = self.s.record_challenge(variant, chdate, code)
        self.s._db.execute(
            "INSERT INTO plays(challenge_id, started_at, completed_at, duration_ms, completed) "
            "VALUES (?,?,?,?,1)",
            (cid, f"{chdate}T12:00:00", f"{chdate}T12:05:00", 300000),
        )
        self.s._db.commit()

    def test_record_challenge_is_idempotent_by_code(self):
        a = self.s.record_challenge("v6", "2026-07-01", "CODE1")
        b = self.s.record_challenge("v6", "2026-07-01", "CODE1")
        self.assertEqual(a, b)

    def test_completion_today_on_time_vs_none(self):
        today = date.today().isoformat()
        self._play("v6", today, "c-today")            # completed same day -> ON_TIME
        self._play("v7", today, "c-open", complete=False)  # started, not completed -> NONE
        status = self.s.completion_today(today, ["v6", "v7", "v8"])
        self.assertEqual(status["v6"], Completion.ON_TIME)
        self.assertEqual(status["v7"], Completion.NONE)
        self.assertEqual(status["v8"], Completion.NONE)

    def test_completion_late_when_solved_after_puzzle_date(self):
        old = "2000-01-01"
        self._play("v6", old, "c-old")  # completed today, puzzle dated 2000 -> LATE
        status = self.s.completion_today(old, ["v6"])
        self.assertEqual(status["v6"], Completion.LATE)

    def test_streak_counts_on_time_daily(self):
        today = date.today()
        for i in range(3):
            d = (today - timedelta(days=i)).isoformat()
            self._backdate_ontime("v6", d, f"c{i}")
        self.assertEqual(self.s.streak(), 3)

    def test_streak_zero_without_recent_play(self):
        self._play("v6", "2000-01-01", "c-old")  # LATE, not counted for streak
        self.assertEqual(self.s.streak(), 0)

    def test_month_status_and_all_plays_and_stats(self):
        today = date.today()
        self._play("v6", today.isoformat(), "c1", duration=1500)
        ms = self.s.month_status(today.year, today.month, ["v6", "v7"])
        self.assertIn(today.isoformat(), ms.days)
        self.assertEqual(ms.days[today.isoformat()]["v6"], Completion.ON_TIME)

        plays = self.s.all_plays()
        self.assertIsInstance(plays[0], PlayRecord)
        self.assertTrue(plays[0].completed)

        st = self.s.stats()
        self.assertEqual(st["completed"], 1)
        self.assertEqual(st["total_ms"], 1500)

    def test_finish_play_records_loss_and_attempts(self):
        cid = self.s.record_challenge("v6", None, "c-loss")
        pid = self.s.start_play(cid)
        self.s.finish_play(pid, won=False, duration_ms=5000, attempts=6)
        p = self.s.all_plays()[0]
        self.assertEqual(p.attempts, 6)
        self.assertFalse(p.completed)              # lost
        self.assertIsNotNone(p.completed_at)       # finished, not abandoned

    def test_complete_play_records_attempts(self):
        cid = self.s.record_challenge("v6", None, "c-win")
        pid = self.s.start_play(cid)
        self.s.complete_play(pid, 3000, attempts=3)
        p = self.s.all_plays()[0]
        self.assertTrue(p.completed)
        self.assertEqual(p.attempts, 3)
        self.assertEqual(self.s.stats()["avg_attempts"], 3.0)


if __name__ == "__main__":
    unittest.main()
