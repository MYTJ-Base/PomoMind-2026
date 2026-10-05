"""Reward feedback shared by the screens: give XP, then tell the student (toasts).

Toasts are queued in session state and shown at the start of the NEXT run, because the
screens call st.rerun() right after a reward (to refresh the sidebar) and that would erase them.
"""
import streamlit as st

from pomomind.i18n import t
from pomomind.services.progress_store import progress_store


def grant_xp(amount: int, message: str = "") -> None:
    """Save `amount` XP for the logged-in student and queue the messages to show.

    `message` replaces the default "+<amount> XP" toast when you want something more specific.
    """
    result = progress_store.award_xp(st.session_state.username, amount)
    messages = [message or f"+{amount} XP"]
    messages += [t("rewards.badge", badge=t(f"badge.{key}")) for key in result.new_badges]
    st.session_state.pending_notices = (*st.session_state.pending_notices, *messages)


def show_pending_notices() -> None:
    """Show (then clear) the queued toasts. Call once near the top of the screen."""
    for message in st.session_state.pending_notices:
        st.toast(message)
    st.session_state.pending_notices = ()
