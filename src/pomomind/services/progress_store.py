"""Saves each student's XP, streak and badges in a SQLite file, so they survive logout and restarts.

Only the standard library is used. Each call opens its own short-lived connection,
which keeps it safe with Streamlit's several threads. The file lives at config.PROGRESS_DB_PATH.

Limit: hosts with a temporary disk (e.g. free cloud tiers) erase the file on redeploy or restart.
To scale, keep `get` / `award_xp` and swap the internals for a real database.
"""
import os
import sqlite3
from contextlib import closing
from datetime import date
from typing import Optional

from pomomind.config import PROGRESS_DB_PATH, STARTING_XP
from pomomind.models import AwardResult, Progress
from pomomind.services.gamification import new_badges, next_streak, today_local

_SCHEMA = """
CREATE TABLE IF NOT EXISTS progress (
    username    TEXT PRIMARY KEY,
    xp          INTEGER NOT NULL,
    streak      INTEGER NOT NULL,
    last_active TEXT,
    badges      TEXT NOT NULL DEFAULT ''
)
"""
_SELECT = "SELECT xp, streak, last_active, badges FROM progress WHERE username = ?"


def _to_progress(username: str, row) -> Progress:
    if row is None:  # a student we have never seen: starting values, nothing saved yet
        return Progress(username, STARTING_XP, 0, None, ())
    xp, streak, last_active, badges = row
    return Progress(
        username,
        xp,
        streak,
        date.fromisoformat(last_active) if last_active else None,
        tuple(b for b in badges.split(",") if b),
    )


class ProgressStore:
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        folder = os.path.dirname(self._db_path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        conn = sqlite3.connect(self._db_path, timeout=10, isolation_level=None)
        conn.execute(_SCHEMA)
        return conn

    def get(self, username: str) -> Progress:
        with closing(self._connect()) as conn:
            return _to_progress(username, conn.execute(_SELECT, (username,)).fetchone())

    def award_xp(self, username: str, amount: int, today: Optional[date] = None) -> AwardResult:
        """Add XP, update the streak, unlock badges, and save: all in one transaction."""
        if amount <= 0:
            raise ValueError("amount must be positive")
        today = today or today_local()
        with closing(self._connect()) as conn:
            conn.execute("BEGIN IMMEDIATE")  # lock so two sessions can't overwrite each other
            try:
                current = _to_progress(username, conn.execute(_SELECT, (username,)).fetchone())
                xp = current.xp + amount
                unlocked = new_badges(current.badges, xp)
                updated = Progress(
                    username,
                    xp,
                    next_streak(current.last_active, today, current.streak),
                    max(today, current.last_active) if current.last_active else today,
                    current.badges + unlocked,
                )
                conn.execute(
                    "INSERT OR REPLACE INTO progress (username, xp, streak, last_active, badges)"
                    " VALUES (?, ?, ?, ?, ?)",
                    (username, updated.xp, updated.streak,
                     updated.last_active.isoformat(), ",".join(updated.badges)),
                )
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
        return AwardResult(updated, unlocked)


progress_store = ProgressStore(PROGRESS_DB_PATH)
