"""Pure gamification rules: streaks, badges, "what day is it". No Streamlit, no database."""
from datetime import date, datetime, timedelta, timezone
from typing import Optional, Sequence, Tuple

from pomomind.config import APP_UTC_OFFSET_HOURS, BADGES


def today_local(offset_hours: int = APP_UTC_OFFSET_HOURS, now: Optional[datetime] = None) -> date:
    """Today's date in the app's timezone (a fixed UTC offset, no daylight saving).

    `now` must be timezone-aware; it exists so tests can fake the clock.
    """
    now = now or datetime.now(timezone.utc)
    return now.astimezone(timezone(timedelta(hours=offset_hours))).date()


def next_streak(last_active: Optional[date], today: date, current: int) -> int:
    """New streak value after the student earns XP on `today`."""
    if last_active is None:
        return 1
    gap = (today - last_active).days
    if gap == 0:        # already counted today
        return max(current, 1)
    if gap == 1:        # consecutive day
        return current + 1
    if gap < 0:         # clock went backwards: don't punish the student
        return max(current, 1)
    return 1            # missed at least one full day: start again


def effective_streak(last_active: Optional[date], today: date, stored: int) -> int:
    """Streak to DISPLAY today: a stored streak is broken once a full day was missed."""
    if last_active is None:
        return 0
    return stored if (today - last_active).days <= 1 else 0


def badges_for_xp(xp: int, rules: Sequence[Tuple[str, int]] = BADGES) -> Tuple[str, ...]:
    """Keys of every badge a student with `xp` points deserves."""
    return tuple(key for key, needed in rules if xp >= needed)


def new_badges(owned: Sequence[str], xp: int, rules: Sequence[Tuple[str, int]] = BADGES) -> Tuple[str, ...]:
    """Badges deserved at `xp` that the student does not own yet."""
    return tuple(key for key in badges_for_xp(xp, rules) if key not in owned)
