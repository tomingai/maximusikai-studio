import streamlit as st
import replicate
import os

# --- 1. CONFIG ---
st.set_page_config(page_title="MAXIMUSIK AI PRO", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session State Init
if "active_window" not in st.session_state: st.session_state.active_window = None
if "synth_res" not in st.session_state: st.session_state.synth_res = None
if "audio_res" not in st.session_state: st.session_state.audio_res = None

# --- 2. DESIGN (CSS) ---
def apply_ui():
    st.markdown("""
        <style>
        /* FUTURISTISK CYBERPUNK BAKGRUND */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }

        /* MEGA NEON-KNAPPAR */
        div[data-testid="stButton"] > button {
            display: block !important;
            margin: 0 auto !important;
            width: 220px !important; 
            height: 220px !important;
            border-radius: 45px !important;
            border: 3px solid rgba(0, 242, 255, 0.3) !important;
            background: rgba(0, 20, 40, 0.4) !important;
            backdrop-filter: blur(10px) !important;
            font-size: 6.5rem !important; 
            line-height: 1 !important;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.7) !important;
        }
        
        div[data-testid="stButton"] > button:hover {
            transform: scale(1.12) translateY(-15px) !important;
            border-color: #00f2ff !important;
            background: rgba(0, 242, 255, 0.1) !important;
            box-shadow: 0 0 60px rgba(0, 242, 255, 0.5), inset 0 0 20px rgba(0, 242, 255, 0.2) !important;
            text-shadow: 0 0 35px rgba(255,255,255,0.9) !important;
        }

        .pro-title {
            text-align: center; color: white; font-size: 6.5rem; font-weight: 900; 
            letter-spacing: -3px; margin-top: 50px; margin-bottom: 0;
            background: linear-gradient(to bottom, #ffffff 50%, #00f2ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(0, 242, 255, 0.4);
        }
        .label { 
            text-align: center; color: #00f2ff; font-family: 'Courier New', monospace; 
            font-weight: bold; margin-top: 25px; letter-spacing: 8px; 
            font-size: 1.1rem; text-transform: uppercase;
            text-shadow: 0 0 10px #00f2ff;
        }

        /* WINDOW INTERFACE */
        .window {
            background: rgba(5, 7, 12, 0.98) !important;
            backdrop-filter: blur(50px);
            border: 2px solid rgba(0, 242, 255, 0.25);
            border-radius: 40px;
            padding: 50px;
            box-shadow: 0 50px 150px rgba(0,0,0,1);
        }
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<h1 class='pro-title'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:15px; opacity:0.6; margin-bottom:80px;'>CORE_SYSTEM_ACTIVE_V4</p>", unsafe_allow_html=True)
    
    _, c1, c2, c3, c4, _ = st.columns([0.1, 1, 1, 1, 1, 0.1])
    
    with c1:
        if st.button("🌌", key="s"): 
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()
        st.markdown('<p class="label">Synth</p>', unsafe_allow_html=True)

    with c2:
        if st.button("🧬", key="a"): 
            st.session_state.active_window = "AUDIO"
            st.rerun()
        st.markdown('<p class="label">Audio</p>', unsafe_allow_html=True)

    with c3:
        if st.button("🛰️", key="v"): 
            st.session_state.active_window = "VIDEO"
            st.rerun()
        st.markdown('<p class="label">Video</p>', unsafe_allow_html=True)

    with c4:
        if st.button("💎", key="sys"): 
            st.session_state.active_window = "SYSTEM"
            st.rerun()
        st.markdown('<p class="label">System</p>', unsafe_allow_html=True)

# --- 4. WINDOW MANAGER ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.1, 1, 0.1])
    
    with win_col:
        st.markdown('<div class="window">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:#00f2ff; font-size:2.8rem; font-family:monospace;'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:1px solid rgba(0,242,255,0.15); margin:30px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            p = st.text_area("MATRIX COMMAND:", height=150)
            if st.button("EXECUTE", use_container_width=True):
                with st.status("PROCESSING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res: st.image(st.session_state.synth_res, use_container_width=True)

        elif st.session_state.active_window == "AUDIO":
            p = st.text_input("SONIC PARAMETERS:")
            if st.button("GENERATE", use_container_width=True):
                with st.status("TUNING..."):
                    res = replicate.run("facebookresearch/musicgen:7b57424c30623a3111867c006579c3b88d2f1f0a204364ef0c6e93833f48a901", input={"prompt": p})
                    st.session_state.audio_res = res
                st.rerun()
            if st.session_state.audio_res: st.audio(st.session_state.audio_res)

        elif st.session_state.active_window == "SYSTEM":
            st.metric("CORE STATUS", "NOMINAL", "ACTIVE")
            st.code("MAXIMUSIK AI OS\nBUILD: 4.0.0\nENCRYPTION: QUANTUM-SECURED")
            if st.button("PURGE_CACHE", use_container_width=True):
                st.session_state.synth_res = None
                st.session_state.audio_res = None
                st.success("CACHE PURGED")

        st.markdown('</div>', unsafe_allow_html=True)












