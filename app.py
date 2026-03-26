import streamlit as st
import replicate
import os

# --- 1. SYSTEMKONFIGURATION ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

# API-nyckel hantering
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# State-hantering
if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None
if "last_audio" not in st.session_state: st.session_state.last_audio = None

# --- 2. DESIGN (CSS) ---
def apply_space_ui():
    st.markdown("""
        <style>
        /* RYMDBAKGRUND */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }
        
        /* GLAS-BOX FÖR IKONER */
        [data-testid="stVerticalBlock"] > div:has(div.icon-container) {
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(20px);
            border-radius: 35px;
            border: 1px solid rgba(0, 242, 255, 0.3);
            padding: 25px;
            transition: 0.4s;
            text-align: center;
            box-shadow: 0 15px 45px rgba(0,0,0,0.5);
        }
        
        [data-testid="stVerticalBlock"] > div:has(div.icon-container):hover {
            border-color: #00f2ff;
            transform: translateY(-10px);
            box-shadow: 0 0 40px rgba(0, 242, 255, 0.3);
        }

        /* FÖNSTER (GLASSMORPHISM) */
        .window-pane {
            background: rgba(0, 0, 0, 0.92) !important;
            backdrop-filter: blur(40px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 40px;
            padding: 45px;
            box-shadow: 0 0 120px rgba(0,0,0,1);
            color: white;
        }
        
        /* KNAPP-STYLING */
        .stButton > button {
            width: 100% !important;
            background: rgba(0, 242, 255, 0.1) !important;
            color: #00f2ff !important;
            border: 1px solid #00f2ff !important;
            border-radius: 15px !important;
            font-weight: bold !important;
            padding: 10px !important;
            margin-top: 15px !important;
        }
        .stButton > button:hover {
            background: #00f2ff !important;
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY (IKONER) ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:5rem; font-weight:900;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:15px; margin-bottom:50px;'>OS_STABLE_V9</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="icon-container"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", caption="SYNTHESIS (SKOG)", use_container_width=True)
        if st.button("ÖPPNA BILDMODUL", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with col2:
        st.markdown('<div class="icon-container"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", caption="AUDIO (BERG)", use_container_width=True)
        if st.button("ÖPPNA LJUDMODUL", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with col3:
        st.markdown('<div class="icon-container"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", caption="VIDEO (SJÖ)", use_container_width=True)
        if st.button("ÖPPNA VIDEOMODUL", key="btn_v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()

# --- 4. FÖNSTER-VY (INNEHÅLL) ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.1, 1, 0.1])
    
    with win_col:
        st.markdown('<div class="window-pane">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:white; margin:0;'>🗔 {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✖", key="exit"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid rgba(0,242,255,0.2); margin:25px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            st.subheader("🎨 AI Bild-generator (Flux)")
            p = st.text_area("Beskriv din vision här...")
            if st.button("GENERA BILD"):
                with st.spinner("Beräknar pixlar..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_res = res
                st.rerun()
            if st.session_state.last_res: st.image(st.session_state.last_res, use_container_width=True)

        elif st.session_state.active_window == "AUDIO":
            st.subheader("🎵 AI Musik-kompositör (MusicGen)")
            ap = st.text_area("Beskriv musiken du vill skapa...")
            if st.button("KOMPONERA"):
                with st.spinner("Skapar ljudvågor..."):
                    res = replicate.run("meta/musicgen:671ac645cf51591bc3754da5ff3f4523d44373308dfc9496883cd2050119e8de", input={"prompt": ap})
                    st.session_state.last_audio = res
                st.rerun()
            if st.session_state.last_audio: st.audio(st.session_state.last_audio)

        elif st.session_state.active_window == "VIDEO":
            st.subheader("🎬 AI Video-modul")
            st.info("Video-generering via Stable Video Diffusion implementeras härnäst.")
            st.video("https://www.w3schools.com")

        st.markdown('</div>', unsafe_allow_html=True)








