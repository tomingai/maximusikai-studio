import streamlit as st
import replicate
import os
import time
from datetime import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

SPACE_BG = "https://images.unsplash.com"

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {"ANONYM": 10, "TOMAS2026": 999}
if "app_bg" not in st.session_state: st.session_state.app_bg = SPACE_BG
if "agreed" not in st.session_state: st.session_state.agreed = False
if "logs" not in st.session_state: st.session_state.logs = [f"[{datetime.now().strftime('%H:%M:%S')}] Neural Link Active."]

def add_log(msg):
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    if len(st.session_state.logs) > 10: st.session_state.logs.pop(0)

# --- 2. TOTAL TRANSPARENCY ENGINE (CSS) ---
def apply_design():
    bg_url = st.session_state.app_bg
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com');

        /* Bakgrundssynk för hela cockpit */
        .stApp, [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"] {{
            background: linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.3)), url("{bg_url}") !important;
            background-size: cover !important; background-attachment: fixed !important;
            background-position: center !important;
        }}

        /* GÖR ALLA FÄLT TOTALT TRANSPARENTA */
        div[data-baseweb="base-input"], div[data-baseweb="select"], div[data-baseweb="popover"], 
        .stTextArea textarea, .stTextInput input, .stSelectbox div, .stNumberInput input, 
        div[role="listbox"], .stMultiSelect div {{
            background-color: rgba(255, 255, 255, 0.01) !important;
            backdrop-filter: blur(20px) !important;
            color: #00f2ff !important;
            border: 1px solid rgba(0, 242, 255, 0.4) !important;
            border-radius: 0px !important; /* Rakare, mer teknisk look */
            font-family: 'Orbitron', sans-serif;
        }}

        /* KNAPPAR - ENBART RAM & TEXT */
        .stButton>button {{
            background: rgba(0, 0, 0, 0) !important;
            color: #00f2ff !important;
            border: 1px solid #00f2ff !important;
            border-radius: 0px !important;
            backdrop-filter: blur(10px);
            font-family: 'Orbitron', sans-serif;
            text-transform: uppercase; letter-spacing: 2px;
            transition: 0.4s;
            width: 100%;
        }}
        .stButton>button:hover {{
            background: rgba(0, 242, 255, 0.15) !important;
            box-shadow: 0 0 25px rgba(0, 242, 255, 0.5);
            color: white !important;
        }}

        /* FLIKAR (TABS) - TRANSPARENTA */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0,0,0,0) !important;
            border-bottom: 1px solid rgba(0, 242, 255, 0.3);
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: transparent !important;
            color: white !important;
            font-family: 'Orbitron';
        }}
        .stTabs [aria-selected="true"] {{
            border-bottom: 2px solid #00f2ff !important;
            background-color: rgba(0, 242, 255, 0.1) !important;
        }}

        /* LOGO */
        .logo-text {{
            font-family: 'Orbitron', sans-serif; font-size: 3.5rem; font-weight: 900; 
            color: #fff; text-align: center; letter-spacing: 12px;
            text-shadow: 0 0 30px #00f2ff; margin-bottom: 25px;
        }}

        /* CONTAINERS & CARDS */
        .card, .stExpander {{
            background: rgba(0, 0, 0, 0.1) !important;
            backdrop-filter: blur(25px);
            border: 1px solid rgba(0, 242, 255, 0.2) !important;
            border-radius: 0px;
        }}
        
        .log-box {{
            background: rgba(0,0,0,0.4); color: #00f2ff; font-family: monospace;
            padding: 10px; font-size: 0.75rem; border-left: 2px solid #00f2ff;
        }}

        /* TEXTKONTRAST */
        h1, h2, h3, p, label, span {{ 
            color: white !important; 
            font-family: 'Orbitron'; 
            text-shadow: 2px 2px 10px #000;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. MISSION CONTROL (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🛰️ MISSION CONTROL</h2>", unsafe_allow_html=True)
    st.divider()

    artist_id = st.text_input("CALLSIGN:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    is_admin = (artist_id == "TOMAS2026")
    
    st.markdown(f"<h1 style='text-align:center; color:#00f2ff;'>{st.session_state.user_db[artist_id]}</h1>", unsafe_allow_html=True)
    st.caption("<p style='text-align:center; color:white;'>UNITS REMAINING</p>", unsafe_allow_html=True)

    st.divider()
    if st.button("🚀 SYNC SPACE CORE"):
        with st.spinner("Processing Nebula..."):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Deep space nebula, sci-fi starfield, 8k"})
            st.session_state.app_bg = str(res[0] if isinstance(res, list) else res)
            add_log("Core Sync: 100%"); st.rerun()

    st.markdown("### 📝 LIVE LOG")
    log_html = "".join([f"<div style='margin-bottom:4px;'>{l}</div>" for l in reversed(st.session_state.logs)])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
apply_design()
st.markdown('<div class="logo-text">MAXIMUSIKAI</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("INITIALIZE NEURAL LINK", use_container_width=True): 
        st.session_state.agreed = True; add_log("Neural link active."); st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "⚙️ ADMIN"] if is_admin else ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV"])

    with tabs[0]: # MAGI
        st.markdown('<div class="card" style="padding:20px;">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        prompt = col1.text_area("VISIONARY INPUT", placeholder="Beskriv rymdens framtid...")
        aspect = col2.selectbox("RATIO", ["1:1", "16:9", "9:16"])
        if st.button("🔥 EXECUTE GENERATION", use_container_width=True):
            if is_admin or st.session_state.user_db[artist_id] > 0:
                with st.status("Synthesizing..."):
                    img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"Futuristic space: {prompt}", "aspect_ratio": aspect})
                    img_url = str(img[0] if isinstance(img, list) else img)
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt, "url": img_url})
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    add_log(f"Gen: {prompt[:10]}..."); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]: # REGI
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if my_imgs:
            sel = st.selectbox("SELECT SOURCE", [p["name"][:50] for p in my_imgs])
            target = next(p for p in my_imgs if p["name"][:50] == sel)
            st.image(target["url"], width=700)
            if st.button("🎬 RENDER VIDEO (5 UNITS)"):
                with st.spinner("Luma Processing..."):
                    vid = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic space motion", "image_url": target["url"]})
                    st.video(str(vid)); add_log("Video sync ready.")
        else: st.info("Skapa en bild först.")

    with tabs[3]: # ARKIV (Index 3 eftersom flikarna räknas från 0)
        my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        cols = st.columns(3)
        for idx, p in enumerate(reversed(my_stuff)):
            with cols[idx % 3]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image(p["url"])
                if st.button("SYNC TO UI", key=f"bg_{p['id']}"):
                    st.session_state.app_bg = p["url"]; add_log("UI Sync: New Background."); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("Missing REPLICATE_API_TOKEN.")


