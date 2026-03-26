import streamlit as st
import replicate
import os
import requests
from streamlit_lottie import st_lottie

# --- 1. CONFIG ---
st.set_page_config(page_title="MAXIMUSIK AI PRO", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session State
if "active_window" not in st.session_state: st.session_state.active_window = None
if "synth_res" not in st.session_state: st.session_state.synth_res = None

# --- 2. LOTTIE LOADER ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

# Länkar till snygga rörliga tech-ikoner
lottie_synth = load_lottieurl("https://lottie.host") # AI/Visual
lottie_audio = load_lottieurl("https://lottie.host") # Soundwave
lottie_video = load_lottieurl("https://lottie.host") # Camera
lottie_sys = load_lottieurl("https://lottie.host")   # Settings/Chip

# --- 3. DESIGN (CSS) ---
def apply_ui():
    st.markdown("""
        <style>
        .stAppViewContainer {
            background-color: #020205 !important;
            background-image: radial-gradient(circle at 50% 50%, #001a2d 0%, #020205 100%) !important;
        }
        
        /* Transparenta knappar som ligger OVANPÅ animationerna */
        div.stButton > button {
            background: rgba(0, 242, 255, 0.0) !important;
            border: 1px solid rgba(0, 242, 255, 0.2) !important;
            height: 180px !important;
            width: 100% !important;
            border-radius: 30px !important;
            position: relative;
            z-index: 10;
            transition: 0.4s all !important;
        }
        div.stButton > button:hover {
            background: rgba(0, 242, 255, 0.1) !important;
            border-color: #00f2ff !important;
            box-shadow: 0 0 30px rgba(0, 242, 255, 0.2) !important;
        }

        .pro-title {
            text-align: center; color: white; font-size: 5rem; font-weight: 900; 
            letter-spacing: -2px; margin-bottom: 0;
            background: linear-gradient(to bottom, #ffffff 40%, #00f2ff 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .label { text-align: center; color: #00f2ff; font-family: monospace; font-weight: bold; margin-top: -30px; letter-spacing: 3px; z-index: 1;}
        
        .window {
            background: rgba(5, 7, 10, 0.98) !important;
            backdrop-filter: blur(20px); border: 1px solid #00f2ff33;
            border-radius: 30px; padding: 40px;
        }
        
        /* Centrera animationerna bakom knapparna */
        .lottie-container {
            margin-top: -180px;
            pointer-events: none;
        }
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 class='pro-title'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:10px; opacity:0.4;'>ANIMATED_KERNEL_LOADED</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, c1, c2, c3, c4, _ = st.columns([0.5, 1, 1, 1, 1, 0.5])
    
    with c1:
        st.button(" ", key="b1", on_click=lambda: setattr(st.session_state, 'active_window', 'SYNTHESIS'))
        st.markdown('<div class="lottie-container">', unsafe_allow_html=True)
        st_lottie(lottie_synth, height=180, key="l1")
        st.markdown('</div><p class="label">SYNTH</p>', unsafe_allow_html=True)

    with c2:
        st.button(" ", key="b2", on_click=lambda: setattr(st.session_state, 'active_window', 'AUDIO'))
        st.markdown('<div class="lottie-container">', unsafe_allow_html=True)
        st_lottie(lottie_audio, height=180, key="l2")
        st.markdown('</div><p class="label">AUDIO</p>', unsafe_allow_html=True)

    with c3:
        st.button(" ", key="b3", on_click=lambda: setattr(st.session_state, 'active_window', 'VIDEO'))
        st.markdown('<div class="lottie-container">', unsafe_allow_html=True)
        st_lottie(lottie_video, height=180, key="l3")
        st.markdown('</div><p class="label">VIDEO</p>', unsafe_allow_html=True)

    with c4:
        st.button(" ", key="b4", on_click=lambda: setattr(st.session_state, 'active_window', 'SYSTEM'))
        st.markdown('<div class="lottie-container">', unsafe_allow_html=True)
        st_lottie(lottie_sys, height=180, key="l4")
        st.markdown('</div><p class="label">SYSTEM</p>', unsafe_allow_html=True)

# --- 5. WINDOW MANAGER ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.15, 1, 0.15])
    
    with win_col:
        st.markdown('<div class="window">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:#00f2ff; margin:0;'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid #333; margin:25px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            p = st.text_area("MATRIX COMMAND:")
            if st.button("GENERATE"):
                with st.status("DREAMING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res: st.image(st.session_state.synth_res)

        elif st.session_state.active_window == "SYSTEM":
            st.success("CORE ONLINE")
            st.info("Animation Engine: Lottie | Kernel: Aurora V3")
        
        st.markdown('</div>', unsafe_allow_html=True)









