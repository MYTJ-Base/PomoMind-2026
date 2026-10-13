import os
import tempfile
from datetime import date, timedelta

from src.pomomind.config import BADGES, STARTING_XP
from src.pomomind.services.progress_store import ProgressStore

D = date(2026, 10, 10)


def _store(folder):
    return ProgressStore(os.path.join(folder, "sub", "test.db"))  # also checks the folder is created


def test_unknown_user_gets_starting_values_without_saving():
    with tempfile.TemporaryDirectory() as folder:
        progress = _store(folder).get("newbie")
        assert (progress.xp, progress.streak, progress.last_active, progress.badges) == (STARTING_XP, 0, None, ())


def test_award_adds_xp_and_starts_streak():
    with tempfile.TemporaryDirectory() as folder:
        result = _store(folder).award_xp("ada", 50, today=D)
        assert result.progress.xp == STARTING_XP + 50
        assert result.progress.streak == 1
        assert result.progress.last_active == D


def test_progress_survives_a_restart():
    with tempfile.TemporaryDirectory() as folder:
        _store(folder).award_xp("ada", 50, today=D)
        reloaded = _store(folder).get("ada")  # a brand-new object, like after a server restart
        assert reloaded.xp == STARTING_XP + 50
        assert reloaded.last_active == D


def test_two_awards_same_day_count_one_streak_day():
    with tempfile.TemporaryDirectory() as folder:
        store = _store(folder)
        store.award_xp("ada", 50, today=D)
        assert store.award_xp("ada", 20, today=D).progress.streak == 1


def test_consecutive_days_build_streak_and_gap_resets_it():
    with tempfile.TemporaryDirectory() as folder:
        store = _store(folder)
        store.award_xp("ada", 50, today=D)
        assert store.award_xp("ada", 50, today=D + timedelta(days=1)).progress.streak == 2
        assert store.award_xp("ada", 50, today=D + timedelta(days=4)).progress.streak == 1


def test_badge_is_unlocked_once():
    key, needed = BADGES[0]
    with tempfile.TemporaryDirectory() as folder:
        store = _store(folder)
        first = store.award_xp("ada", needed - STARTING_XP, today=D)
        assert first.new_badges == (key,)
        second = store.award_xp("ada", 10, today=D)
        assert second.new_badges == ()
        assert store.get("ada").badges == (key,)


def test_users_are_independent():
    with tempfile.TemporaryDirectory() as folder:
        store = _store(folder)
        store.award_xp("ada", 50, today=D)
        assert store.get("bob").xp == STARTING_XP


def test_non_positive_amount_is_rejected():
    with tempfile.TemporaryDirectory() as folder:
        try:
            _store(folder).award_xp("ada", 0, today=D)
        except ValueError:
            return
        raise AssertionError("expected ValueError")
