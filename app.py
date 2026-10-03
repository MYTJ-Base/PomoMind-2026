"""PomoMind AI - Streamlit entry point.

Run with:  streamlit run app.py

This file only wires things together. Features live in the `pomomind` package.
"""
import streamlit as st

from src.pomomind import state
from src.pomomind.config import APP_ICON, APP_NAME, ROLE_PROFESSOR
from src.pomomind.ui import student
from src.pomomind.ui import sidebar
from src.pomomind.ui import login, professor

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON)

state.init()
sidebar.language_selector()

if not state.is_logged_in():
    login.render()
else:
    api = sidebar.account_panel()
    if st.session_state.role == ROLE_PROFESSOR:
        professor.render(api)
    else:
        student.render(api)
