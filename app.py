import streamlit as st
import replicate
import os
import time
import requests
from datetime import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

# Initialisering av alla variabler
for key, default in {
    "gallery": [], 
    "user_db": {"ANONYM": 10, "TOMAS2026": 999}, 
    "app_bg": "https://images.unsplash.com",
    "agreed": False, 
    "lang": "Svenska",
    "logs": [f"[{datetime.now().strftime('%H:%M:%S')}] System Initialized."]
}.items():
    if key not in st.session_state: st.session_state[key] = default

def add_log(msg):
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    if len(st.session_state.logs) > 10: st.session_state.logs.pop(0)

# --- 2. DESIGN-MOTOR (MISSION CONTROL THEME) ---
def apply_design():
    bg_url = st.session_state.app_bg
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url("{bg_url}") !important;
            background-size: cover !important; background-attachment: fixed !important;
        }}
        .logo-text {{
            font-size: 3rem !important; font-weight: 900 !important; color: #fff !important; text-align: center;
            text-transform: uppercase; letter-spacing: 4px;
            text-shadow: 0 0 15px #00d2ff, 2px 2px 5px #000 !important;
        }}
        .card {{
            background: rgba(0,0,0,0.5) !important; backdrop-filter: blur(15px);
            border-radius: 15px; padding: 15px; border: 1px solid #00d2ff;
        }}
        .log-box {{
            background: #000; color: #00ff00; font-family: 'Courier New', monospace;
            padding: 10px; border-radius: 5px; font-size: 0.75rem; border: 1px solid #333;
        }}
        p, label, h1, h2, h3, .stTabs [data-baseweb="tab"] {{ 
            color: white !important; text-shadow: 1px 1px 3px #000 !important; 
        }}
        </style>
    """, unsafe_allow_html=True)

def get_url(res):
    try:
        if isinstance(res, list): return str(res[0])
        if hasattr(res, "url"): return str(res.url)
        return str(res)
    except: return None

# --- 3. MISSION CONTROL (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🛰️ MISSION CONTROL")
    st.divider()

    # PROFIL
    with st.expander("👤 ARTIST CALLSIGN", expanded=True):
        st.session_state.lang = st.radio("LANG", ["Svenska", "English"], horizontal=True)
        artist_id = st.text_input("ID:", "ANONYM").strip().upper()
        if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
        is_admin = (artist_id == "TOMAS2026")
        
        st.markdown(f"""
            <div style="background: rgba(0,210,255,0.1); padding: 10px; border-radius: 10px; border: 1px solid #00d2ff; text-align: center;">
                <p style="margin:0; font-size: 1.2rem; color: #00d2ff; font-weight: bold;">⚡ {st.session_state.user_db[artist_id]} UNITS</p>
            </div>
        """, unsafe_allow_html=True)

    # ATMOSFÄR
    with st.expander("🌍 ENVIRONMENT CONTROL", expanded=False):
        c1, c2 = st.columns(2)
        themes = {
            "CYBER": "Bright neon cyberpunk city, cyan and purple, 4k",
            "DRÖM": "Golden hour dreamscape, bright clouds, 4k",
            "LYX": "White luxury marble studio, gold accents, daylight, 4k",
            "FÄRG": "Abstract vibrant color explosion, white background, 4k"
        }
        if c1.button("CYBER"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": themes["CYBER"]})
            st.session_state.app_bg = get_url(res); add_log("Environment: CYBER set."); st.rerun()
        if c2.button("DRÖM"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": themes["DRÖM"]})
            st.session_state.app_bg = get_url(res); add_log("Environment: DREAM set."); st.rerun()
        if c1.button("LYX"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": themes["LYX"]})
            st.session_state.app_bg = get_url(res); add_log("Environment: LUXURY set."); st.rerun()
        if c2.button("FÄRG"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": themes["FÄRG"]})
            st.session_state.app_bg = get_url(res); add_log("Environment: COLOR set."); st.rerun()

    # AUDIO & STATUS
    with st.expander("📊 SYSTEM STATUS", expanded=True):
        st.slider("MASTER OUTPUT", 0, 100, 80)
        st.write(f"CORE: {'💎 ADMIN' if is_admin else '📡 ACTIVE'}")
        st.write("NET: 🔵 OPTIMAL")
    
    # LIVE LOG
    st.markdown("### 📝 LIVE LOG")
    log_html = "".join([f"<div>{l}</div>" for l in reversed(st.session_state.logs)])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

# --- 4. HUVUDAPP ---
apply_design()
L = {"Svenska": ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "⚙️ ADMIN"], 
     "English": ["🪄 MAGIC", "🎬 DIRECTOR", "🎧 MUSIC", "📚 ARCHIVE", "⚙️ ADMIN"]}[st.session_state.lang]

st.markdown(f'<div class="logo-text">⚡ MAXIMUSIKAI STUDIO ⚡</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("INITIALIZE STUDIO", use_container_width=True): 
        st.session_state.agreed = True; add_log("User Access Granted."); st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(L if is_admin else L[:-1])

    # MAGI
    with tabs[0]:
        c1, c2 = st.columns([2,1])
        prompt = c1.text_area("VISION", placeholder="Beskriv vad AI:n ska skapa...")
        aspect = c2.selectbox("RATIO", ["1:1", "16:9", "9:16"])
        if st.button("🔥 EXECUTE GENERATION", use_container_width=True):
            if is_admin or st.session_state.user_db[artist_id] > 0:
                with st.status("Processing AI Layers...") as s:
                    img = get_url(replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": aspect}))
                    try: 
                        aud = str(replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": prompt, "duration": 8}))
                    except: aud = None
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt, "url": img, "audio": aud})
                    add_log(f"Generated: {prompt[:20]}...")
                    s.update(label="COMPLETED", state="complete")
                    st.rerun()

    # REGI
    with tabs[1]:
        st.subheader("🎬 VIDEO SYNTHESIS")
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if my_imgs:
            sel = st.selectbox("SELECT SOURCE", [p["name"][:50] for p in my_imgs])
            target = next(p for p in my_imgs if p["name"][:50] == sel)
            st.image(target["url"], width=300)
            if st.button("🎬 RENDER VIDEO (5 UNITS)"):
                if is_admin or st.session_state.user_db[artist_id] >= 5:
                    with st.spinner("Luma Engine Active..."):
                        vid = get_url(replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic movement", "image_url": target["url"]}))
                        st.video(vid); add_log("Video Rendered.")
                        if not is_admin: st.session_state.user_db[artist_id] -= 5
                else: st.error("Low Units.")

    # MUSIK
    with tabs[2]:
        st.subheader("🎧 AUDIO ENGINE")
        m_in = st.text_input("BEAT DESCRIPTION")
        if st.button("COMPOSE"):
            with st.spinner("Synthesizing..."):
                res = replicate.run("facebookresearch/musicgen:7a76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": m_in, "duration": 10})
                st.audio(str(res)); add_log(f"Audio Created: {m_in[:15]}")

    # ARKIV
    with tabs[3]:
        st.subheader("📚 STUDIO ARCHIVE")
        my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        cols = st.columns(3)
        for idx, p in enumerate(reversed(my_stuff)):
            with cols[idx % 3]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image(p["url"])
                if st.button("SET AS BG", key=f"bg_{p['id']}"):
                    st.session_state.app_bg = p["url"]; add_log("Background updated."); st.rerun()
                if p["audio"]: st.audio(p["audio"])
                st.markdown('</div>', unsafe_allow_html=True)

    # ADMIN
    if is_admin:
        with tabs[4]:
            st.write("USER DATABASE", st.session_state.user_db)
            if st.button("WIPE ALL DATA"):
                st.session_state.gallery = []; add_log("WIPE COMMAND EXECUTED."); st.rerun()
else:
    st.error("MISSING REPLICATE_API_TOKEN IN SECRETS.")
