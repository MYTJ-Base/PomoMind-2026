"""Small shared data types, so modules don't have to pass loose dicts around."""
from dataclasses import dataclass
from datetime import date
from typing import Optional, Tuple


@dataclass(frozen=True)
class User:
    username: str
    role: str
    subject: Optional[str] = None  # professors only


@dataclass(frozen=True)
class Course:
    """A course document broadcast by a professor."""
    filename: str
    subject: str
    content: bytes  # raw PDF bytes


@dataclass(frozen=True)
class ApiSettings:
    """What the sidebar collected: demo mode, or a Gemini API key."""
    demo: bool = False
    key: str = ""

    @property
    def ready(self) -> bool:
        return self.demo or bool(self.key)


@dataclass(frozen=True)
class Verdict:
    approved: bool
    message: str  # raw model answer, shown to the professor when blocked


@dataclass(frozen=True)
class Progress:
    """A student's saved gamification state."""
    username: str
    xp: int
    streak: int                     # value as last stored; use gamification.effective_streak() to display
    last_active: Optional[date]     # last day XP was earned
    badges: Tuple[str, ...] = ()    # badge keys, in the order they were earned


@dataclass(frozen=True)
class AwardResult:
    progress: Progress
    new_badges: Tuple[str, ...]     # badges unlocked by this award (may be empty)
