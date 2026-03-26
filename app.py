import streamlit as st
import replicate
import os

# --- 1. CONFIG ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

# API Setup
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session State Init
if "active_window" not in st.session_state: st.session_state.active_window = None
if "synth_res" not in st.session_state: st.session_state.synth_res = None
if "audio_res" not in st.session_state: st.session_state.audio_res = None
if "video_res" not in st.session_state: st.session_state.video_res = None

# --- 2. DESIGN (CSS) ---
def apply_ui():
    st.markdown("""
        <style>
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }

        /* MEGA-IKONER */
        div.stButton > button {
            display: block; margin: 0 auto;
            width: 160px !important; height: 160px !important;
            border-radius: 30px !important;
            border: 2px solid rgba(0, 242, 255, 0.2) !important;
            background-size: cover !important;
            background-position: center !important;
            color: transparent !important;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        }
        div.stButton > button:hover {
            transform: scale(1.15) rotate(2deg) !important;
            border-color: #00f2ff !important;
            box-shadow: 0 0 50px rgba(0, 242, 255, 0.4) !important;
        }

        /* IKON-BILDER */
        div.stButton > button[key="s"] { background-image: url('https://images.unsplash.com') !important; }
        div.stButton > button[key="a"] { background-image: url('https://images.unsplash.com') !important; }
        div.stButton > button[key="v"] { background-image: url('https://images.unsplash.com') !important; }
        div.stButton > button[key="sys"] { background-image: url('https://images.unsplash.com') !important; }

        .label { text-align: center; color: #00f2ff; font-family: 'Courier New', monospace; font-weight: bold; margin-top: 15px; letter-spacing: 3px; font-size: 0.8rem; text-shadow: 0 0 10px #00f2ff; }

        /* FÖNSTER-DESIGN */
        .window {
            background: rgba(10, 10, 15, 0.95) !important;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 242, 255, 0.4);
            border-radius: 30px;
            padding: 35px;
            color: white;
            box-shadow: 0 20px 80px rgba(0,0,0,0.8);
            animation: fadeIn 0.4s ease-out;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP INTERFACE ---
if st.session_state.active_window is None:
    st.markdown("<br><br><br><h1 style='text-align:center; color:white; font-size:5rem; font-weight:900; letter-spacing:-2px; margin-bottom:0;'>MAXIMUS<span style='color:#00f2ff;'>IKAI</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:12px; margin-top:0; opacity:0.8;'>QUAD_CORE_OS_V2.0.4</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, c1, c2, c3, c4, _ = st.columns([0.5, 1, 1, 1, 1, 0.5])
    
    with c1:
        if st.button(".", key="s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()
        st.markdown('<p class="label">SYNTHESIS</p>', unsafe_allow_html=True)

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

# --- 4. WINDOW MANAGER ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.15, 1, 0.15])
    
    with win_col:
        st.markdown('<div class="window">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:#00f2ff; margin:0; font-family:monospace;'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid rgba(0,242,255,0.2); margin:25px 0;'>", unsafe_allow_html=True)

        # -- MODUL: SYNTHESIS --
        if st.session_state.active_window == "SYNTHESIS":
            prompt = st.text_area("VAD SKA VISUALISERAS?", placeholder="En neonbelyst cyberpunk-stad i regnet...")
            if st.button("EXEKVERA GENERERING", use_container_width=True):
                with st.status("PROCESSAR MATRIS..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res:
                st.image(st.session_state.synth_res, caption="GENERERAD DATA", use_container_width=True)

        # -- MODUL: AUDIO --
        elif st.session_state.active_window == "AUDIO":
            st.write("SKAPA LJUDVÅGOR VIA AI")
            a_prompt = st.text_input("BESKRIV LJUD/MUSIK:", placeholder="Cyberpunk techno, 120bpm, dark synth")
            if st.button("KOMPONERA", use_container_width=True):
                with st.status("SYNTETISERAR LJUD..."):
                    # Använder MusicGen
                    res = replicate.run("facebookresearch/musicgen:7a76a8258a23faac443f1165275e01668e64dc93e430d4375b42d7658742b71d", 
                                        input={"prompt": a_prompt, "duration": 8})
                    st.session_state.audio_res = res
                st.rerun()
            if st.session_state.audio_res:
                st.audio(st.session_state.audio_res)

        # -- MODUL: VIDEO --
        elif st.session_state.active_window == "VIDEO":
            st.write("GENERERA RÖRELSEDATA")
            v_prompt = st.text_input("BESKRIV FILMEN:")
            if st.button("RENDERA VIDEO", use_container_width=True):
                with st.status("RENDERAR..."):
                    # Använder Luma Dream Machine eller liknande
                    res = replicate.run("lucataco/luma-dream-machine", 
                                        input={"prompt": v_prompt})
                    st.session_state.video_res = res
                st.rerun()
            if st.session_state.video_res:
                st.video(st.session_state.video_res)

        # -- MODUL: SYSTEM --
        elif st.session_state.active_window == "SYSTEM":
            st.code("""
            STATUS: ACTIVE
            UPLINK: SECURED
            KERNEL: V2.0.4-AURORA
            MEMORY_LOAD: NOMINAL
            """)
            if st.button("CLEAR ALL CACHE", use_container_width=True):
                st.session_state.synth_res = None
                st.session_state.audio_res = None
                st.session_state.video_res = None
                st.success("CACHE RENSAD")

        st.markdown('</div>', unsafe_allow_html=True)















