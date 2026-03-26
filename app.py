import streamlit as st
import os
import json
import time

# --- 0. DATABAS FÖR ANVÄNDARE (UNITS + BAKGRUND) ---

DB_FILE = "users.json"


def load_user_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

    with open(DB_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_user_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)


# --- 1. SETUP & SESSION STATE ---

st.set_page_config(
    page_title="MAXIMUSIKAI STUDIO PRO 2026",
    page_icon="⚡",
    layout="wide",
)

if "gallery" not in st.session_state:
    st.session_state.gallery = []

if "user_db" not in st.session_state:
    st.session_state.user_db = load_user_db()

if "app_bg" not in st.session_state:
    st.session_state.app_bg = None

if "agreed" not in st.session_state:
    st.session_state.agreed = False

if "lang" not in st.session_state:
    st.session_state.lang = "Svenska"

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "units" not in st.session_state:
    st.session_state.units = 0

