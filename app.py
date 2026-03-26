import streamlit as st
import replicate
import os

# --- 1. CONFIG ---
st.set_page_config(page_title="MAXIMUSIK AI SPACE", layout="wide", initial_sidebar_state="collapsed")

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
        /* RYMD-BAKGRUND */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.8)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }

        /* GIGANTISKA SVÄVANDE KNAPPAR */
        div[data-testid="stButton"] > button {
            display: block !important;
            margin: 0 auto !important;
            width: 260px !important; 
            height: 260px !important;
            border-radius: 60px !important;
            border: 2px solid rgba(255, 255, 255, 0.2) !important;
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(15px) !important;
            font-size: 8rem !important; /* MAXAD STORLEK */
            line-height: 1 !important;
            transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 20px 80px rgba(0,0,0,0.8) !important;
            animation: float 6s ease-in-out infinite;
        }
        
        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
            100% { transform: translateY(0px); }
        }

        div[data-testid="stButton"] > button:hover {
            transform: scale(1.1) rotate(2deg) !important;
            border-color: #00f2ff !important;
            background: rgba(0, 242, 255, 0.1) !important;
            box-shadow: 0 0 100px rgba(0, 242, 255, 0.4) !important;
            text-shadow: 0 0 50px rgba(255,255,255,1) !important;
        }

        /* TITEL */
        .space-title {
            text-align: center; color: white; font-size: 7rem; font-weight: 900; 
            letter-spacing: -4px; margin-top: 40px; margin-bottom: 0;
            text-shadow: 0 0 40px rgba(0, 242, 255, 0.6);
        }
        .label { 
            text-align: center; color: white; font-family: 'Courier New', monospace; 
            font-weight: bold; margin-top: 30px; letter-spacing: 10px; 
            font-size: 1.2rem; text-transform: uppercase;
            text-shadow: 0 0 15px rgba(255,255,255,0.5);
        }

        /* WINDOW INTERFACE */
        .window {
            background: rgba(0, 5, 15, 0.95) !important;
            backdrop-filter: blur(60px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 50px;
            padding: 60px;
            box-shadow: 0 0 200px rgba(0,0,0,1);
        }
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<h1 class='space-title'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:20px; opacity:0.7; margin-bottom:100px;'>DEEP_SPACE_OS_V5</p>", unsafe_allow_html=True)
    
    _, c1, c2, c3, c4, _ = st.columns([0.05, 1, 1, 1, 1, 0.05])
    
    with c1:
        if st.button("🌌", key="s"): 
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()
        st.markdown('<p class="label">Synth</p>', unsafe_allow_html=True)

    with c2:
        if st.button("👽", key="a"): 
            st.session_state.active_window = "AUDIO"
            st.rerun()
        st.markdown('<p class="label">Audio</p>', unsafe_allow_html=True)

    with c3:
        if st.button("🛸", key="v"): 
            st.session_state.active_window = "VIDEO"
            st.rerun()
        st.markdown('<p class="label">Video</p>', unsafe_allow_html=True)

    with c4:
        if st.button("☄️", key="sys"): 
            st.session_state.active_window = "SYSTEM"
            st.rerun()
        st.markdown('<p class="label">System</p>', unsafe_allow_html=True)

# --- 4. WINDOW MANAGER ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.1, 1, 0.1])
    
    with win_col:
        st.markdown('<div class="window">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.95, 0.05])
        h1.markdown(f"<h2 style='color:white; font-size:3rem; font-family:monospace; letter-spacing:5px;'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:1px solid rgba(255,255,255,0.1); margin:40px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            p = st.text_area("COMMAND PROMPT:", height=150)
            if st.button("GENERATE FROM VOID", use_container_width=True):
                with st.status("COLLECTING STARDUST..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res: st.image(st.session_state.synth_res, use_container_width=True)

        elif st.session_state.active_window == "AUDIO":
            p = st.text_input("SONIC FREQUENCY:")
            if st.button("TRANSMIT", use_container_width=True):
                with st.status("VIBRATING..."):
                    res = replicate.run("facebookresearch/musicgen:7b57424c30623a3111867c006579c3b88d2f1f0a204364ef0c6e93833f48a901", input={"prompt": p})
                    st.session_state.audio_res = res
                st.rerun()
            if st.session_state.audio_res: st.audio(st.session_state.audio_res)

        elif st.session_state.active_window == "SYSTEM":
            st.metric("SIGNAL STRENGTH", "MAXIMUM", "CORE")
            st.code("MAXIMUSIK SPACE OS\nSECTOR: 7G\nSTATUS: DRIFTING")
            if st.button("CLEAR MEMORY"):
                st.session_state.synth_res = None
                st.session_state.audio_res = None
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)













