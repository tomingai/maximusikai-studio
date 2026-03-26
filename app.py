import streamlit as st
import replicate
import os
import time
import requests
import json
import os.path

# --- 0. DATABASFUNKTIONER ---
DB_FILE = "users.json"

def load_user_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: json.dump({}, f)
    with open(DB_FILE, "r") as f:
        try: return json.load(f)
        except: return {}

def save_user_db(db):
    with open(DB_FILE, "w") as f: json.dump(db, f, indent=4)

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = load_user_db()
if "app_bg" not in st.session_state: st.session_state.app_bg = None
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. DESIGN ---
def apply_design():
    bg_url = st.session_state.app_bg if st.session_state.app_bg else "https://images.unsplash.com"
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url("{bg_url}") !important;
            background-size: cover !important; background-attachment: fixed !important;
        }}
        .logo-text {{
            font-size: 3rem; font-weight: 900; color: #fff; text-align: center;
            text-transform: uppercase; letter-spacing: 5px;
            text-shadow: 0 0 10px #00d2ff; margin-bottom: 20px;
        }}
        div[data-baseweb="base-input"], textarea, input {{
            background-color: rgba(255,255,255,0.05) !important;
            backdrop-filter: blur(15px) !important; color: white !important;
            border: 1px solid rgba(0, 210, 255, 0.3) !important;
        }}
        h1, h2, h3, p, label, .stTabs [data-baseweb="tab"] {{
            color: white !important; text-shadow: 2px 2px 8px #000;
        }}
        </style>
        <div class="logo-text">⚡ MAXIMUSIKAI STUDIO ⚡</div>
    """, unsafe_allow_html=True)

# --- 3. LOGIK & MENY ---
with st.sidebar:
    st.title("COMMAND")
    st.session_state.lang = st.radio("Språk:", ["Svenska", "English", "Deutsch"], horizontal=True)
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    
    if artist_id not in st.session_state.user_db:
        st.session_state.user_db[artist_id] = 10
        save_user_db(st.session_state.user_db)
    
    is_admin = (artist_id == "TOMAS2026")
    st.metric("UNITS", st.session_state.user_db[artist_id])
    
    if st.button("🚀 SYNC SPACE CORE"):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Deep space nebula, futuristic, 8k"})
        st.session_state.app_bg = str(res[0] if isinstance(res, list) else res)
        st.rerun()

# --- 4. HUVUDAPP ---
apply_design()

if not st.session_state.agreed:
    if st.button("OPEN NEURAL LINK", use_container_width=True):
        st.session_state.agreed = True; st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "🌐 FEED"])

    with tabs[0]: # MAGI
        prompt = st.text_area("VAD SKALL VI SKAPA?")
        if st.button("STARTA GENERERING"):
            if st.session_state.user_db[artist_id] > 0 or is_admin:
                with st.status("AI arbetar..."):
                    img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    img_url = str(img[0] if isinstance(img, list) else img)
                    st.session_state.gallery.append({"artist": artist_id, "url": img_url, "name": prompt})
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    save_user_db(st.session_state.user_db)
                    st.rerun()

    with tabs[3]: # ARKIV
        my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        cols = st.columns(3)
        for idx, p in enumerate(reversed(my_stuff)):
            with cols[idx % 3]:
                st.image(p["url"])
                if st.button("SET AS BG", key=f"bg_{idx}"):
                    st.session_state.app_bg = p["url"]; st.rerun()

else:
    st.error("REPLICATE_API_TOKEN Saknas!")

