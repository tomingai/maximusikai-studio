import streamlit as st
import replicate
import os

# --- 1. CONFIG ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None

# --- 2. DESIGN ---
def apply_ui():
    st.markdown("""
        <style>
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }

        /* MEGA-IKONER (160px) */
        div.stButton > button {
            display: block; margin: 0 auto;
            width: 160px !important; height: 160px !important;
            border-radius: 30px !important;
            border: 2px solid rgba(0, 242, 255, 0.4) !important;
            background-size: cover !important;
            background-position: center !important;
            color: transparent !important;
            transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        }
        div.stButton > button:hover {
            transform: scale(1.1) translateY(-10px) !important;
            border-color: #00f2ff !important;
            box-shadow: 0 0 40px rgba(0, 242, 255, 0.5) !important;
        }

        /* BILDER SOM BESKRIVER FUNKTIONERNA */
        /* Synthesis - En färgstark AI-art bild */
        div.stButton > button[key="s"] { background-image: url('https://images.unsplash.com') !important; }
        /* Audio - En snygg equalizer/ljudvåg */
        div.stButton > button[key="a"] { background-image: url('https://images.unsplash.com') !important; }
        /* Video - En filmscen/klappa */
        div.stButton > button[key="v"] { background-image: url('https://images.unsplash.com') !important; }
        /* System - Kugghjul/Kretskort */
        div.stButton > button[key="sys"] { background-image: url('https://images.unsplash.com') !important; }

        .label { text-align: center; color: #00f2ff; font-family: monospace; font-weight: bold; margin-top: 10px; letter-spacing: 2px; font-size: 0.9rem; }

        .window {
            background: rgba(0, 0, 0, 0.9) !important;
            backdrop-filter: blur(40px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 40px;
            padding: 40px;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:4rem; font-weight:900;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:10px;'>QUAD_CORE_OS_V2</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, c1, c2, c3, c4, _ = st.columns([0.5, 1, 1, 1, 1, 0.5])
    
    with c1:
        if st.button(".", key="s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()
        st.markdown('<p class="label">SYNTH</p>', unsafe_allow_html=True)

    with c2:
        if st.button(".", key="a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()
        st.markdown('<p class="label">AUDIO</p>', unsafe_allow_html=True)

    with c3:
        if st.button(".", key="v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()
        st.markdown('<p class="label">VIDEO</p>', unsafe_allow_html=True)

    with c4:
        if st.button(".", key="sys"):
            st.session_state.active_window = "SYSTEM"
            st.rerun()
        st.markdown('<p class="label">SYSTEM</p>', unsafe_allow_html=True)

# --- 4. WINDOWS ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.1, 1, 0.1])
    
    with win_col:
        st.markdown('<div class="window">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:white; margin:0;'>🗔 {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✖", key="close"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid #222; margin:20px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            p = st.text_area("VAD VILL DU SKAPA?")
            if st.button("GENERA BILD", use_container_width=True):
                with st.status("SKAPAR..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_res = res
                st.rerun()
            if st.session_state.last_res:
                st.image(st.session_state.last_res, use_container_width=True)

        elif st.session_state.active_window == "SYSTEM":
            st.write("### Status: Online")
            st.info("CPU: Optimal | RAM: Stable")

        elif st.session_state.active_window == "AUDIO":
            st.info("AUDIO MODULE READY.")

        elif st.session_state.active_window == "VIDEO":
            st.info("VIDEO MODULE READY.")

        st.markdown('</div>', unsafe_allow_html=True)















