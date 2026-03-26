import streamlit as st
import replicate
import os
import requests
from datetime import datetime

# --- 1. SYSTEM BOOT ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

# API Token Setup
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Initialize Session State
if "active_app" not in st.session_state: st.session_state.active_app = "DESKTOP"
if "vault" not in st.session_state: st.session_state.vault = []
if "last_res" not in st.session_state: st.session_state.last_res = None
if "last_audio" not in st.session_state: st.session_state.last_audio = None

# --- 2. THEME & DESKTOP CSS ---
def apply_os_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com');
        
        /* DESKTOP BACKGROUND */
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.7)), 
                        url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            transition: 1s ease-in-out;
        }

        /* LARGE GLASS ICONS */
        .icon-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 40px;
            padding: 60px 20px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            margin-bottom: 30px;
            position: relative;
        }
        .icon-card:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: #00f2ff;
            transform: translateY(-15px) scale(1.05);
            box-shadow: 0 30px 60px rgba(0,0,0,0.6);
        }
        .icon-emoji { font-size: 100px; margin-bottom: 20px; filter: drop-shadow(0 0 10px rgba(0,242,255,0.4)); }
        .icon-title { color: white; font-family: 'Inter'; font-weight: 900; font-size: 24px; text-transform: uppercase; letter-spacing: 2px; }
        .icon-sub { color: #00f2ff; font-family: 'JetBrains Mono'; font-size: 10px; margin-top: 8px; opacity: 0.7; }

        /* HIDE NATIVE BUTTONS BUT KEEP HITBOX */
        .stButton>button {
            position: absolute; width: 100%; height: 350px; top: 0; left: 0;
            opacity: 0; z-index: 10; cursor: pointer;
        }

        /* BACK BUTTON STYLE */
        .back-btn {
            background: rgba(0,0,0,0.5) !important;
            border: 1px solid #00f2ff !important;
            color: #00f2ff !important;
            font-family: 'JetBrains Mono' !important;
        }
        
        /* INPUT FIELDS */
        textarea, input {
            background: rgba(0,0,0,0.8) !important;
            border: 1px solid #111 !important;
            color: #00f2ff !important;
            font-family: 'JetBrains Mono' !important;
        }
        </style>
    """, unsafe_allow_html=True)

apply_os_theme()

# --- 3. DESKTOP VIEW ---
if st.session_state.active_app == "DESKTOP":
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-family:Inter; font-weight:900; font-size:5rem; letter-spacing:-4px;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:JetBrains Mono; letter-spacing:10px; font-size:12px;'>NEURAL_CORE_OS_v5.0</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # 3 Stora Ikoner i rader
    i1, i2, i3 = st.columns(3, gap="large")
    
    with i1:
        st.markdown('<div class="icon-card"><div class="icon-emoji">🌌</div><div class="icon-title">Synthesis</div><div class="icon-sub">GENERATE_VISUALS</div></div>', unsafe_allow_html=True)
        if st.button("LAUNCH_SYNTH", key="os_synth"):
            st.session_state.active_app = "SYNTH"
            st.rerun()

    with i2:
        st.markdown('<div class="icon-card"><div class="icon-emoji">🎵</div><div class="icon-title">Audio Lab</div><div class="icon-sub">SONIC_ENGINE</div></div>', unsafe_allow_html=True)
        if st.button("LAUNCH_AUDIO", key="os_audio"):
            st.session_state.active_app = "AUDIO"
            st.rerun()

    with i3:
        st.markdown('<div class="icon-card"><div class="icon-emoji">🎬</div><div class="icon-title">Video Flux</div><div class="icon-sub">MOTION_SYNTH</div></div>', unsafe_allow_html=True)
        if st.button("LAUNCH_VIDEO", key="os_video"):
            st.session_state.active_app = "VIDEO"
            st.rerun()

# --- 4. APP VIEW: SYNTHESIS ---
elif st.session_state.active_app == "SYNTH":
    st.markdown("<style>.stApp { background: #050505 !important; }</style>", unsafe_allow_html=True)
    if st.button("← RETURN_TO_DESKTOP"):
        st.session_state.active_app = "DESKTOP"
        st.rerun()
    
    st.title("🌌 NEURAL_SYNTHESIS_UNIT")
    c1, c2 = st.columns([1, 1.8])
    with c1:
        prompt = st.text_area("PARAMETER_INPUT", placeholder="Forest in space, neon stars...", height=200)
        ratio = st.selectbox("ASPECT_RATIO", ["1:1", "16:9", "9:16"])
        if st.button("EXECUTE_SYNTHESIS", use_container_width=True):
            if prompt:
                with st.status("PROCESSING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": ratio})
                    st.session_state.last_res = res if isinstance(res, list) else res
                    st.session_state.vault.append({"url": st.session_state.last_res, "prompt": prompt})
                st.rerun()
    with c2:
        if st.session_state.last_res:
            st.image(st.session_state.last_res, use_container_width=True)

# --- 5. APP VIEW: AUDIO LAB ---
elif st.session_state.active_app == "AUDIO":
    st.markdown("<style>.stApp { background: #0a000a !important; }</style>", unsafe_allow_html=True)
    if st.button("← RETURN_TO_DESKTOP"):
        st.session_state.active_app = "DESKTOP"
        st.rerun()
        
    st.title("🎵 SONIC_WAVEFORM_LAB")
    if st.session_state.last_res:
        c_a1, c_a2 = st.columns(2)
        with c_a1:
            st.image(st.session_state.last_res, caption="REFERENCE_IMAGE", width=400)
        with c_a2:
            audio_p = st.text_input("AUDIO_MOOD", "Ambient space techno, deep forest reverb")
            if st.button("SYNTHESIZE_SOUNDTRACK", use_container_width=True):
                with st.status("COMPOSING..."):
                    audio = replicate.run("facebookresearch/musicgen:7a76a8258a299f6600c61230623a39e2abc0fa15f8a0da54d9e50f3c5f201089", 
                                          input={"prompt": audio_p, "duration": 10})
                    st.session_state.last_audio = audio
                st.rerun()
            if st.session_state.last_audio:
                st.audio(st.session_state.last_audio)
    else:
        st.warning("LOAD_SOURCE_IMAGE_FROM_SYNTH_FIRST")

# --- 6. SYSTEM TRAY ---
st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.9); padding: 5px 20px; border-top: 1px solid #111; display: flex; justify-content: space-between;">
        <span style="color: #444; font-family: 'JetBrains Mono'; font-size: 10px;">CORE_v5.0_ONLINE</span>
        <span style="color: #444; font-family: 'JetBrains Mono'; font-size: 10px;">MAXIMUSIKAI_PREMIER</span>
    </div>
""", unsafe_allow_html=True)


