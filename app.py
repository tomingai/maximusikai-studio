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
        /* BAKGRUND */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }
        
        /* GLAS-CONTAINER FÖR IKONER */
        [data-testid="stVerticalBlock"] > div:has(div.icon-box) {
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(15px);
            border-radius: 30px;
            border: 1px solid rgba(0, 242, 255, 0.3);
            padding: 20px;
            transition: 0.3s;
            text-align: center;
        }

        /* FÖNSTER */
        .window-pane {
            background: rgba(0, 0, 0, 0.9) !important;
            backdrop-filter: blur(40px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 40px;
            padding: 40px;
            box-shadow: 0 0 100px rgba(0,0,0,1);
            color: white;
        }
        
        /* STYLA KNAPPARNA */
        .stButton > button {
            width: 100% !important;
            background: rgba(0, 242, 255, 0.1) !important;
            color: #00f2ff !important;
            border: 1px solid #00f2ff !important;
            font-weight: bold !important;
            letter-spacing: 2px !important;
            text-transform: uppercase !important;
        }
        .stButton > button:hover {
            background: #00f2ff !important;
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:5rem; font-weight:900;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:15px; margin-bottom:50px;'>STABLE_OS_V8</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="icon-box"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", use_container_width=True)
        if st.button("ÖPPNA SYNTHESIS", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with col2:
        st.markdown('<div class="icon-box"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", use_container_width=True)
        if st.button("ÖPPNA AUDIO", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with col3:
        st.markdown('<div class="icon-box"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", use_container_width=True)
        if st.button("ÖPPNA VIDEO", key="btn_v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()

# --- 4. FÖNSTER-VY ---
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
        
        st.markdown("<hr style='border:0.5px solid rgba(0,242,255,0.2); margin:20px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            st.subheader("🎨 Bild-generator")
            p = st.text_area("VAD SKALL SKAPAS?")
            if st.button("GENERA BILD"):
                with st.spinner("Skapar..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_res = res
                st.rerun()
            if st.session_state.last_res: st.image(st.session_state.last_res)

        elif st.session_state.active_window == "AUDIO":
            st.subheader("🎵 Musik-kompositör")
            ap = st.text_area("BESKRIV MUSIKEN")
            if st.button("SKAPA MUSIK"):
                with st.spinner("Komponerar..."):
                    res = replicate.run("meta/musicgen:671ac645cf51591bc3754da5ff3f4523d44373308dfc9496883cd2050119e8de", input={"prompt": ap})
                    st.session_state.last_audio = res
                st.rerun()
            if st.session_state.last_audio: st.audio(st.session_state.last_audio)

        elif st.session_state.active_window == "VIDEO":
            st.subheader("🎬 Video-modul")
            st.video("https://www.w3schools.com")

        st.markdown('</div>', unsafe_allow_html=True)








