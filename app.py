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
            background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }
        
        /* DESKTOP-IKONER */
        .desktop-icon {
            background-size: cover; background-position: center;
            border: 2px solid rgba(0, 242, 255, 0.4); border-radius: 30px;
            height: 320px; display: flex; flex-direction: column;
            justify-content: flex-end; transition: 0.5s ease;
            box-shadow: 0 20px 50px rgba(0,0,0,0.8);
            position: relative; overflow: hidden;
            pointer-events: none; /* Låter knappen under ta emot klicket */
        }
        
        /* SYNLIG TEXT PÅ IKONEN */
        .icon-label {
            background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(15px);
            width: 100%; text-align: center; padding: 20px 0;
            color: #00f2ff; font-family: monospace; font-weight: 900;
            letter-spacing: 5px; font-size: 20px; border-top: 1px solid rgba(0, 242, 255, 0.2);
        }

        /* FIX FÖR ATT GÖRA STREAMLIT-KNAPPEN OSYNLIG MEN KLICKBAR */
        div[data-testid="stColumn"] {
            position: relative;
        }
        .stButton button {
            position: absolute;
            top: 0; left: 0;
            width: 100%;
            height: 320px; /* Samma som ikonens höjd */
            background: transparent !important;
            border: none !important;
            color: transparent !important;
            z-index: 100;
            cursor: pointer;
        }
        .stButton button:hover {
            background: rgba(0, 242, 255, 0.1) !important;
        }
        
        .window-pane {
            background: rgba(0, 0, 0, 0.95) !important; backdrop-filter: blur(40px);
            border: 1px solid rgba(0, 242, 255, 0.3); border-radius: 40px;
            padding: 50px; box-shadow: 0 0 120px rgba(0,0,0,1); color: white;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:6rem; font-weight:900;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:15px; margin-bottom:80px;'>CORE_V7_STABLE</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="desktop-icon" style="background-image: url(\'https://images.unsplash.com\');"><div class="icon-label">SYNTHESIS</div></div>', unsafe_allow_html=True)
        if st.button("OPEN_S", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with col2:
        st.markdown('<div class="desktop-icon" style="background-image: url(\'https://images.unsplash.com\');"><div class="icon-label">AUDIO</div></div>', unsafe_allow_html=True)
        if st.button("OPEN_A", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with col3:
        st.markdown('<div class="desktop-icon" style="background-image: url(\'https://images.unsplash.com\');"><div class="icon-label">VIDEO</div></div>', unsafe_allow_html=True)
        if st.button("OPEN_V", key="btn_v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()

# --- 4. FÖNSTER-VY ---
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
            c1, c2 = st.columns(2)
            with c1:
                p = st.text_area("VAD VILL DU GENERERA?")
                if st.button("STARTA GENERERING", use_container_width=True):
                    with st.spinner("Skapar bild..."):
                        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                        st.session_state.last_res = res
                    st.rerun()
            with c2:
                if st.session_state.last_res: st.image(st.session_state.last_res, use_container_width=True)

        elif st.session_state.active_window == "AUDIO":
            st.subheader("🎵 Musik-kompositör")
            ap = st.text_area("BESKRIV MUSIKEN")
            if st.button("KOMPONERA", use_container_width=True):
                with st.spinner("Komponerar musik..."):
                    res = replicate.run("meta/musicgen:671ac645cf51591bc3754da5ff3f4523d44373308dfc9496883cd2050119e8de", input={"prompt": ap})
                    st.session_state.last_audio = res
                st.rerun()
            if st.session_state.last_audio: st.audio(st.session_state.last_audio)

        elif st.session_state.active_window == "VIDEO":
            st.subheader("🎬 Video-modul")
            st.video("https://www.w3schools.com")

        st.markdown('</div>', unsafe_allow_html=True)







