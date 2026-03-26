import streamlit as st
import replicate
import os

# --- 1. CONFIG ---
st.set_page_config(page_title="MAXIMUSIK AI", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

if "active_window" not in st.session_state: st.session_state.active_window = None
if "synth_res" not in st.session_state: st.session_state.synth_res = None
if "audio_res" not in st.session_state: st.session_state.audio_res = None
if "video_res" not in st.session_state: st.session_state.video_res = None

# --- 2. DESIGN (CSS) ---
def apply_ui():
    st.markdown("""
        <style>
        /* Bakgrund */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.95)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }

        /* MEGA-IKONER (Här fixas bilderna) */
        div.stButton > button {
            display: block; margin: 0 auto;
            width: 160px !important; height: 160px !important;
            border-radius: 35px !important;
            border: 2px solid rgba(0, 242, 255, 0.3) !important;
            background-size: cover !important;
            background-position: center !important;
            color: transparent !important; /* Döljer Streamlits text i knappen */
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        }
        
        div.stButton > button:hover {
            transform: scale(1.1) translateY(-10px) !important;
            border-color: #00f2ff !important;
            box-shadow: 0 0 40px rgba(0, 242, 255, 0.6) !important;
        }

        /* SPECIFIKA BILDER FÖR VARJE KEY */
        div.stButton > button[key="s"] { background-image: url('https://images.unsplash.com') !important; }
        div.stButton > button[key="a"] { background-image: url('https://images.unsplash.com') !important; }
        div.stButton > button[key="v"] { background-image: url('https://images.unsplash.com') !important; }
        div.stButton > button[key="sys"] { background-image: url('https://images.unsplash.com') !important; }

        .label { text-align: center; color: #00f2ff; font-family: monospace; font-weight: bold; margin-top: 12px; letter-spacing: 3px; font-size: 0.85rem; text-shadow: 0 0 8px #00f2ff; }

        /* FÖNSTER */
        .window {
            background: rgba(5, 5, 10, 0.95) !important;
            backdrop-filter: blur(30px);
            border: 1px solid rgba(0, 242, 255, 0.4);
            border-radius: 40px;
            padding: 40px;
            color: white;
            box-shadow: 0 30px 100px rgba(0,0,0,0.9);
        }
        
        /* LOGGA ANIMATION */
        .glitch {
            text-align:center; color:white; font-size:5rem; font-weight:900; 
            letter-spacing:-2px; margin-bottom:0;
            text-shadow: 2px 2px #ff00ff, -2px -2px #00ffff;
        }
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 class='glitch'>MAXIMUSIK <span style='color:#00f2ff;'>AI</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:10px; opacity:0.6;'>QUAD_CORE_OS_V2</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, c1, c2, c3, c4, _ = st.columns([0.5, 1, 1, 1, 1, 0.5])
    
    with c1:
        if st.button(" ", key="s"): st.session_state.active_window = "SYNTHESIS"; st.rerun()
        st.markdown('<p class="label">SYNTHESIS</p>', unsafe_allow_html=True)
    with c2:
        if st.button(" ", key="a"): st.session_state.active_window = "AUDIO"; st.rerun()
        st.markdown('<p class="label">AUDIO</p>', unsafe_allow_html=True)
    with c3:
        if st.button(" ", key="v"): st.session_state.active_window = "VIDEO"; st.rerun()
        st.markdown('<p class="label">VIDEO</p>', unsafe_allow_html=True)
    with c4:
        if st.button(" ", key="sys"): st.session_state.active_window = "SYSTEM"; st.rerun()
        st.markdown('<p class="label">SYSTEM</p>', unsafe_allow_html=True)

# --- 4. WINDOW MANAGER ---
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
        
        st.markdown("<hr style='border:0.5px solid #222; margin:25px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            p = st.text_area("SKAPA VISUELL DATA:")
            if st.button("STARTA GENERERING", use_container_width=True):
                with st.status("PROCESSAR..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res: st.image(st.session_state.synth_res)

        elif st.session_state.active_window == "AUDIO":
            p = st.text_input("SKAPA LJUDVÅGOR:")
            if st.button("KOMPONERA", use_container_width=True):
                with st.status("SYNTETISERAR..."):
                    res = replicate.run("facebookresearch/musicgen:7b57424c30623a3111867c006579c3b88d2f1f0a204364ef0c6e93833f48a901", input={"prompt": p})
                    st.session_state.audio_res = res
                st.rerun()
            if st.session_state.audio_res: st.audio(st.session_state.audio_res)

        elif st.session_state.active_window == "VIDEO":
            p = st.text_input("SKAPA RÖRELSE:")
            if st.button("RENDERA", use_container_width=True):
                with st.status("RENDERAR..."):
                    res = replicate.run("lucataco/luma-dream-machine", input={"prompt": p})
                    st.session_state.video_res = res
                st.rerun()
            if st.session_state.video_res: st.video(st.session_state.video_res)

        elif st.session_state.active_window == "SYSTEM":
            st.code("STATUS: ONLINE\nOS: MAXIMUSIK AI\nCACHED_FILES: ENABLED")
            if st.button("PURGE CACHE", use_container_width=True):
                st.session_state.synth_res = st.session_state.audio_res = st.session_state.video_res = None
                st.success("CACHE RENSAD")

        st.markdown('</div>', unsafe_allow_html=True)






