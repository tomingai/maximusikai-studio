import streamlit as st
import replicate
import os
import requests

# --- 1. IMPORT LOTTIE ---
try:
    from streamlit_lottie import st_lottie
    LOTTIE_AVAILABLE = True
except ImportError:
    LOTTIE_AVAILABLE = False

# --- 2. CONFIG ---
st.set_page_config(page_title="MAXIMUSIK AI PRO", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session State Init
if "active_window" not in st.session_state: st.session_state.active_window = None
if "synth_res" not in st.session_state: st.session_state.synth_res = None
if "audio_res" not in st.session_state: st.session_state.audio_res = None

# --- 3. LOTTIE LOADER ---
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# Pro-ikoner (Lottie JSON)
lottie_synth = load_lottieurl("https://assets10.lottiefiles.com") # AI
lottie_audio = load_lottieurl("https://assets10.lottiefiles.com") # Audio
lottie_video = load_lottieurl("https://assets1.lottiefiles.com") # Video
lottie_sys = load_lottieurl("https://assets1.lottiefiles.com") # System

# --- 4. DESIGN (CSS) ---
def apply_ui():
    st.markdown("""
        <style>
        .stAppViewContainer {
            background-color: #020205 !important;
            background-image: radial-gradient(circle at 50% 50%, #001a2d 0%, #020205 100%) !important;
        }
        
        /* Knappar ovanpå animationerna */
        div[data-testid="stButton"] > button {
            background: rgba(0, 242, 255, 0.02) !important;
            border: 1px solid rgba(0, 242, 255, 0.2) !important;
            height: 180px !important;
            width: 100% !important;
            border-radius: 30px !important;
            z-index: 10;
            transition: 0.3s all !important;
            color: transparent !important;
        }
        div[data-testid="stButton"] > button:hover {
            background: rgba(0, 242, 255, 0.1) !important;
            border-color: #00f2ff !important;
            transform: scale(1.02) !important;
        }

        .pro-title {
            text-align: center; color: white; font-size: 5rem; font-weight: 900; 
            letter-spacing: -2px; margin-bottom: 0;
            background: linear-gradient(to bottom, #ffffff 40%, #00f2ff 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .label { text-align: center; color: #00f2ff; font-family: monospace; font-weight: bold; margin-top: 10px; letter-spacing: 3px; }
        .lottie-box { margin-top: -185px; pointer-events: none; text-align: center; }

        .window {
            background: rgba(5, 7, 10, 0.98) !important;
            backdrop-filter: blur(25px); border: 1px solid #00f2ff33;
            border-radius: 30px; padding: 40px; color: white;
        }
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 5. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 class='pro-title'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:10px; opacity:0.4;'>NEURAL_CORE_READY</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, c1, c2, c3, c4, _ = st.columns([0.5, 1, 1, 1, 1, 0.5])
    
    modules = [
        ("SYNTHESIS", lottie_synth, "🌌"),
        ("AUDIO", lottie_audio, "🧬"),
        ("VIDEO", lottie_video, "🛰️"),
        ("SYSTEM", lottie_sys, "💎")
    ]
    
    cols = [c1, c2, c3, c4]

    for i, col in enumerate(cols):
        name, lottie_data, fallback = modules[i]
        with col:
            if st.button(fallback, key=f"btn_{i}"):
                st.session_state.active_window = name
                st.rerun()
            
            if LOTTIE_AVAILABLE and lottie_data:
                st.markdown('<div class="lottie-box">', unsafe_allow_html=True)
                st_lottie(lottie_data, height=180, key=f"lottie_{i}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown(f'<p class="label">{name}</p>', unsafe_allow_html=True)

# --- 6. WINDOW MANAGER ---
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
            p = st.text_area("COMMAND:")
            if st.button("EXECUTE"):
                with st.status("PROCESSING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res: st.image(st.session_state.synth_res)

        elif st.session_state.active_window == "AUDIO":
            p = st.text_input("SONIC PARAMETERS:")
            if st.button("GENERATE"):
                with st.status("TUNING..."):
                    res = replicate.run("facebookresearch/musicgen:7b57424c30623a3111867c006579c3b88d2f1f0a204364ef0c6e93833f48a901", input={"prompt": p})
                    st.session_state.audio_res = res
                st.rerun()
            if st.session_state.audio_res: st.audio(st.session_state.audio_res)

        elif st.session_state.active_window == "SYSTEM":
            st.code(f"ANIMATION_ENGINE: {'LOADED' if LOTTIE_AVAILABLE else 'ERROR'}\nSYSTEM_STATUS: NOMINAL")
            if st.button("HARD RESET"):
                st.session_state.synth_res = None
                st.session_state.audio_res = None
                st.success("CACHE PURGED")
        
        st.markdown('</div>', unsafe_allow_html=True)










