import streamlit as st
import replicate
import os
import time
from datetime import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

# Fastställd futuristisk rymdbakgrund
SPACE_BG = "https://images.unsplash.com"

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {"ANONYM": 10, "TOMAS2026": 999}
if "app_bg" not in st.session_state: st.session_state.app_bg = SPACE_BG
if "agreed" not in st.session_state: st.session_state.agreed = False
if "logs" not in st.session_state: st.session_state.logs = [f"[{datetime.now().strftime('%H:%M:%S')}] Space Engine Active."]

def add_log(msg):
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    if len(st.session_state.logs) > 10: st.session_state.logs.pop(0)

# --- 2. DESIGN-MOTOR (TOTAL TRANSPARENCY & SPACE SYNC) ---
def apply_design():
    bg_url = st.session_state.app_bg
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com');

        .stApp, [data-testid="stSidebar"], [data-testid="stHeader"] {{
            background: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.4)), url("{bg_url}") !important;
            background-size: cover !important; background-attachment: fixed !important;
            background-position: center !important;
        }}

        /* Holografisk scanline-effekt */
        .stApp::before {{
            content: " "; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 255, 255, 0.03) 50%);
            background-size: 100% 4px; pointer-events: none; z-index: 100;
        }}

        div[data-baseweb="base-input"], textarea, input {{
            background-color: rgba(255, 255, 255, 0.02) !important;
            backdrop-filter: blur(15px) !important; color: #00f2ff !important;
            border: 1px solid rgba(0, 242, 255, 0.3) !important; font-family: 'Orbitron';
        }}

        .stButton>button {{
            background: rgba(0, 0, 0, 0) !important; color: #00f2ff !important;
            border: 1px solid #00f2ff !important; backdrop-filter: blur(10px);
            font-family: 'Orbitron'; text-transform: uppercase; transition: 0.3s;
            width: 100%;
        }}

        .stButton>button:hover {{
            background: rgba(0, 242, 255, 0.1) !important;
            box-shadow: 0 0 20px #00f2ff;
        }}

        .logo-text {{
            font-family: 'Orbitron'; font-size: 3.5rem; font-weight: 900; 
            color: #fff; text-align: center; letter-spacing: 12px;
            text-shadow: 0 0 25px #00f2ff; margin-bottom: 20px;
        }}

        .card {{
            background: rgba(0, 0, 0, 0.3) !important; backdrop-filter: blur(20px);
            border-radius: 10px; padding: 20px; border: 1px solid rgba(0, 242, 255, 0.2);
        }}

        .log-box {{
            background: rgba(0,0,0,0.5); color: #00f2ff; font-family: monospace;
            padding: 8px; border-radius: 4px; font-size: 0.7rem; border-left: 3px solid #00f2ff;
        }}

        h1, h2, h3, p, label {{ color: white !important; font-family: 'Orbitron'; text-shadow: 2px 2px 10px #000; }}
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
    st.caption("<p style='text-align:center; color:white;'>NEURAL UNITS AVAILABLE</p>", unsafe_allow_html=True)

    st.divider()
    if st.button("🚀 SYNC SPACE CORE"):
        # Genererar en ny, unik rymdbild om man vill uppdatera rymdtemat
        with st.spinner("Re-syncing with Nebula..."):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Deep space nebula, cinematic starfield, futuristic 8k"})
            st.session_state.app_bg = str(res[0] if isinstance(res, list) else res)
            add_log("Space Core Re-synced."); st.rerun()

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
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
                    add_log(f"New Asset: {prompt[:10]}..."); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]: # REGI
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if my_imgs:
            sel = st.selectbox("SELECT FRAME", [p["name"][:50] for p in my_imgs])
            target = next(p for p in my_imgs if p["name"][:50] == sel)
            st.image(target["url"], width=600)
            if st.button("🎬 RENDER VIDEO (5 UNITS)"):
                with st.spinner("Processing..."):
                    vid = replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic space motion", "image_url": target["url"]})
                    st.video(str(vid)); add_log("Video sync ready.")
        else: st.info("Använd MAGI-fliken för att skapa en bild först.")

    with tabs[2]: # MUSIK
        st.subheader("🎧 SONIC SYNTHESIS")
        m_in = st.text_input("SPACE VIBE (ex: Ambient Starship)")
        if st.button("COMPOSE AUDIO"):
            with st.spinner("Calculating..."):
                res = replicate.run("facebookresearch/musicgen:7b76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": m_in, "duration": 10})
                st.audio(str(res)); add_log(f"Audio: {m_in[:10]}")

    with tabs[3]: # ARKIV
        my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        cols = st.columns(3)
        for idx, p in enumerate(reversed(my_stuff)):
            with cols[idx % 3]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image(p["url"])
                if st.button("SYNC TO UI", key=f"bg_{p['id']}"):
                    st.session_state.app_bg = p["url"]; add_log("UI Background Updated."); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    if is_admin and len(tabs) > 4:
        with tabs[4]:
            st.write(st.session_state.user_db)
            if st.button("SYSTEM PURGE"): st.session_state.gallery = []; add_log("Wipe complete."); st.rerun()
else:
    st.error("Missing REPLICATE_API_TOKEN in Secrets.")

