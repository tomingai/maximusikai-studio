import streamlit as st
import replicate
import os
import time
import requests
import json
import os.path

# --- 0. DATABAS FÖR ANVÄNDARE ---
DB_FILE = "users.json"

def load_user_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"ANONYM": 10, "TOMAS2026": 999}, f)
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {"ANONYM": 10}

def save_user_db(db):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(db, f, indent=4)
    except:
        pass

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = load_user_db()
if "app_bg" not in st.session_state: st.session_state.app_bg = "https://images.unsplash.com"
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. DESIGN (FUTURISTIC TRANSPARENT) ---
def apply_design():
    bg_url = st.session_state.app_bg
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com');
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url("{bg_url}") !important;
            background-size: cover !important; background-attachment: fixed !important;
        }}
        .logo-text {{
            font-family: 'Orbitron'; font-size: 3rem; font-weight: 900; color: #fff; text-align: center;
            text-transform: uppercase; letter-spacing: 5px; text-shadow: 0 0 20px #00d2ff; margin-bottom: 20px;
        }}
        /* NUCLEAR TRANSPARENCY */
        div[data-baseweb="base-input"], div[data-baseweb="textarea"], textarea, input, .stTextArea textarea {{
            background-color: rgba(255,255,255,0.01) !important;
            backdrop-filter: blur(15px) !important; color: white !important;
            border: 1px solid rgba(0, 210, 255, 0.4) !important; border-radius: 5px !important;
        }}
        label, p, h1, h2, h3, .stTabs [data-baseweb="tab"] {{
            color: white !important; font-family: 'Orbitron'; text-shadow: 2px 2px 8px #000;
        }}
        .stButton>button {{
            background: rgba(0, 210, 255, 0.1) !important; color: white !important;
            border: 1px solid #00d2ff !important; border-radius: 5px !important;
        }}
        </style>
        <div class="logo-text">⚡ MAXIMUSIKAI 2026 ⚡</div>
    """, unsafe_allow_html=True)

# --- 3. SPRÅK ---
texts = {
    "Svenska": {
        "title": "STUDIO", "tab_names": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "⚙️ ADMIN"],
        "units": "UNITS", "start_gen": "STARTA GENERERING", "prompt_label": "VISIONARY INPUT"
    },
    "English": {
        "title": "STUDIO", "tab_names": ["🪄 MAGIC", "🎬 DIRECTOR", "🎧 MUSIC", "📚 ARCHIVE", "⚙️ ADMIN"],
        "units": "UNITS", "start_gen": "START GENERATION", "prompt_label": "VISIONARY INPUT"
    },
    "Deutsch": {
        "title": "STUDIO", "tab_names": ["🪄 MAGIE", "🎬 REGIE", "🎧 MUSIK", "📚 ARCHIV", "⚙️ ADMIN"],
        "units": "EINHEITEN", "start_gen": "GENERIERUNG STARTEN", "prompt_label": "VISIONÄRE EINGABE"
    }
}
L = texts[st.session_state.lang]

# --- 4. SIDEBAR ---
with st.sidebar:
    st.session_state.lang = st.radio("Language:", ["Svenska", "English", "Deutsch"], horizontal=True)
    artist_id = st.text_input("ARTIST ID:", "ANONYM").upper()
    if artist_id not in st.session_state.user_db:
        st.session_state.user_db[artist_id] = 10
    
    st.metric(L["units"], st.session_state.user_db[artist_id])
    if st.button("❌ RESET BG"):
        st.session_state.app_bg = "https://images.unsplash.com"
        st.rerun()

# --- 5. MAIN APP ---
apply_design()

if not st.session_state.agreed:
    if st.button("GODKÄNN & ÖPPNA STUDION", use_container_width=True):
        st.session_state.agreed = True
        st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(L["tab_names"])

    with tabs[0]: # MAGI
        col1, col2 = st.columns(2)
        prompt = col1.text_area(L["prompt_label"], placeholder="Describe your vision...")
        aspect = col2.selectbox("Ratio", ["1:1", "16:9", "9:16"])
        if st.button(L["start_gen"], use_container_width=True):
            if st.session_state.user_db[artist_id] > 0:
                with st.status("AI Syncing..."):
                    img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": aspect})
                    img_url = str(img[0] if isinstance(img, list) else img)
                    st.session_state.gallery.append({"artist": artist_id, "url": img_url, "name": prompt})
                    st.session_state.user_db[artist_id] -= 1
                    save_user_db(st.session_state.user_db)
                    st.rerun()

    with tabs[1]: # REGI
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if my_imgs:
            sel = st.selectbox("Select Image", [p["name"][:30] for p in my_imgs])
            target = next(p for p in my_imgs if p["name"][:30] == sel)
            st.image(target["url"], width=500)
            if st.button("🎬 ANIMATE (5 UNITS)"):
                vid = replicate.run("luma-ai/luma-dream-machine", input={"image_url": target["url"]})
                st.video(str(vid))
        else: st.info("Create magic first.")

    with tabs[3]: # ARKIV
        my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        cols = st.columns(3)
        for idx, p in enumerate(reversed(my_stuff)):
            with cols[idx % 3]:
                st.image(p["url"])
                if st.button("SET BG", key=f"bg_{idx}"):
                    st.session_state.app_bg = p["url"]
                    st.rerun()

    if artist_id == "TOMAS2026":
        with tabs[4]: # ADMIN
            st.write(st.session_state.user_db)
            if st.button("PURGE GALLERY"):
                st.session_state.gallery = []
                st.rerun()
else:
    st.error("MISSING API TOKEN")


