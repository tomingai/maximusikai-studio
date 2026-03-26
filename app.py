import streamlit as st
import replicate
import os
from datetime import datetime

# --- 1. SYSTEM BOOT ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Initialize States
if "active_app" not in st.session_state: st.session_state.active_app = "DESKTOP"
if "start_open" not in st.session_state: st.session_state.start_open = False
if "vault" not in st.session_state: st.session_state.vault = []
if "last_res" not in st.session_state: st.session_state.last_res = None

# --- 2. CSS: TASKBAR & START MENU ---
def apply_os_interface():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com');
        
        /* BACKGROUND */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.7)), 
                        url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
        }}

        /* TASKBAR */
        .taskbar {{
            position: fixed; bottom: 0; left: 0; width: 100%; height: 45px;
            background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(15px);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex; align-items: center; padding: 0 15px; z-index: 9999;
        }}

        /* START BUTTON */
        .start-btn-ui {{
            background: linear-gradient(45deg, #00f2ff, #0066ff);
            border-radius: 5px; width: 35px; height: 35px;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; transition: 0.3s;
        }}
        .start-btn-ui:hover {{ box-shadow: 0 0 15px #00f2ff; }}

        /* START MENU PANEL */
        .start-menu {{
            position: fixed; bottom: 55px; left: 15px; width: 300px;
            background: rgba(10, 10, 10, 0.95); backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px;
            padding: 20px; z-index: 10000; box-shadow: 0 10px 40px rgba(0,0,0,0.8);
            font-family: 'Inter', sans-serif;
        }}

        /* DESKTOP ICONS (Compact) */
        .icon-card {{
            background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px;
            padding: 20px; text-align: center; transition: 0.3s;
            max-width: 150px; margin: auto; position: relative;
        }}
        .icon-card:hover {{ background: rgba(255, 255, 255, 0.1); border-color: #00f2ff; transform: translateY(-5px); }}
        .icon-emoji {{ font-size: 40px; margin-bottom: 10px; }}
        .icon-title {{ color: white; font-weight: 800; font-size: 13px; text-transform: uppercase; }}

        /* HIDE STREAMLIT BUTTONS BUT KEEP HITBOX */
        .stButton>button {{ opacity: 0; position: absolute; width: 100%; height: 100%; top: 0; left: 0; z-index: 10; cursor: pointer; }}
        </style>
    """, unsafe_allow_html=True)

apply_os_interface()

# --- 3. START MENU LOGIC ---
if st.session_state.start_open:
    st.markdown(f"""
        <div class="start-menu">
            <h3 style="color:white; margin-bottom:5px;">MAXIMUS_OS</h3>
            <p style="color:#444; font-size:10px; font-family:'JetBrains Mono';">SYSTEM_STATUS: OPTIMAL</p>
            <hr style="border:0.5px solid #222;">
            <div style="color:#00f2ff; font-size:12px; margin-bottom:10px;">👤 USER: ADMIN</div>
            <div style="color:#999; font-size:11px; margin-bottom:5px;">📁 TOTAL_ASSETS: {len(st.session_state.vault)}</div>
            <div style="color:#999; font-size:11px; margin-bottom:20px;">⏱️ UPTIME: 124m</div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("CLOSE_MENU", key="close_st"):
        st.session_state.start_open = False
        st.rerun()

# --- 4. DESKTOP VIEW ---
if st.session_state.active_app == "DESKTOP":
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-family:Inter; font-weight:900; font-size:4rem; letter-spacing:-2px;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Grid för ikoner
    _, i1, i2, i3, _ = st.columns([1, 1, 1, 1, 1])
    
    with i1:
        st.markdown('<div class="icon-card"><div class="icon-emoji">🌌</div><div class="icon-title">Synthesis</div></div>', unsafe_allow_html=True)
        if st.button("L_SYNTH", key="os_synth"):
            st.session_state.active_app = "SYNTH"
            st.rerun()

    with i2:
        st.markdown('<div class="icon-card"><div class="icon-emoji">🎵</div><div class="icon-title">Audio Lab</div></div>', unsafe_allow_html=True)
        if st.button("L_AUDIO", key="os_audio"):
            st.session_state.active_app = "AUDIO"
            st.rerun()

    with i3:
        st.markdown('<div class="icon-card"><div class="icon-emoji">🎬</div><div class="icon-title">Video Flux</div></div>', unsafe_allow_html=True)
        if st.button("L_VIDEO", key="os_video"):
            st.session_state.active_app = "VIDEO"
            st.rerun()

# --- 5. APP VIEW: SYNTHESIS ---
elif st.session_state.active_app == "SYNTH":
    st.markdown("<style>.stApp { background: #050505 !important; }</style>", unsafe_allow_html=True)
    if st.button("← BACK"):
        st.session_state.active_app = "DESKTOP"
        st.rerun()
    st.title("🌌 NEURAL_SYNTHESIS")
    # ... din bild-kod här ...

# --- 6. TASKBAR & START BUTTON ---
st.markdown('<div class="taskbar"><div class="start-btn-ui">M</div></div>', unsafe_allow_html=True)
with st.container():
    # En osynlig knapp placerad över "M" i taskbaren
    c_start, _ = st.columns([0.05, 0.95])
    with c_start:
        if st.button("S", key="start_trig", help="Open Start Menu"):
            st.session_state.start_open = not st.session_state.start_open
            st.rerun()


