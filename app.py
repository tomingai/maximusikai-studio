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

# Session State
if "active_window" not in st.session_state: st.session_state.active_window = None
if "synth_res" not in st.session_state: st.session_state.synth_res = None

# --- 3. LOTTIE LOADER (UPPDATERADE STABILA LÄNKAR) ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200: return None
        return r.json()
    except:
        return None

# Dessa länkar är direkt till rå-JSON (viktigt för att det ska röra sig)
lottie_synth = load_lottieurl("https://assets5.lottiefiles.com") # AI Robot
lottie_audio = load_lottieurl("https://assets5.lottiefiles.com")    # Audio Wave
lottie_video = load_lottieurl("https://assets5.lottiefiles.com") # Video/Play
lottie_sys = load_lottieurl("https://assets5.lottiefiles.com")     # Gears/System

# --- 4. DESIGN (CSS) ---
def apply_ui():
    st.markdown("""
        <style>
        .stAppViewContainer {
            background-color: #020205 !important;
            background-image: radial-gradient(circle at 50% 50%, #001a2d 0%, #020205 100%) !important;
        }
        
        /* Transparent knapp som ligger framför animationen */
        div[data-testid="stButton"] > button {
            background: rgba(0, 242, 255, 0.0) !important;
            border: 2px solid rgba(0, 242, 255, 0.2) !important;
            height: 180px !important;
            width: 100% !important;
            border-radius: 30px !important;
            position: relative;
            z-index: 100 !important;
            color: transparent !important;
            transition: 0.3s all !important;
        }
        div[data-testid="stButton"] > button:hover {
            border-color: #00f2ff !important;
            background: rgba(0, 242, 255, 0.05) !important;
            box-shadow: 0 0 30px rgba(0, 242, 255, 0.3) !important;
        }

        .pro-title {
            text-align: center; color: white; font-size: 5rem; font-weight: 900; 
            letter-spacing: -2px; margin-bottom: 0;
            background: linear-gradient(to bottom, #ffffff 40%, #00f2ff 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .label { text-align: center; color: #00f2ff; font-family: monospace; font-weight: bold; margin-top: 10px; letter-spacing: 3px; }
        
        /* Container för Lottie - placeras bakom knappen */
        .lottie-box { 
            margin-top: -180px; 
            pointer-events: none; 
            z-index: 1 !important;
        }

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
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:10px; opacity:0.4;'>NEURAL_CORE_V3</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, c1, c2, c3, c4, _ = st.columns([0.5, 1, 1, 1, 1, 0.5])
    
    modules = [
        ("SYNTHESIS", lottie_synth, "🎨"),
        ("AUDIO", lottie_audio, "🔊"),
        ("VIDEO", lottie_video, "🎬"),
        ("SYSTEM", lottie_sys, "⚙️")
    ]
    
    cols = [c1, c2, c3, c4]

    for i, col in enumerate(cols):
        name, lottie_data, fallback = modules[i]
        with col:
            # Knappen tar klicket
            if st.button(fallback, key=f"btn_{i}"):
                st.session_state.active_window = name
                st.rerun()
            
            # Animationen rör sig bakom knappen
            if LOTTIE_AVAILABLE and lottie_data:
                st.markdown('<div class="lottie-box">', unsafe_allow_html=True)
                st_lottie(lottie_data, height=180, key=f"anim_{i}", speed=1, loop=True, quality="high")
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

        elif st.session_state.active_window == "SYSTEM":
            st.code(f"LOTTIE_ENGINE: {'LOADED' if LOTTIE_AVAILABLE else 'ERROR'}\nSYSTEM_STATUS: NOMINAL")
        
        st.markdown('</div>', unsafe_allow_html=True)










