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

        /* 1. BAKGRUNDSSYNK */
        .stApp, [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"] {{
            background: linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.3)), url("{bg_url}") !important;
            background-size: cover !important; background-attachment: fixed !important;
            background-position: center !important;
        }}

        /* 2. FORCE TRANSPARENCY PÅ ALLA INPUTS & TEXT AREAS */
        /* Vi siktar på både behållaren och det faktiska input-elementet */
        div[data-baseweb="base-input"], 
        div[data-baseweb="textarea"], 
        textarea, 
        input, 
        .stTextArea textarea, 
        .stTextInput input {{
            background-color: transparent !important;
            background: transparent !important;
            backdrop-filter: blur(15px) !important;
            color: #00f2ff !important;
            border: 1px solid rgba(0, 242, 255, 0.5) !important;
            border-radius: 0px !important;
            font-family: 'Orbitron', sans-serif;
        }}

        /* Fixar specifikt bakgrunden som Streamlit lägger på när man klickar i rutan */
        textarea:focus, input:focus {{
            background-color: rgba(0, 242, 255, 0.05) !important;
            outline: none !important;
            border: 1px solid #00f2ff !important;
        }}

        /* 3. CONTAINERS & TABS */
        [data-testid="stVerticalBlock"], [data-testid="stExpander"], .stTabs {{
            background-color: transparent !important;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            background-color: transparent !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(0,0,0,0.2) !important;
            border: 1px solid rgba(0, 242, 255, 0.2) !important;
            color: white !important;
            font-family: 'Orbitron';
        }}

        /* 4. KNAPPAR */
        .stButton>button {{
            background: rgba(0, 0, 0, 0) !important;
            color: #00f2ff !important;
            border: 1px solid #00f2ff !important;
            backdrop-filter: blur(10px);
            font-family: 'Orbitron';
            text-transform: uppercase;
        }}
        .stButton>button:hover {{
            background: rgba(0, 242, 255, 0.15) !important;
            box-shadow: 0 0 20px #00f2ff;
        }}

        /* 5. CARDS (De genomskinliga ramarna) */
        .card {{
            background: rgba(255, 255, 255, 0.02) !important;
            backdrop-filter: blur(30px);
            border: 1px solid rgba(0, 242, 255, 0.2);
            padding: 20px;
            margin-bottom: 10px;
        }}
        
        .log-box {{
            background: rgba(0,0,0,0.4);
            color: #00f2ff;
            font-family: monospace;
            padding: 10px;
            border-left: 2px solid #00f2ff;
        }}

        h1, h2, h3, p, label {{ color: white !important; font-family: 'Orbitron'; text-shadow: 2px 2px 10px #000; }}
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
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Epic deep space nebula, 8k"})
        st.session_state.app_bg = str(res if isinstance(res, list) else res)
        st.rerun()

    st.markdown("### 📝 LIVE LOG")
    log_html = "".join([f"<div>{l}</div>" for l in reversed(st.session_state.logs)])
    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
apply_design()
st.markdown('<div style="text-align:center; font-family:Orbitron; font-size:3.5rem; letter-spacing:10px; text-shadow:0 0 20px #00f2ff; color:white; margin-bottom:20px;">MAXIMUSIKAI</div>', unsafe_allow_html=True)

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
        # Här är rutan som ska vara transparent
        prompt = col1.text_area("VISIONARY INPUT", placeholder="Skriv in din vision...")
        aspect = col2.selectbox("RATIO", ["1:1", "16:9", "9:16"])
        if st.button("🔥 EXECUTE GENERATION", use_container_width=True):
            with st.status("Synthesizing..."):
                img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"Space: {prompt}", "aspect_ratio": aspect})
                img_url = str(img if isinstance(img, list) else img)
                st.session_state.gallery.append({"id": time.time(), "artist": artist_id, "name": prompt, "url": img_url})
                if not is_admin: st.session_state.user_db[artist_id] -= 1
                add_log(f"Gen: {prompt[:10]}..."); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]: # REGI
        my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
        if my_imgs:
            sel = st.selectbox("SOURCE", [p["name"][:50] for p in my_imgs])
            target = next(p for p in my_imgs if p["name"][:50] == sel)
            st.image(target["url"], use_container_width=True)
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

