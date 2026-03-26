import streamlit as st
import replicate
import os
import json
import time
import requests

# =========================
# 0. DATABAS & ANVÄNDARE
# =========================

DB_FILE = "users.json"

def init_user_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({}, f)

def load_db():
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def load_user(artist_id):
    db = load_db()
    if artist_id not in db:
        db[artist_id] = {
            "units": 20,
            "bg": None,
            "gallery": []
        }
        save_db(db)
    return db[artist_id]

def update_user(artist_id, key, value):
    db = load_db()
    if artist_id not in db:
        db[artist_id] = {
            "units": 20,
            "bg": None,
            "gallery": []
        }
    db[artist_id][key] = value
    save_db(db)

def add_to_gallery(artist, name, img_url, audio_url):
    db = load_db()
    if artist not in db:
        db[artist] = {
            "units": 20,
            "bg": None,
            "gallery": []
        }
    entry = {
        "id": time.time(),
        "artist": artist,
        "name": name[:30] if name else "UNTITLED",
        "url": img_url,
        "audio": audio_url
    }
    db[artist]["gallery"].append(entry)
    save_db(db)

def get_user_gallery(artist):
    db = load_db()
    if artist not in db:
        return []
    return db[artist].get("gallery", [])

def get_global_feed():
    db = load_db()
    feed = []
    for artist in db:
        feed.extend(db[artist].get("gallery", []))
    return feed

# =========================
# 1. SPRÅK & TEXTER
# =========================

LANG = {
    "Svenska": {
        "title": "MAXIMUSIKAI SUPER STUDIO",
        "status": "STATUS",
        "units": "Units",
        "magic_tab": "🪄 MAGI",
        "director_tab": "🎬 REGI",
        "music_tab": "🎧 MUSIK",
        "archive_tab": "📚 ARKIV",
        "feed_tab": "🌐 FEED",
        "admin_tab": "⚙️ ADMIN",
        "prompt_label": "Vad ska vi skapa?",
        "generate_btn": "GENERERA",
        "no_gallery": "Inga verk ännu.",
        "create_first": "Skapa något i MAGI först.",
        "beat_label": "Beskriv beatet:",
        "create_sound": "SKAPA LJUD",
        "video_instr": "Instruktion:",
        "create_video": "SKAPA VIDEO",
        "open_studio": "GODKÄNN & ÖPPNA STUDION",
        "studio_title": "STUDIO",
        "artist_id": "ARTIST ID:",
        "lang_label": "Språk:",
        "theme_label": "Tema:",
        "admin_only": "Endast för admin.",
        "admin_panel": "ADMIN PANEL",
    },
    "English": {
        "title": "MAXIMUSIKAI SUPER STUDIO",
        "status": "STATUS",
        "units": "Units",
        "magic_tab": "🪄 MAGIC",
        "director_tab": "🎬 DIRECTOR",
        "music_tab": "🎧 MUSIC",
        "archive_tab": "📚 ARCHIVE",
        "feed_tab": "🌐 FEED",
        "admin_tab": "⚙️ ADMIN",
        "prompt_label": "What shall we create?",
        "generate_btn": "GENERATE",
        "no_gallery": "No works yet.",
        "create_first": "Create something in MAGIC first.",
        "beat_label": "Describe the beat:",
        "create_sound": "CREATE SOUND",
        "video_instr": "Instruction:",
        "create_video": "CREATE VIDEO",
        "open_studio": "ACCEPT & OPEN STUDIO",
        "studio_title": "STUDIO",
        "artist_id": "ARTIST ID:",
        "lang_label": "Language:",
        "theme_label": "Theme:",
        "admin_only": "Admin only.",
        "admin_panel": "ADMIN PANEL",
    }
}

def get_texts(lang):
    return LANG.get(lang, LANG["Svenska"])

# =========================
# 2. DESIGN
# =========================

def apply_design():
    theme = st.session_state.get("theme", "Neon")
    bg = st.session_state.get("app_bg", None)

    base_css = """
    <style>
    .stApp {
        background-color: #050505;
        color: white;
    }
    h1, h2, h3 {
        font-weight: 900;
    }
    </style>
    """

    neon_css = """
    <style>
    .stApp {
        background: #000000;
        color: #ffffff;
    }
    h1, h2, h3 {
        text-shadow: 0 0 10px #0ff, 0 0 20px #0ff;
    }
    </style>
    """

    cyber_css = """
    <style>
    .stApp {
        background: radial-gradient(circle at top, #1a2a3a, #000000);
        color: #e0e0ff;
    }
    h1, h2, h3 {
        text-shadow: 0 0 15px #ff00ff;
    }
    </style>
    """

    if bg:
        bg_css = f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), url("{bg}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
            color: white;
        }}
        </style>
        """
    else:
        bg_css = ""

    if theme == "Neon":
        css = neon_css
    elif theme == "Cyberpunk":
        css = cyber_css
    else:
        css = base_css

    st.markdown(css + bg_css, unsafe_allow_html=True)

def theme_selector(label):
    st.session_state.theme = st.selectbox(
        label,
        ["Neon", "Dark", "
