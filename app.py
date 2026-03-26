import streamlit as st
import replicate
import os
import time
from datetime import datetime

# --- 1. SETUP & SESSION STATE ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

# START-BILD: En extremt futuristisk sci-fi miljö
START_BG = "https://images.unsplash.com"

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {"ANONYM": 10, "TOMAS2026": 999}
if "app_bg" not in st.session_state: st.session_state.app_bg = START_BG
if "agreed" not in st.session_state: st.session_state.agreed = False
if "lang" not in st.session_state: st.session_state.lang = "Svenska"
if "logs" not in st.session_state: st.session_state.logs = [f"[{datetime.now().strftime('%H:%M:%S')}] Core Online."]

def add_log(msg):
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    if len(st.session_state.logs) > 8: st.session_state.logs.pop(0)

# --- 2. THE FUTURISTIC GLASS ENGINE (CSS) ---
def apply_design():
    bg_url = st.session_state.app_bg
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com');

        /* TOTAL BACKGROUND SYNC */
        .stApp, [data-testid="stSidebar"], [data-testid="stHeader"] {{
            background: linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.3)), url("{bg_url}") !important;
            background-size: cover !important; background-attachment: fixed !important;
            background-position: center !important;
        }}

        /* HOLOGRAM OVERLAY EFFECT (Scannlines) */
        .stApp::before {{
            content: " ";
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 255, 255, 0.05) 50%), 
                        linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
            background-size: 100% 4px, 3px 100%;
            pointer-events: none; z-index: 100;
        }}

        /* TRANSPARENT INPUTS */
        div[data-baseweb="base-input"], textarea, input {{
            background-color: rgba(255, 255, 255, 0.02) !important;
            backdrop-filter: blur(15px) !important;
            color: #00f2ff !important;
            border: 1px solid rgba(0, 242, 255, 0.3) !important;
            font-family: 'Orbitron', sans-serif;
        }}

        /* PULSING TRANSPARENT BUTTONS */
        .stButton>button {{
            background: rgba(0, 0, 0, 0) !important;
            color: #00f2ff !important;
            border: 1px solid #00f2ff !important;
            backdrop-filter: blur(10px);
            font-family: 'Orbitron', sans-serif;
            text-transform: uppercase; letter-spacing: 2px;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background: rgba(0, 242, 255, 0.1) !important;
            box-shadow: 0 0 20px #00f2ff;
        }}

        /* LOGO */
        .logo-text {{
            font-family: 'Orbitron', sans-serif; font-size: 3.5rem !important; font-weight: 900 !important; 
            color: #fff !important; text-align: center; letter-spacing: 12px;
            text-shadow: 0 0 20px #00f2ff, 0 0 40px #00f2ff !important;
        }}

        /* LOG-BOX & CARDS */
        .card {{
            background: rgba(0, 0, 0, 0.2) !important;
            backdrop-filter: blur(20px);
            border-radius: 10px; padding: 20px;
            border: 1px solid rgba(0, 242, 255, 0.2);
        }}
        .log-box {{
            background: rgba(0,0,0,0.5); color: #00f2ff; font-family: monospace;
            padding: 8px; border-radius: 4px; font-size: 0.7rem; border-left: 3px solid #00f2ff;
        }}
        h1, h2, h3, p, label {{ color: white !important; font-family: 'Orbitron'; text-shadow: 2px 2px 8px #000; }}
        </style>
    """, unsafe_allow_html=True)

def get_url(res):
    try:
        if isinstance(res, list): return str(res[0])
        return str(res)
    except: return None

# --- 3. MISSION CONTROL (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🛰️ MISSION CONTROL</h2>", unsafe_allow_html=True)
    st.divider()

    with st.expander("👤 ARTIST DATA", expanded=True):
        artist_id = st.text_input("CALLSIGN:", "ANONYM").strip().upper()
        if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
        is_admin = (artist_id == "TOMAS2026")
        st.markdown(f"<h1 style='text-align:center; color:#00f2ff;'>{st.session_state.user_db[artist_id]}</h1>", unsafe_allow_html=True)

    with st.expander("🌍 ENV GEN (FUTURISTIC)", expanded=True):
        c1, c2 = st.columns(2)
        def gen_env(prompt):
            with st.spinner("Syncing..."):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"Ultra futuristic cinematic 8k, neon {prompt}"})
                st.session_state.app_bg = get_url(res)
                add_log(f"Env: {prompt} synced.")
                st.rerun()

        if c1.button("RYMDEN"): gen_env("deep space station nebula")
        if c2.button("SKOG"): gen_env("bioluminescent neon forest")
        if c1.button("HAV"): gen_env("futuristic underwater city ocean")
        if c2.button("STUDIO"): gen_env("high-tech music production console hologram")

    st.markdown("### 📝 LIVE LOG")
    log_html = "".join([f"<div>{l}</div>" for l in reversed(st.session_state.logs)])
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
        c1, c2 = st.columns()
        prompt = c1.text_area("VISIONARY INPUT", placeholder="Skapa framtiden...")
        aspect = c2.selectbox("RATIO", ["1:1", "16:9", "9:16"])
        if st.button("🔥 EXECUTE GENERATION", use_container_width=True):
            if is_admin or st.session_state.user_db[artist_id] > 0:
                with st.status("Synthesizing...") as s:
                    img = get_url(replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"Futuristic cinematic: {prompt}", "aspect_ratio": aspect}))
                    try: aud = str(replicate.run("facebookresearch/musicgen:7b76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": prompt, "duration": 8}))
                    except: aud = None
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt, "url": img, "audio": aud})
                    add_log(f"Gen: {prompt[:10]}..."); s.update(label="Complete", state="complete"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]: # REGI
        st.subheader("🎬 LUMA ENGINE")
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if my_imgs:
            sel = st.selectbox("SELECT FRAME", [p["name"][:50] for p in my_imgs])
            target = next(p for p in my_imgs if p["name"][:50] == sel)
            st.image(target["url"], width=500)
            if st.button("🎬 RENDER VIDEO (5 UNITS)"):
                with st.spinner("Processing..."):
                    vid = get_url(replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Futuristic cinematic motion", "image_url": target["url"]}))
                    st.video(vid); add_log("Video sync ready.")
        else: st.info("Skapa en bild först.")

    with tabs[2]: # MUSIK
        st.subheader("🎧 SONIC SYNTHESIS")
        m_in = st.text_input("STYLE/VIBE")
        if st.button("COMPOSE"):
            with st.spinner("Synthesizing..."):
                res = replicate.run("facebookresearch/musicgen:7b76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": m_in, "duration": 10})
                st.audio(str(res)); add_log(f"Audio: {m_in[:10]}")

    with tabs[3]: # ARKIV
        st.subheader("📚 NEURAL VAULT")
        my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        cols = st.columns(3)
        for idx, p in enumerate(reversed(my_stuff)):
            with cols[idx % 3]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image(p["url"])
                if st.button("SYNC TO UI", key=f"bg_{p['id']}"):
                    st.session_state.app_bg = p["url"]; add_log("UI Resynced."); st.rerun()
                if p["audio"]: st.audio(p["audio"])
                st.markdown('</div>', unsafe_allow_html=True)
else:
    st.error("Missing REPLICATE_API_TOKEN.")

