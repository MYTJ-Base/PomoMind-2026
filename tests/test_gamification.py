from datetime import date, datetime, timezone

from src.pomomind.config import BADGES
from src.pomomind.locales import STRINGS
from src.pomomind.services.gamification import (
    badges_for_xp,
    effective_streak,
    new_badges,
    next_streak,
    today_local,
)

D = date(2026, 10, 10)


def test_first_activity_starts_a_streak():
    assert next_streak(None, D, 0) == 1


def test_same_day_does_not_increase_streak():
    assert next_streak(D, D, 4) == 4


def test_next_day_increases_streak():
    assert next_streak(date(2026, 10, 9), D, 4) == 5


def test_missed_day_resets_streak():
    assert next_streak(date(2026, 10, 8), D, 4) == 1


def test_clock_going_backwards_keeps_streak():
    assert next_streak(date(2026, 10, 11), D, 4) == 4


def test_effective_streak_is_zero_without_activity():
    assert effective_streak(None, D, 0) == 0


def test_effective_streak_alive_today_and_yesterday():
    assert effective_streak(D, D, 3) == 3
    assert effective_streak(date(2026, 10, 9), D, 3) == 3


def test_effective_streak_broken_after_a_missed_day():
    assert effective_streak(date(2026, 10, 8), D, 3) == 0


def test_badges_follow_xp_thresholds():
    (first_key, first_xp), (second_key, second_xp) = BADGES[0], BADGES[1]
    assert badges_for_xp(first_xp - 1) == ()
    assert badges_for_xp(first_xp) == (first_key,)
    assert badges_for_xp(second_xp) == (first_key, second_key)


def test_new_badges_skips_owned_ones():
    first_key, first_xp = BADGES[0]
    assert new_badges((), first_xp) == (first_key,)
    assert new_badges((first_key,), first_xp) == ()


def test_today_local_uses_the_offset():
    late_evening_utc = datetime(2026, 10, 10, 23, 30, tzinfo=timezone.utc)
    assert today_local(offset_hours=1, now=late_evening_utc) == date(2026, 10, 11)
    assert today_local(offset_hours=0, now=late_evening_utc) == date(2026, 10, 10)


def test_every_badge_has_a_label_in_every_language():
    for lang, table in STRINGS.items():
        for key, _ in BADGES:
            assert f"badge.{key}" in table, f"{lang} is missing badge.{key}"
