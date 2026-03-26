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
    "app_bg": "https://images.unsplash.com", # Rymden start
    "agreed": False, 
    "lang": "Svenska",
    "logs": [f"[{datetime.now().strftime('%H:%M:%S')}] System Online."]
}.items():
    if key not in st.session_state: st.session_state[key] = default

def add_log(msg):
    st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    if len(st.session_state.logs) > 8: st.session_state.logs.pop(0)

# --- 2. DESIGN-MOTOR (SYNCHRONIZED BACKGROUND) ---
def apply_design():
    bg_url = st.session_state.app_bg
    st.markdown(f"""
        <style>
        /* Huvudbakgrund */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url("{bg_url}") !important;
            background-size: cover !important; background-attachment: fixed !important;
            background-position: center !important;
        }}
        /* Sidomeny bakgrund (Samma som huvudfönstret) */
        [data-testid="stSidebar"] {{
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url("{bg_url}") !important;
            background-size: cover !important; background-attachment: fixed !important;
            background-position: left center !important;
            border-right: 1px solid rgba(255,255,255,0.1);
        }}
        .logo-text {{
            font-size: 2.8rem !important; font-weight: 900 !important; color: #fff !important; text-align: center;
            text-transform: uppercase; letter-spacing: 4px;
            text-shadow: 0 0 20px #00d2ff, 2px 2px 5px #000 !important;
            margin-bottom: 20px;
        }}
        .stTabs [data-baseweb="tab-list"] {{ background-color: rgba(0,0,0,0.6) !important; border-radius: 15px; padding: 5px; }}
        .card {{
            background: rgba(0,0,0,0.5) !important; backdrop-filter: blur(10px);
            border-radius: 15px; padding: 15px; border: 1px solid rgba(0,210,255,0.3);
        }}
        .log-box {{
            background: rgba(0,0,0,0.8); color: #00ffcc; font-family: 'Courier New', monospace;
            padding: 10px; border-radius: 8px; font-size: 0.7rem; border: 1px solid #00d2ff;
        }}
        h1, h2, h3, p, label, span {{ color: white !important; text-shadow: 1px 1px 3px #000 !important; }}
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

    with st.expander("👤 ARTIST ID", expanded=True):
        artist_id = st.text_input("CALLSIGN:", "ANONYM").strip().upper()
        if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
        is_admin = (artist_id == "TOMAS2026")
        st.markdown(f"<h2 style='text-align:center; color:#00d2ff;'>⚡ {st.session_state.user_db[artist_id]}</h2>", unsafe_allow_html=True)

    with st.expander("🌍 MILJÖ (ATMOSPHERE)", expanded=True):
        c1, c2 = st.columns(2)
        # Direktgenerering för specifika önskemål
        if c1.button("RYMDEN 🌌"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Cinematic deep space, nebula, stars, bright colors, 4k"})
            st.session_state.app_bg = get_url(res); add_log("Env: Deep Space set."); st.rerun()
        if c2.button("SKOG 🌲"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Sunlit magic forest, lush greenery, misty morning, 4k"})
            st.session_state.app_bg = get_url(res); add_log("Env: Forest set."); st.rerun()
        if c1.button("HAV 🌊"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Tropical turquoise ocean, bright sunlight, underwater light rays, 4k"})
            st.session_state.app_bg = get_url(res); add_log("Env: Ocean set."); st.rerun()
        if c2.button("STUDIO 🎚️"):
            res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Professional music studio control desk, neon buttons, bright faders, 4k"})
            st.session_state.app_bg = get_url(res); add_log("Env: Studio Console set."); st.rerun()

    with st.expander("📊 SYSTEM", expanded=True):
        st.session_state.lang = st.radio("SPRAK", ["Svenska", "English"], horizontal=True)
        st.slider("OUTPUT GAIN", 0, 100, 80)
    
    st.markdown("### 📝 LIVE LOG")
    log_html = "".join([f"<div>{l}</div>" for l in reversed(st.session_state.logs)])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
apply_design()
st.markdown('<div class="logo-text">⚡ MAXIMUSIKAI STUDIO ⚡</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("OPEN STUDIO GATE", use_container_width=True): 
        st.session_state.agreed = True; add_log("Gateway Opened."); st.rerun()
    st.stop()

token = st.secrets.get("REPLICATE_API_TOKEN")
if token:
    os.environ["REPLICATE_API_TOKEN"] = token
    tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV", "⚙️ ADMIN"] if is_admin else ["🪄 MAGI", "🎬 REGI", "🎧 MUSIK", "📚 ARKIV"])

    with tabs[0]: # MAGI
        c1, c2 = st.columns([2, 1])
        prompt = c1.text_area("VAD SKALL SKAPAS?", placeholder="Beskriv din vision här...")
        aspect = c2.selectbox("RATIO", ["1:1", "16:9", "9:16"])
        if st.button("🔥 STARTA GENERERING", use_container_width=True):
            if is_admin or st.session_state.user_db[artist_id] > 0:
                with st.status("AI Core Processing...") as s:
                    img = get_url(replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": aspect}))
                    try:
                        aud = str(replicate.run("facebookresearch/musicgen:7b76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": prompt, "duration": 8}))
                    except: aud = None
                    if not is_admin: st.session_state.user_db[artist_id] -= 1
                    st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt, "url": img, "audio": aud})
                    add_log(f"New Creation: {prompt[:15]}..."); s.update(label="Ready!", state="complete"); st.rerun()

    with tabs[1]: # REGI
        st.subheader("🎬 LUMA VIDEO ENGINE")
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if my_imgs:
            sel = st.selectbox("VÄLJ KÄLLA", [p["name"][:50] for p in my_imgs])
            target = next(p for p in my_imgs if p["name"][:50] == sel)
            st.image(target["url"], width=350)
            if st.button("🎬 SKAPA VIDEO (5 UNITS)"):
                if is_admin or st.session_state.user_db[artist_id] >= 5:
                    with st.spinner("Rendrerar video..."):
                        vid = get_url(replicate.run("luma-ai/luma-dream-machine", input={"prompt": "Cinematic movement", "image_url": target["url"]}))
                        st.video(vid); add_log("Video sync complete.")
                        if not is_admin: st.session_state.user_db[artist_id] -= 5
                else: st.error("Ladda units!")

    with tabs[2]: # MUSIK
        st.subheader("🎧 BEAT STATION")
        m_in = st.text_input("STIL/GENRE")
        if st.button("KOMPONERA"):
            with st.spinner("Jobbar..."):
                res = replicate.run("facebookresearch/musicgen:7b76a8258b299f66db13045610ec090409a25032899478f7e2c9f5835b800e47", input={"prompt": m_in, "duration": 10})
                st.audio(str(res)); add_log(f"Beat: {m_in[:15]}")

    with tabs[3]: # ARKIV
        st.subheader("📚 STUDIO ARKIV")
        my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        cols = st.columns(3)
        for idx, p in enumerate(reversed(my_stuff)):
            with cols[idx % 3]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image(p["url"])
                if st.button("ANVÄND SOM BG", key=f"bg_{p['id']}"):
                    st.session_state.app_bg = p["url"]; add_log("UI Background updated."); st.rerun()
                if p["audio"]: st.audio(p["audio"])
                st.markdown('</div>', unsafe_allow_html=True)

    if is_admin and len(tabs) > 4:
        with tabs[4]:
            st.write(st.session_state.user_db)
            if st.button("HARD RESET"): st.session_state.gallery = []; st.rerun()
else:
    st.error("Lägg in REPLICATE_API_TOKEN i Secrets!")
