import streamlit as st
import replicate
import os

# --- 1. CONFIG ---
st.set_page_config(page_title="MAXIMUSIK AI SPACE", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session State
if "active_window" not in st.session_state: st.session_state.active_window = None
if "synth_res" not in st.session_state: st.session_state.synth_res = None

# --- 2. DESIGN (CSS) ---
def apply_ui():
    st.markdown("""
        <style>
        /* RYMD-BAKGRUND */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }

        /* KNAPPAR FASTLÅSTA PÅ 200PX MED GIGANTISKA EMOJIS */
        div[data-testid="stButton"] > button {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 auto !important;
            width: 200px !important; 
            height: 200px !important;
            border-radius: 50px !important;
            border: 2px solid rgba(255, 255, 255, 0.2) !important;
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px) !important;
            font-size: 8rem !important; /* GIGANTISK EMOJI INUTI 200PX */
            padding: 0 !important;
            overflow: visible !important; /* Låter emojin "poppa" */
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 15px 50px rgba(0,0,0,0.8) !important;
        }
        
        div[data-testid="stButton"] > button:hover {
            transform: scale(1.1) translateY(-10px) !important;
            border-color: #00f2ff !important;
            background: rgba(0, 242, 255, 0.1) !important;
            box-shadow: 0 0 70px rgba(0, 242, 255, 0.4) !important;
        }

        /* TITEL */
        .space-title {
            text-align: center; color: white; font-size: 6rem; font-weight: 900; 
            letter-spacing: -3px; margin-top: 50px;
            text-shadow: 0 0 30px rgba(0, 242, 255, 0.5);
        }
        .label { 
            text-align: center; color: #00f2ff; font-family: monospace; 
            font-weight: bold; margin-top: 25px; letter-spacing: 10px; 
            font-size: 1.2rem; text-transform: uppercase;
        }

        /* WINDOW INTERFACE */
        .window {
            background: rgba(0, 5, 15, 0.98) !important;
            backdrop-filter: blur(50px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 40px;
            padding: 50px;
            box-shadow: 0 0 100px rgba(0,0,0,1);
        }
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<h1 class='space-title'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:15px; opacity:0.6; margin-bottom:100px;'>SPACE_CORE_V5</p>", unsafe_allow_html=True)
    
    _, c1, c2, c3, c4, _ = st.columns([0.1, 1, 1, 1, 1, 0.1])
    
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
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:white; font-size:3rem; font-family:monospace;'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:1px solid rgba(255,255,255,0.1); margin:30px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            p = st.text_area("COMMAND:", height=150)
            if st.button("GENERATE", use_container_width=True):
                with st.status("PROCESSING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res: st.image(st.session_state.synth_res, use_container_width=True)

        elif st.session_state.active_window == "SYSTEM":
            st.write("SIGNAL STATUS: MAXIMUM")
            if st.button("PURGE CACHE", use_container_width=True):
                st.session_state.synth_res = None
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)














