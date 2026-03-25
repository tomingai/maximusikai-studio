import streamlit as st
import replicate
import os
import time
import json
import os.path

# --- 0. DATABAS-HANTERING ---
DB_FILE = "users.json"

def load_user_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_user_db():
    with open(DB_FILE, "w") as f:
        json.dump(st.session_state.user_db, f, indent=4)

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = load_user_db()
if "app_bg" not in st.session_state: st.session_state.app_bg = None
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"

# --- 2. DESIGN ---
def apply_design():
    if st.session_state.app_bg:
        bg_url = str(st.session_state.app_bg)
        st.markdown(f"""
            <style>
            .stApp {{
                background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url("{bg_url}") !important;
                background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
            }}
            .logo-text {{
                font-size: 3rem; font-weight: 900; color: #fff; text-align: center;
                text-transform: uppercase; letter-spacing: 5px;
                text-shadow: 0 0 15px #00d2ff; margin-bottom: 20px;
            }}
            div[data-baseweb="base-input"], textarea {{
                background-color: rgba(255,255,255,0.1) !important; color: white !important;
                backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2) !important;
            }}
            label, p, h1, h2, h3 {{ color: white !important; text-shadow: 2px 2px 4px #000; }}
            </style>
        """, unsafe_allow_html=True)

def get_url(res):
    if isinstance(res, list): return str(res[0])
    return str(res.url) if hasattr(res, 'url') else str(res)

# --- 3. SPRÅK ---
texts = {
    "Svenska": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "⚙️ ADMIN"],
        "units": "UNITS", "status": "STATUS", "atm": "ATMOSFÄR"
    },
    "English": {
        "title": "MAXIMUSIKAI STUDIO",
        "tab_names": ["🪄 MAGIC", "🎬 DIRECTOR", "🎧 MUSIC", "📚 ARCHIVE", "⚙️ ADMIN"],
        "units": "UNITS", "status": "STATUS", "atm": "ATMOSPHERE"
    }
}
L = texts.get(st.session_state.lang, texts["Svenska"])

# --- 4. SIDOMENY ---
with st.sidebar:
    st.title("⚡ STUDIO")
    st.session_state.lang = st.radio("Language:", ["Svenska", "English"], horizontal=True)
    artist_id = st.text_input("ARTIST ID:", "ANONYM").strip().upper()
    
    if artist_id not in st.session_state.user_db:
        st.session_state.user_db[artist_id] = 10
        save_user_db()
    
    u_creds = st.session_state.user_db[artist_id]
    st.info(f"{L['status']}: {u_creds} {L['units']}")
    
    st.divider()
    if st.button("❌ NOLLSTÄLL DESIGN"):
        st.session_state.app_bg = None
        st.rerun()

# --- 5. HUVUDAPP ---
apply_design()
st.markdown(f'<div class="logo-text">⚡ {L["title"]} ⚡</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("ÖPPNA STUDION", use_container_width=True):
        st.session_state.agreed = True
        st.rerun()
    st.stop()

# API Init
token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(L["tab_names"])

    with tabs[0]: # MAGI
        prompt = st.text_area("VAD SKALL VI SKAPA?")
        if st.button("STARTA GENERERING", use_container_width=True):
            if u_creds > 0:
                with st.status("AI arbetar..."):
                    st.session_state.user_db[artist_id] -= 1
                    save_user_db()
                    img_url = get_url(replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt}))
                    st.session_state.gallery.append({"artist": artist_id, "name": prompt[:20], "url": img_url})
                    st.session_state.app_bg = img_url
                    st.rerun()

    with tabs[1]: # REGI
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if my_imgs:
            selected = st.selectbox("Välj bild:", [p["name"] for p in my_imgs])
            img_url = next(p["url"] for p in my_imgs if p["name"] == selected)
            if st.button("SKAPA VIDEO (5 UNITS)"):
                if u_creds >= 5:
                    with st.spinner("Luma renderar..."):
                        st.session_state.user_db[artist_id] -= 5
                        save_user_db()
                        vid = replicate.run("luma-ai/luma-dream-machine", input={"image_url": img_url})
                        st.video(get_url(vid))
        else: st.info("Skapa en bild först!")

    with tabs[3]: # ARKIV
        for p in reversed([p for p in st.session_state.gallery if p["artist"] == artist_id]):
            st.image(p["url"], caption=p["name"])
            st.divider()
else:
    st.error("API TOKEN SAKNAS")


        "













































































































































































































































































