import streamlit as st
import replicate
import os
import time
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO CONSOLE", page_icon="🎚️", layout="wide")

# BAKGRUND: Ett äkta studio-bord (High-End Console)
STUDIO_BG = "https://images.unsplash.com"

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {"ANONYM": 10, "TOMAS2026": 999}

# --- 2. STUDIO CONSOLE ENGINE (CSS) ---
def apply_design():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com');

        /* Bakgrund: Studio-bordet */
        .stApp, [data-testid="stSidebar"] {{
            background: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.4)), url("{STUDIO_BG}") !important;
            background-size: cover !important;
            background-attachment: fixed !important;
            background-position: center !important;
        }}

        /* TOTAL TRANSPARENS PÅ ALLA ELEMENT */
        div[data-testid="stVerticalBlock"], 
        div[data-baseweb="textarea"], 
        div[data-baseweb="input"], 
        div[data-baseweb="select"],
        textarea, input, .stSelectbox div {{
            background: rgba(255, 255, 255, 0.02) !important; /* Nästan osynlig */
            backdrop-filter: blur(10px) !important;
            color: #fff !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 4px !important;
            font-family: 'Share Tech Mono', monospace !important;
        }}

        /* KNAPPAR: Som glas-knappar på mixern */
        .stButton>button {{
            background: rgba(255, 255, 255, 0.05) !important;
            color: #fff !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            backdrop-filter: blur(15px);
            font-family: 'Share Tech Mono';
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: bold !important;
            width: 100%;
            height: 50px;
        }}
        .stButton>button:hover {{
            background: rgba(0, 242, 255, 0.2) !important;
            border: 1px solid #00f2ff !important;
            box-shadow: 0 0 20px rgba(0, 242, 255, 0.4);
            color: #00f2ff !important;
        }}

        /* LOGO */
        .logo-text {{
            font-family: 'Share Tech Mono'; font-size: 3.5rem; font-weight: 900; 
            color: #fff; text-align: center; letter-spacing: 8px;
            text-shadow: 0 0 15px rgba(0, 242, 255, 0.8);
            margin-bottom: 30px;
        }}

        /* LIVE LOG & CARDS */
        .card {{
            background: rgba(0, 0, 0, 0.3) !important;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 15px; border-radius: 8px;
        }}

        h1, h2, h3, p, label {{ color: white !important; font-family: 'Share Tech Mono'; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. MISSION CONTROL (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🛰️ CONSOLE CONTROL")
    artist_id = st.text_input("USER_ID:", "ANONYM").upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    
    st.markdown(f"## UNITS: {st.session_state.user_db[artist_id]}")
    st.divider()
    
    # Knapp för att byta mixer-bord om man vill
    if st.button("🔄 RE-SYNC CONSOLE"):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Professional music production console close-up, neon lighting, 8k"})
        st.session_state.app_bg = str(res[0] if isinstance(res, list) else res)
        st.rerun()

# --- 4. STUDIO INTERFACE ---
apply_design()
st.markdown('<div class="logo-text">MAXIMUSIKAI</div>', unsafe_allow_html=True)

os.environ["REPLICATE_API_TOKEN"] = st.secrets.get("REPLICATE_API_TOKEN", "")

# --- SEKTION: MASTER INPUT ---
st.markdown("### 🎚️ MASTER PARAMETERS")
st.markdown('<div class="card">', unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])

with col1:
    prompt = st.text_area("VISIONARY INPUT", placeholder="DESCRIBE AUDIO/VISUAL SYNTHESIS...")
with col2:
    aspect = st.selectbox("FRAME RATIO", ["1:1", "16:9", "9:16"])
    if st.button("🔥 EXECUTE"):
        if st.session_state.user_db[artist_id] > 0:
            with st.status("PROCESSING..."):
                img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"Professional studio shot: {prompt}", "aspect_ratio": aspect})
                img_url = str(img[0] if isinstance(img, list) else img)
                st.session_state.gallery.append({"artist": artist_id, "name": prompt, "url": img_url})
                st.session_state.user_db[artist_id] -= 1
                st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# --- SEKTION: DATA VAULT (ARKIV) ---
st.markdown("### 📚 STUDIO DATA VAULT")
if st.session_state.gallery:
    my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
    cols = st.columns(3)
    for idx, p in enumerate(reversed(my_stuff)):
        with cols[idx % 3]:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.image(p["url"])
            if st.button("SYNC TO CONSOLE", key=f"bg_{idx}"):
                st.session_state.app_bg = p["url"]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
