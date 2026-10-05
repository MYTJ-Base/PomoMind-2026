"""Student area: Pomodoro timer (focus + break) with ambient sound, and the course feed."""
import time
from pathlib import Path

import streamlit as st

from pomomind.config import (
    AUDIO_DIR,
    BREAK_SECONDS,
    HEADPHONES_RECOMMENDED,
    POMODORO_SECONDS,
    SOUNDS,
    XP_FLASHCARDS,
    XP_POMODORO,
)
from pomomind.i18n import t
from pomomind.models import ApiSettings
from pomomind.services import gemini
from pomomind.services.course_store import course_store
from pomomind.ui import rewards

# <project root>/assets/audio  (this file is <root>/pomomind/ui/student.py)
_AUDIO_ROOT = Path(__file__).resolve().parents[2] / AUDIO_DIR
_MIME_TYPES = {".mp3": "audio/mp3", ".wav": "audio/wav", ".ogg": "audio/ogg"}


def render(api: ApiSettings) -> None:
    st.title(t("student.title"))
    rewards.show_pending_notices()

    course = course_store.current()
    if course:
        st.info(t("student.notification", subject=course.subject, filename=course.filename))

    timer_tab, feed_tab = st.tabs([t("student.tab_timer"), t("student.tab_feed")])
    with timer_tab:
        _timer_tab()
    with feed_tab:
        _feed_tab(api)


def _countdown(label: str, seconds: int) -> None:
    """Show a mm:ss countdown, then clear it. Blocks the page while it runs."""
    display = st.empty()
    for remaining in range(seconds, 0, -1):
        minutes, secs = divmod(remaining, 60)
        display.metric(label, f"{minutes:02d}:{secs:02d}")
        time.sleep(1)
    display.empty()


def _play_sound(sound: str) -> None:
    """Play the chosen sound from assets/audio, or say which file is missing."""
    filename = SOUNDS[sound]
    if filename is None:  # silence
        return
    if sound in HEADPHONES_RECOMMENDED:
        st.caption(t("timer.headphones"))

    path = _AUDIO_ROOT / filename
    if not path.is_file():
        st.info(t("timer.sound_missing", file=f"{AUDIO_DIR}/{filename}"))
        return

    data = path.read_bytes()
    mime = _MIME_TYPES.get(path.suffix.lower(), "audio/mp3")
    try:
        st.audio(data, format=mime, loop=True)
    except TypeError:  # older Streamlit versions have no `loop` option
        st.audio(data, format=mime)


def _timer_tab() -> None:
    st.subheader(t("timer.subheader"))

    sound = st.selectbox(t("timer.sound"), list(SOUNDS), format_func=lambda k: t(f"sound.{k}"))
    _play_sound(sound)

    if st.button(t("timer.start")):
        _countdown(t("timer.focus"), POMODORO_SECONDS)
        st.balloons()
        rewards.grant_xp(XP_POMODORO)  # saved as soon as the focus phase is complete
        st.success(t("timer.done"))
        _countdown(t("timer.break"), BREAK_SECONDS)
        st.rerun()  # refresh the sidebar (XP, streak, badges)


def _feed_tab(api: ApiSettings) -> None:
    st.subheader(t("feed.subheader"))

    course = course_store.current()
    if course is None:
        st.write(t("feed.empty"))
        return

    st.write(t("feed.document", filename=course.filename, subject=course.subject))

    if st.button(t("feed.flashcards_button")):
        if not api.ready:
            st.error(t("feed.missing_key"))
        else:
            with st.spinner(t("feed.spinner")):
                try:
                    text = gemini.generate_flashcards(api, course)
                except Exception as err:
                    st.error(t("feed.error", error=err))
                else:
                    st.session_state.flashcards = (course.filename, text)
                    rewards.grant_xp(XP_FLASHCARDS, message=t("feed.success"))
                    st.rerun()  # refresh the sidebar (XP, streak, badges)

    saved = st.session_state.flashcards
    if saved and saved[0] == course.filename:
        st.markdown("---")
        st.write(saved[1])
