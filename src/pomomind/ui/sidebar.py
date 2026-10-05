"""Sidebar: language picker (always) and account panel (logged-in only)."""
import streamlit as st

from pomomind import state
from pomomind.config import LANGUAGES, ROLE_STUDENT
from pomomind.i18n import LANGUAGE_KEY, t
from pomomind.models import ApiSettings
from pomomind.services.gamification import effective_streak, today_local
from pomomind.services.progress_store import progress_store


def language_selector() -> None:
    st.sidebar.selectbox(
        t("language.label"),
        list(LANGUAGES),
        format_func=lambda code: LANGUAGES[code],
        key=LANGUAGE_KEY,
    )


def _student_metrics() -> None:
    """Streak, XP and badges, read from the saved progress (so they survive logout)."""
    progress = progress_store.get(st.session_state.username)
    streak = effective_streak(progress.last_active, today_local(), progress.streak)
    streak_text = t("sidebar.streak_one" if streak == 1 else "sidebar.streak_many", days=streak)
    st.sidebar.metric(t("sidebar.streak"), streak_text)
    st.sidebar.metric(t("sidebar.score"), f"{progress.xp} XP")
    if progress.badges:
        st.sidebar.caption(t("sidebar.badges"))
        for key in progress.badges:
            st.sidebar.write("🏅 " + t(f"badge.{key}"))


def account_panel() -> ApiSettings:
    """Render role info, API settings and logout. Returns the collected API settings."""
    role = st.session_state.role
    st.sidebar.title(t("sidebar.title", role=t(f"role.{role}")))

    if role == ROLE_STUDENT:
        _student_metrics()

    demo = st.sidebar.checkbox(t("sidebar.demo_mode"), value=False)
    key = "" if demo else st.sidebar.text_input(t("sidebar.api_key"), type="password")

    if st.sidebar.button(t("sidebar.logout")):
        state.log_out()
        st.rerun()

    return ApiSettings(demo=demo, key=key)
