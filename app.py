import streamlit as st
import replicate
import os
import time
from datetime import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

for key, default in {
    "gallery": [], 
    "user_db": {"ANONYM": 10, "TOMAS2026": 999}, 
    "app_bg": "https://images.unsplash.com",
    "agreed": False, 
    "lang": "Svenska",
    "logs": [f"[{datetime.now().strftime('%H:%M:%S')}] System Ready."]
}.items():
    if key not in st.session_state: st.session_state[key] = default

def add_log(msg):
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    if len(st.session_state.logs) > 8: st.session_state.logs.pop(0)

# --- 2. DESIGN-MOTOR (TRANSPARENT GLASS UI) ---
def apply_design():
    bg_url = st.session_state.app_bg
    st.markdown(f"""
        <style>
        /* Huvudbakgrund & Sidomeny synk */
        .stApp, [data-testid="stSidebar"] {{
            background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url("{bg_url}") !important;
            background-size: cover !important; background-attachment: fixed !important;
            background-position: center !important;
        }}
        [data-testid="stSidebar"] {{ border-right: 1px solid rgba(255,255,255,0.1); }}

        /* TRANSPARENTA KNAPPAR */
        .stButton>button {{
            background: rgba(255, 255, 255, 0.05) !important;
            color: white !important;
            border: 1px solid rgba(0, 210, 255, 0.5) !important;
            border-radius: 10px !important;
            backdrop-filter: blur(5px) !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase;
            font-weight: 700 !important;
            letter-spacing: 1px;
        }}
        .stButton>button:hover {{
            background: rgba(0, 210, 255, 0.2) !important;
            border: 1px solid #00d2ff !important;
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
            transform: translateY(-2px);
        }}

        /* LOGO & TEXT */
        .logo-text {{
            font-size: 3rem !important; font-weight: 900 !important; color: #fff !important; text-align: center;
            text-transform: uppercase; letter-spacing: 6px;
            text-shadow: 0 0 20px #00d2ff !important; margin-bottom: 20px;
        }}
        
        /* KORT & INPUTS */
        .card {{
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(15px);
            border-radius: 20px; padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        div[data-baseweb="base-input"], textarea, input {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            color: white !important; border: 1px solid rgba(255,255,255,0.2) !important;
        }}
        .log-box {{
            background: rgba(0,0,0,0.5); color: #00ffcc; font-family: monospace;
            padding: 10px; border-radius: 8px; font-size: 0.7rem; border: 1px solid rgba(0,210,255,0.2);
        }}
        h1, h2, h3, p, label, span {{ color: white !important; text-shadow: 1px 1px 4px #000 !important; }}
        </style>
    """, unsafe_allow_html=True)

def get_url(res):
    try:
        if isinstance(res, list): return str(res[0])
        return str(res)
    except: return None

# --- 3. MISSION CONTROL (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🛰️ MISSION CONTROL")
    st.divider()

    with st.expander("👤 ARTIST CALLSIGN", expanded=True):
        artist_id = st.text_input("ID:", "ANONYM").strip().upper()
        if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
        is_admin = (artist_id == "TOMAS2026")
        st.markdown(f"<h1 style='text-align:center; color:#00d2ff; margin:0;'>{st.session_state.user_db[artist_id]}</h1>", unsafe_allow_html=True)
        st.caption("<p style='text-align:center;'>AVAILABLE UNITS</p>", unsafe_allow_html=True)

    with st.expander("🌍 MILJÖ (ATMOSPHERE)", expanded=True):
        c1, c2 = st.columns(2)
        if c1.button("RYMDEN"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Epic space nebula, stars, deep blue and violet, 4k"})
            st.session_state.app_bg = get_url(res); add_log("Env: Space activated."); st.rerun()
        if c2.button("SKOG"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Hyper-realistic ancient forest, sunbeams, misty atmosphere, 4k"})
            st.session_state.app_bg = get_url(res); add_log("Env: Forest activated."); st.rerun()
        if c1.button("HAV"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Vibrant ocean horizon, sunset light, crystal clear water, 4k"})
            st.session_state.app_bg = get_url(res); add_log("Env: Ocean activated."); st.rerun()
        if c2.button("STUDIO"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Futuristic music studio console, glowing neon faders, 4k"})
            st.session_state.app_bg = get_url(res); add_log("Env: Console activated."); st.rerun()

    st.markdown("### 📝 LIVE LOG")
    log_html = "".join([f"<div>{l}</div>" for l in reversed(st.session_state.logs)])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
apply_design()
st.markdown('<div class="logo-text">⚡ MAXIMUSIKAI ⚡</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("INITIALIZE STUDIO INTERFACE", use_container_width=True): 
        st.session_state.agreed = True; add_log("Interface Sync Complete."); st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "⚙️ ADMIN"] if is_admin else ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV"])

    with tabs[0]: # MAGI
        st.markdown('<div class="card">', unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        prompt = c1.text_area("VISIONARY INPUT", placeholder="Vad vill du skapa idag?")
        aspect = c2.selectbox("RATIO", ["1:1", "16:9", "9:16"])
        if st.button("🔥 GENERATE ALL ASSETS", use_container_width=True):
            if is_admin or st.session_state.user_db[artist_id] > 0:
                with st.status("Synthesizing...") as s:
                    img = get_url(replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": aspect}))
                    try:
                        aud = str(replicate.run("facebookresearch/musicgen:7b76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": prompt, "duration": 8}))
                    except: aud = None
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt, "url": img, "audio": aud})
                    add_log(f"Generated: {prompt[:15]}..."); s.update(label="Ready!", state="complete"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]: # REGI
        st.subheader("🎬 VIDEO SYNTHESIS")
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if my_imgs:
            sel = st.selectbox("SOURCE IMAGE", [p["name"][:50] for p in my_imgs])
            target = next(p for p in my_imgs if p["name"][:50] == sel)
            st.image(target["url"], width=400)
            if st.button("🎬 RENDER VIDEO"):
                if is_admin or st.session_state.user_db[artist_id] >= 5:
                    with st.spinner("Processing Video..."):
                        vid = get_url(replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic movement", "image_url": target["url"]}))
                        st.video(vid); add_log("Video Rendered."); st.rerun()
        else: st.info("Skapa en bild i MAGI först.")

    with tabs[2]: # MUSIK
        st.subheader("🎧 BEAT STATION")
        m_in = st.text_input("GENRE / MOOD")
        if st.button("CREATE AUDIO"):
            with st.spinner("Composing..."):
                res = replicate.run("facebookresearch/musicgen:7b76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": m_in, "duration": 10})
                st.audio(str(res)); add_log(f"Audio: {m_in[:15]}")

    with tabs[3]: # ARKIV
        st.subheader("📚 STUDIO ARCHIVE")
        my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        cols = st.columns(3)
        for idx, p in enumerate(reversed(my_stuff)):
            with cols[idx % 3]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image(p["url"])
                if st.button("SET AS UI BG", key=f"bg_{p['id']}"):
                    st.session_state.app_bg = p["url"]; add_log("UI Sync: New Background."); st.rerun()
                if p["audio"]: st.audio(p["audio"])
                st.markdown('</div>', unsafe_allow_html=True)

    if is_admin and len(tabs) > 4:
        with tabs[4]:
            st.write(st.session_state.user_db)
            if st.button("SYSTEM PURGE"): st.session_state.gallery = []; st.rerun()
else:
    st.error("Lägg in REPLICATE_API_TOKEN i Secrets!")
