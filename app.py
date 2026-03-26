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
        /* Mörk sci-fi bakgrund */
        .stAppViewContainer {
            background-color: #020205 !important;
            background-image: radial-gradient(circle at 50% 50%, #001a2d 0%, #020205 100%) !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }

        /* NEON-KNAPPAR MED EMOJIS */
        div[data-testid="stButton"] > button {
            display: block !important;
            margin: 0 auto !important;
            width: 160px !important;
            height: 160px !important;
            border-radius: 35px !important;
            border: 2px solid rgba(0, 242, 255, 0.2) !important;
            background: rgba(255, 255, 255, 0.03) !important;
            font-size: 4rem !important;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
        }
        
        div[data-testid="stButton"] > button:hover {
            transform: scale(1.1) translateY(-10px) !important;
            border-color: #00f2ff !important;
            background: rgba(0, 242, 255, 0.08) !important;
            box-shadow: 0 0 40px rgba(0, 242, 255, 0.4) !important;
        }

        /* TITEL DESIGN */
        .pro-title {
            text-align: center; color: white; font-size: 5rem; font-weight: 900; 
            letter-spacing: -2px; margin-bottom: 0;
            background: linear-gradient(to bottom, #ffffff 40%, #00f2ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 15px rgba(0, 242, 255, 0.2));
        }
        .label { 
            text-align: center; color: #00f2ff; font-family: monospace; 
            font-weight: bold; margin-top: 15px; letter-spacing: 5px; 
            font-size: 0.8rem; text-transform: uppercase;
        }

        /* WINDOW INTERFACE */
        .window {
            background: rgba(5, 7, 10, 0.98) !important;
            backdrop-filter: blur(30px);
            border: 1px solid rgba(0, 242, 255, 0.2);
            border-radius: 30px;
            padding: 40px;
            color: #e0e0e0;
            box-shadow: 0 40px 100px rgba(0,0,0,1);
        }
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 class='pro-title'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:12px; opacity:0.4;'>NEURAL_OS_READY</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, c1, c2, c3, c4, _ = st.columns([0.5, 1, 1, 1, 1, 0.5])
    
    with c1:
        if st.button("🌌", key="s"): 
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()
        st.markdown('<p class="label">Synthesis</p>', unsafe_allow_html=True)

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
    _, win_col, _ = st.columns([0.15, 1, 0.15])
    
    with win_col:
        st.markdown('<div class="window">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:#00f2ff; margin:0; font-family:monospace;'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid rgba(0,242,255,0.1); margin:25px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            p = st.text_area("VAD SKALL SKAPAS?")
            if st.button("EXECUTE"):
                with st.status("WORKING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res: st.image(st.session_state.synth_res)

        elif st.session_state.active_window == "AUDIO":
            p = st.text_input("BESKRIV LJUDVÅG:")
            if st.button("GENERATE"):
                with st.status("TUNING..."):
                    res = replicate.run("facebookresearch/musicgen:7b57424c30623a3111867c006579c3b88d2f1f0a204364ef0c6e93833f48a901", input={"prompt": p})
                    st.session_state.audio_res = res
                st.rerun()
            if st.session_state.audio_res: st.audio(st.session_state.audio_res)

        elif st.session_state.active_window == "SYSTEM":
            st.code("STATUS: NOMINAL\nUPLINK: ENCRYPTED\nKERNEL: V2.5")
            if st.button("PURGE ALL DATA", use_container_width=True):
                st.session_state.synth_res = None
                st.session_state.audio_res = None
                st.success("CLEARED")

        st.markdown('</div>', unsafe_allow_html=True)











