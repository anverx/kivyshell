"""Generic SQLite StorageAdapter — the default backing store for the shell.

Generalized from yaque's database.py: game-specific columns (board size, seed,
num_solutions, kingdom_strategy, …) collapse into a single opaque `meta` JSON
blob, and puzzles key on (variant_id, date) instead of size. The rest — plays,
timing, completion, streak, stats — is game-agnostic and lives here so any
daily-puzzle game (yaque, yawop) reuses it unchanged.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

from .adapter import Completion, MonthStatus, PlayRecord
from .streak import compute_streak, format_streak_text

SCHEMA = """
CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant_id TEXT NOT NULL,
    date TEXT,                         -- ISO date for daily; NULL for random
    code TEXT NOT NULL UNIQUE,
    meta TEXT,                         -- opaque game-specific JSON
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_challenges_date ON challenges(date);
CREATE TABLE IF NOT EXISTS plays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id INTEGER NOT NULL REFERENCES challenges(id),
    started_at TEXT NOT NULL,
    completed_at TEXT,
    duration_ms INTEGER,
    completed INTEGER NOT NULL DEFAULT 0,
    attempts INTEGER,
    rating INTEGER
);
CREATE INDEX IF NOT EXISTS idx_plays_challenge ON plays(challenge_id);
"""


class SqliteStore:
    """A generic StorageAdapter. Pass ``:memory:`` as data_dir for tests."""

    def __init__(self) -> None:
        self._db: sqlite3.Connection | None = None

    def open(self, data_dir: str) -> None:
        path = ":memory:" if data_dir == ":memory:" else str(Path(data_dir) / "kivyshell.db")
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        self._db.executescript(SCHEMA)
        self._db.commit()

    def close(self) -> None:
        if self._db:
            self._db.close()
            self._db = None

    # --- writes ---------------------------------------------------------------
    def record_challenge(self, variant_id, date, code, meta=None) -> int:
        cur = self._db.execute(
            "INSERT OR IGNORE INTO challenges(variant_id, date, code, meta) VALUES (?,?,?,?)",
            (variant_id, date, code, json.dumps(meta) if meta is not None else None),
        )
        self._db.commit()
        if cur.lastrowid:
            return cur.lastrowid
        row = self._db.execute("SELECT id FROM challenges WHERE code=?", (code,)).fetchone()
        return row["id"]

    def start_play(self, challenge_id) -> int:
        cur = self._db.execute(
            "INSERT INTO plays(challenge_id, started_at) VALUES (?,?)",
            (challenge_id, datetime.now().isoformat()),
        )
        self._db.commit()
        return cur.lastrowid

    def finish_play(self, play_id, won: bool, duration_ms=None, attempts=None) -> None:
        """Finalize a play, win or lose. `completed` = solved; `completed_at` is set
        either way so finished (incl. lost) games are distinguishable from abandoned
        ones. `attempts` = number of tries (e.g. guesses)."""
        self._db.execute(
            "UPDATE plays SET completed=?, completed_at=?, duration_ms=?, attempts=? WHERE id=?",
            (1 if won else 0, datetime.now().isoformat(), duration_ms, attempts, play_id),
        )
        self._db.commit()

    def complete_play(self, play_id, duration_ms, attempts=None) -> None:
        """Record a solved play (back-compat convenience over finish_play)."""
        self.finish_play(play_id, True, duration_ms, attempts)

    def rate_play(self, play_id, rating) -> None:
        self._db.execute("UPDATE plays SET rating=? WHERE id=?", (rating, play_id))
        self._db.commit()

    # --- reads ----------------------------------------------------------------
    def _completion(self, challenge_date: str | None, completed_at: str | None) -> Completion:
        if not completed_at:
            return Completion.NONE
        if challenge_date and completed_at[:10] == challenge_date:
            return Completion.ON_TIME
        return Completion.LATE

    def completion_today(self, date, variant_ids) -> dict[str, Completion]:
        out = {v: Completion.NONE for v in variant_ids}
        rows = self._db.execute(
            """SELECT c.variant_id, MIN(p.completed_at) AS ca
               FROM challenges c JOIN plays p ON p.challenge_id=c.id
               WHERE c.date=? AND p.completed=1 GROUP BY c.variant_id""",
            (date,),
        ).fetchall()
        for r in rows:
            if r["variant_id"] in out:
                out[r["variant_id"]] = self._completion(date, r["ca"])
        return out

    def month_status(self, year, month, variant_ids) -> MonthStatus:
        prefix = f"{year:04d}-{month:02d}"
        rows = self._db.execute(
            """SELECT c.date, c.variant_id, MIN(p.completed_at) AS ca
               FROM challenges c JOIN plays p ON p.challenge_id=c.id
               WHERE c.date LIKE ? AND p.completed=1
               GROUP BY c.date, c.variant_id""",
            (prefix + "%",),
        ).fetchall()
        days: dict[str, dict[str, Completion]] = {}
        for r in rows:
            days.setdefault(r["date"], {})[r["variant_id"]] = self._completion(r["date"], r["ca"])
        month_name = date(year, month, 1).strftime("%B %Y")
        streak = self.streak()
        badge = Completion.ON_TIME if days and all(
            any(s == Completion.ON_TIME for s in d.values()) for d in days.values()
        ) else (Completion.LATE if days else Completion.NONE)
        return MonthStatus(month_name=month_name, streak_text=format_streak_text(streak),
                           days=days, month_badge=badge)

    def all_plays(self, limit=50, offset=0, sort_by="time") -> list[PlayRecord]:
        order = {"time": "p.started_at DESC", "duration": "p.duration_ms ASC",
                 "rating": "p.rating DESC"}.get(sort_by, "p.started_at DESC")
        rows = self._db.execute(
            f"""SELECT c.variant_id, c.date, c.code, p.started_at, p.completed_at,
                       p.duration_ms, p.completed, p.attempts, p.rating
                FROM plays p JOIN challenges c ON c.id=p.challenge_id
                ORDER BY {order} LIMIT ? OFFSET ?""",
            (limit, offset),
        ).fetchall()
        return [PlayRecord(variant_id=r["variant_id"], date=r["date"], code=r["code"],
                           started_at=r["started_at"], completed_at=r["completed_at"],
                           duration_ms=r["duration_ms"], completed=bool(r["completed"]),
                           attempts=r["attempts"], rating=r["rating"]) for r in rows]

    def stats(self) -> dict:
        row = self._db.execute(
            """SELECT COUNT(*) AS plays, SUM(completed) AS completed,
                      AVG(CASE WHEN completed=1 THEN duration_ms END) AS avg_ms,
                      SUM(CASE WHEN completed=1 THEN duration_ms ELSE 0 END) AS total_ms,
                      AVG(CASE WHEN completed=1 THEN attempts END) AS avg_attempts
               FROM plays WHERE completed_at IS NOT NULL""",
        ).fetchone()
        return {"plays": row["plays"] or 0, "completed": row["completed"] or 0,
                "avg_ms": int(row["avg_ms"]) if row["avg_ms"] else None,
                "total_ms": row["total_ms"] or 0,
                "avg_attempts": round(row["avg_attempts"], 1) if row["avg_attempts"] else None}

    def _played_dates(self) -> set[str]:
        """Dates whose daily puzzle was completed on that same date (for streaks)."""
        rows = self._db.execute(
            """SELECT DISTINCT c.date FROM challenges c JOIN plays p ON p.challenge_id=c.id
               WHERE c.date IS NOT NULL AND p.completed=1 AND substr(p.completed_at,1,10)=c.date""",
        ).fetchall()
        return {r["date"] for r in rows}

    def streak(self, ref_date=None) -> int:
        ref = date.fromisoformat(ref_date) if ref_date else None
        return compute_streak(self._played_dates(), ref)
