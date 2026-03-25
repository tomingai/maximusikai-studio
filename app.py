import streamlit as st
import os
import json
import requests
import time
# --- 0. DATABAS FÖR ANVÄNDARE (UNITS + BAKGRUND) ---
DB_FILE = "users.json"
def load_user_db():
if not os.path.exists(DB_FILE):
with open(DB_FILE, "w") as f:
json.dump({}, f)
with open(DB_FILE, "r") as f:
try:
return json.load(f)
except json.JSONDecodeError:
return {}
def save_user_db(db):
with open(DB_FILE, "w") as f:
json.dump(db, f, indent=4)
# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")
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
# --- 2. DESIGN ---
def apply_design():
if st.session_state.app_bg:
bg_url = str(st.session_state.app_bg)
st.markdown(
f"""
.stApp {{
background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('{bg_url}') !important;
background-size: cover !important;
background-position: center !important;
background-attachment: fixed !important;
}}
.logo-text {{
font-size: 3rem !important;
font-weight: 900 !important;
color: #fff !important;
text-align: center;
text-transform: uppercase;
letter-spacing: 5px;
text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #00d2ff, 0 0 40px #00d2ff !important;
margin-bottom: 20px;
}}
div[data-baseweb="base-input"], div[data-baseweb="textarea"], .stTextArea textarea, .stTextInput input {{
background-color: rgba(255,255,255,0.1) !important;
color: white !important;
backdrop-filter: blur(15px) !important;
border: 1px solid rgba(255,255,255,0.2) !important;
border-radius: 12px !important;
}}
label, p, span, h1, h2, h3, .stTabs [data-baseweb="tab"] {{
color: white !important;
text-shadow: 2px 2px 8px rgba(0,0,0,1) !important;
font-weight: 800 !important;
}}
.stTabs [data-baseweb="tab-list"] {{
background-color: rgba(0,0,0,0.4) !important;
border-radius: 10px !important;
}}
""",
unsafe_allow_html=True,
)
else:
st.markdown(".stApp { background-color: #050505 !important; }", unsafe_allow_html=True)
# --- 3. HJÄLPFUNKTION FÖR URL ---
def get_url(res):
if isinstance(res, list):
return str(res[0])
if hasattr(res, "url"):
return str(res.url)
return str(res)
# --- 4. SPRÅK ---
texts = {
"Svenska": {
"title": "MAXIMUSIKAI STUDIO",
"tab_names": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED", "⚙️ ADMIN"],
"atm_space": "RYMDEN 🌌",
"atm_forest": "SKOGEN 🌲",
"atm_city": "STADEN 🌆",
"atm_bake": "BAKNING 🥐",
"status": "STATUS",
"units": "UNITS",
"set_bg": "🖼 SÄTT SOM BAKGRUND",
"download": "💾 LADDA NER",
"studio": "STUDIO",
"lang_label": "Språk:",
"artist_id": "ARTIST ID:",
"atmosphere": "ATMOSFÄR",
"reset_design": "❌ NOLLSTÄLL DESIGN",
"agree_open": "GODKÄNN & ÖPPNA STUDION",
"prompt_label": "VAD SKALL VI SKAPA?",
"start_gen": "STARTA GENERERING",
"no_units": "Du har slut på Units!",
"empty_prompt": "Skriv en prompt först.",
"ai_working": "AI arbetar...",
"luma_sub": "🎬 LUMA DREAM MACHINE",
"need_magic_first": "Skapa en bild i MAGI först!",
"select_image_label": "Välj bild:",
"instruction": "Instruktion:",
"create_video": "SKAPA VIDEO (5 UNITS)",
"too_few_units": "För få Units!",
"music_desc": "Beskriv beatet:",
"create_sound": "SKAPA LJUD",
"need_music_desc": "Skriv en beskrivning först.",
"composing": "Komponerar...",
"archive_empty": "Inga sparade verk.",
"work_saved": "Verket är skapat och sparat i ARKIV & FEED.",
"no_image": "Ingen bild kunde skapas.",
"bg_fail": "Kunde inte generera bakgrund:",
"img_fail": "Bildgenerering misslyckades:",
"music_fail": "Musikgenerering misslyckades:",
"luma_fail": "Luma är upptagen eller kräver betalkonto.",
"admin_panel": "ADMIN PANEL",
"user_db": "User DB:",
"gallery_cleared": "Gallery rensat.",
"api_missing": "API TOKEN SAKNAS"


        "













































































































































































































































































