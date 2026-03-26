import streamlit as st
import replicate
import os

# --- 1. SYSTEMKONFIGURATION ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None
if "last_audio" not in st.session_state: st.session_state.last_audio = None

# --- 2. DESIGN (CSS) ---
def apply_space_ui():
    st.markdown("""
        <style>
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }
        
        /* EXTRA STORA GLAS-BOXAR FÖR IKONER */
        [data-testid="stVerticalBlock"] > div:has(div.mega-icon) {
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(25px);
            border-radius: 40px;
            border: 2px solid rgba(0, 242, 255, 0.4);
            padding: 35px; /* Mer luft inuti */
            transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            text-align: center;
            box-shadow: 0 25px 60px rgba(0,0,0,0.8);
        }
        
        [data-testid="stVerticalBlock"] > div:has(div.mega-icon):hover {
            border-color: #00f2ff;
            transform: scale(1.03) translateY(-15px);
            box-shadow: 0 0 50px rgba(0, 242, 255, 0.4);
        }

        .window-pane {
            background: rgba(0, 0, 0, 0.95) !important;
            backdrop-filter: blur(50px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 45px;
            padding: 50px;
            box-shadow: 0 0 150px rgba(0,0,0,1);
            color: white;
        }
        
        .stButton > button {
            width: 100% !important;
            height: 60px !important; /* Större knapp */
            background: rgba(0, 242, 255, 0.15) !important;
            color: #00f2ff !important;
            border: 1px solid #00f2ff !important;
            border-radius: 20px !important;
            font-size: 18px !important;
            font-weight: 900 !important;
            letter-spacing: 3px !important;
            margin-top: 20px !important;
        }
        .stButton > button:hover {
            background: #00f2ff !important;
            color: black !important;
            box-shadow: 0 0 20px #00f2ff;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY (IKONER) ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:6rem; font-weight:900;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:20px; margin-bottom:60px;'>MEGA_CORE_V10</p>", unsafe_allow_html=True)
    
    # Justerat kolumnbredd för att göra dem maffigare
    _, col1, col2, col3, _ = st.columns([0.1, 1, 1, 1, 0.1])
    
    with col1:
        st.markdown('<div class="mega-icon"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", use_container_width=True)
        if st.button("SYNTHESIS", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with col2:
        st.markdown('<div class="mega-icon"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", use_container_width=True)
        if st.button("AUDIO", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with col3:
        st.markdown('<div class="mega-icon"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", use_container_width=True)
        if st.button("VIDEO", key="btn_v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()

# --- 4. FÖNSTER-VY (MODULER) ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.05, 1, 0.05])
    
    with win_col:
        st.markdown('<div class="window-pane">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:white; margin:0;'>🗔 {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✖", key="exit"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid rgba(0,242,255,0.2); margin:25px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            st.subheader("🎨 Bild-generator")
            p = st.text_area("VAD VILL DU SKAPA?")
            if st.button("GENERA"):
                with st.spinner("Beräknar..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_res = res
                st.rerun()
            if st.session_state.last_res: st.image(st.session_state.last_res, use_container_width=True)

        elif st.session_state.active_window == "AUDIO":
            st.subheader("🎵 Musik-kompositör")
            ap = st.text_area("BESKRIV MUSIKEN")
            if st.button("SKAPA"):
                with st.spinner("Komponerar..."):
                    res = replicate.run("meta/musicgen:671ac645cf51591bc3754da5ff3f4523d44373308dfc9496883cd2050119e8de", input={"prompt": ap})
                    st.session_state.last_audio = res
                st.rerun()
            if st.session_state.last_audio: st.audio(st.session_state.last_audio)

        elif st.session_state.active_window == "VIDEO":
            st.subheader("🎬 Video-modul")
            st.video("https://www.w3schools.com")

        st.markdown('</div>', unsafe_allow_html=True)









