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

# --- 2. TOTAL TRANSPARENCY ENGINE (FORCED CSS) ---
def apply_design():
    bg_url = st.session_state.app_bg
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com');

        /* 1. GRUNDEN & SIDOMENY */
        .stApp, [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"] {{
            background: linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.3)), url("{bg_url}") !important;
            background-size: cover !important; background-attachment: fixed !important;
            background-position: center !important;
        }}

        /* 2. TVINGA ALLA CONTAINERS ATT BLI GENOMSKINLIGA */
        [data-testid="stVerticalBlock"], [data-testid="stExpander"], .stTabs, [data-testid="stHorizontalBlock"] {{
            background-color: transparent !important;
        }}

        /* 3. INPUT-FÄLT & DROPDOWNS (DENNA FIXAR DE GRÅA RUTORNA) */
        div[data-baseweb="base-input"], div[data-baseweb="select"], div[role="combobox"], 
        .stTextArea textarea, .stTextInput input, .stSelectbox div, .stNumberInput input {{
            background-color: rgba(255, 255, 255, 0.0) !important; /* Helt nollad bakgrund */
            backdrop-filter: blur(20px) !important;
            color: #00f2ff !important;
            border: 1px solid rgba(0, 242, 255, 0.5) !important;
            border-radius: 0px !important;
            font-family: 'Orbitron', sans-serif;
        }}

        /* 4. FLIKAR (TABS) - TOTAL CLEANUP */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: transparent !important;
            border: none !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(0,0,0,0.2) !important;
            border: 1px solid rgba(0, 242, 255, 0.2) !important;
            margin-right: 5px;
            color: white !important;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: rgba(0, 242, 255, 0.2) !important;
            border: 1px solid #00f2ff !important;
        }}

        /* 5. KNAPPAR */
        .stButton>button {{
            background: rgba(0, 0, 0, 0) !important;
            color: #00f2ff !important;
            border: 1px solid #00f2ff !important;
            backdrop-filter: blur(10px);
            font-family: 'Orbitron';
            text-transform: uppercase;
            width: 100%;
        }}
        .stButton>button:hover {{
            background: rgba(0, 242, 255, 0.2) !important;
            box-shadow: 0 0 20px #00f2ff;
        }}

        /* 6. KORT & BOXAR */
        .card {{
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(30px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            padding: 20px;
            margin-bottom: 10px;
        }}
        
        .log-box {{
            background: rgba(0,0,0,0.5);
            color: #00f2ff;
            font-family: monospace;
            padding: 10px;
            border-left: 2px solid #00f2ff;
        }}

        /* ALL TEXT */
        h1, h2, h3, p, label, span {{ 
            color: white !important; 
            font-family: 'Orbitron'; 
            text-shadow: 2px 2px 10px #000;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. MISSION CONTROL ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🛰️ MISSION CONTROL</h2>", unsafe_allow_html=True)
    artist_id = st.text_input("CALLSIGN:", "ANONYM").strip().upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    is_admin = (artist_id == "TOMAS2026")
    st.markdown(f"<h1 style='text-align:center; color:#00f2ff;'>{st.session_state.user_db[artist_id]}</h1>", unsafe_allow_html=True)
    
    if st.button("🚀 SYNC SPACE CORE"):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Deep space nebula 8k"})
        st.session_state.app_bg = str(res[0] if isinstance(res, list) else res)
        st.rerun()

    st.markdown("### 📝 LIVE LOG")
    log_html = "".join([f"<div>{l}</div>" for l in reversed(st.session_state.logs)])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
apply_design()
st.markdown('<div class="logo-text" style="text-align:center; font-family:Orbitron; font-size:3.5rem; letter-spacing:10px; text-shadow:0 0 20px #00f2ff;">MAXIMUSIKAI</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("INITIALIZE NEURAL LINK", use_container_width=True): 
        st.session_state.agreed = True; st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "📚 ARKIV"])

    with tabs[0]: # MAGI
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        prompt = col1.text_area("VISIONARY INPUT")
        aspect = col2.selectbox("RATIO", ["1:1", "16:9", "9:16"])
        if st.button("🔥 EXECUTE GENERATION"):
            with st.status("Synthesizing..."):
                img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"Space: {prompt}", "aspect_ratio": aspect})
                img_url = str(img[0] if isinstance(img, list) else img)
                st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt, "url": img_url})
                if not is_admin: st.session_state.user_db[artist_id] -= 1
                add_log(f"Gen: {prompt[:10]}..."); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]: # REGI
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if my_imgs:
            sel = st.selectbox("SOURCE", [p["name"][:50] for p in my_imgs])
            target = next(p for p in my_imgs if p["name"][:50] == sel)
            st.image(target["url"], width=600)
            if st.button("🎬 RENDER VIDEO"):
                vid = replicate.run("luma-ai/luma-dream-machine", input={"image_url": target["url"]})
                st.video(str(vid))
        else: st.info("Skapa en bild först.")

    with tabs[2]: # ARKIV
        my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        cols = st.columns(3)
        for idx, p in enumerate(reversed(my_stuff)):
            with cols[idx % 3]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image(p["url"])
                if st.button("SYNC TO UI", key=f"bg_{p['id']}"):
                    st.session_state.app_bg = p["url"]; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)



