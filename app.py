import streamlit as st
import replicate
import os

# --- 1. SYSTEMKONFIGURATION ---
st.set_page_config(page_title="MAXIMUS_OS_2026", layout="wide", initial_sidebar_state="collapsed")

# API-nyckel hantering
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# State-hantering för navigering och resultat
if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None
if "last_audio" not in st.session_state: st.session_state.last_audio = None

# --- 2. DESIGN (CSS) ---
def apply_space_ui():
    st.markdown("""
        <style>
        /* RYMDBAKGRUND 2026 */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }
        
        /* KVADRATISKA MEGA-IKONER */
        [data-testid="stVerticalBlock"] > div:has(div.square-icon) {
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(30px);
            border-radius: 40px;
            border: 2px solid rgba(0, 242, 255, 0.4);
            padding: 30px;
            transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            text-align: center;
            aspect-ratio: 1 / 1; /* Tvingar fram kvadratisk form */
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 30px 70px rgba(0,0,0,0.8);
        }
        
        [data-testid="stVerticalBlock"] > div:has(div.square-icon):hover {
            border-color: #00f2ff;
            transform: scale(1.05) translateY(-10px);
            box-shadow: 0 0 60px rgba(0, 242, 255, 0.5);
        }

        /* Bild-styling inuti kvadraten */
        .stImage img {
            border-radius: 25px;
            object-fit: cover;
            aspect-ratio: 1 / 1;
            border: 1px solid rgba(255,255,255,0.1);
        }

        /* FÖNSTER GLASSMORPHISM */
        .window-pane {
            background: rgba(0, 0, 0, 0.95) !important;
            backdrop-filter: blur(60px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 50px;
            padding: 60px;
            color: white;
            box-shadow: 0 0 150px rgba(0,0,0,1);
        }
        
        /* STYLA KNAPPARNA */
        .stButton > button {
            width: 100% !important;
            height: 60px !important;
            background: rgba(0, 242, 255, 0.15) !important;
            color: #00f2ff !important;
            border: 2px solid #00f2ff !important;
            border-radius: 20px !important;
            font-weight: 900 !important;
            font-size: 18px !important;
            letter-spacing: 3px !important;
            margin-top: 20px !important;
            transition: 0.3s;
        }
        .stButton > button:hover {
            background: #00f2ff !important;
            color: black !important;
            box-shadow: 0 0 30px #00f2ff;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY (START) ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:7rem; font-weight:900;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:25px; margin-bottom:80px;'>ULTRA_CORE_2026</p>", unsafe_allow_html=True)
    
    # Justerat kolumnbredd för de stora kvadraterna
    _, col1, col2, col3, _ = st.columns([0.15, 1, 1, 1, 0.15])
    
    with col1:
        st.markdown('<div class="square-icon"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", use_container_width=True)
        if st.button("SYNTHESIS", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with col2:
        st.markdown('<div class="square-icon"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", use_container_width=True)
        if st.button("AUDIO", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with col3:
        st.markdown('<div class="square-icon"></div>', unsafe_allow_html=True)
        st.image("https://images.unsplash.com", use_container_width=True)
        if st.button("VIDEO", key="btn_v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()

# --- 4. FÖNSTER-VY (INNEHÅLL) ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.05, 1, 0.05])
    
    with win_col:
        st.markdown('<div class="window-pane">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h1 style='color:white; margin:0;'>🗔 {st.session_state.active_window}</h1>", unsafe_allow_html=True)
        if h2.button("✖", key="exit"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid rgba(0,242,255,0.2); margin:30px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            st.subheader("🎨 AI Bild-generator (FLUX_SCHNELL)")
            p = st.text_area("VAD VILL DU GENERERA?", placeholder="En rymd-skog i neon...")
            if st.button("STARTA GENERERING"):
                with st.spinner("Beräknar pixlar..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_res = res
                st.rerun()
            if st.session_state.last_res: st.image(st.session_state.last_res, use_container_width=True)

        elif st.session_state.active_window == "AUDIO":
            st.subheader("🎵 AI Musik-kompositör (MusicGen)")
            ap = st.text_area("BESKRIV DIN LÅT", placeholder="Ambient space music with deep bass...")
            if st.button("KOMPONERA"):
                with st.spinner("Skapar ljudvågor..."):
                    res = replicate.run("meta/musicgen:671ac645cf51591bc3754da5ff3f4523d44373308dfc9496883cd2050119e8de", input={"prompt": ap})
                    st.session_state.last_audio = res
                st.rerun()
            if st.session_state.last_audio: st.audio(st.session_state.last_audio)

        elif st.session_state.active_window == "VIDEO":
            st.subheader("🎬 AI Video-modul")
            st.info("Kopplar upp mot Stable Video Diffusion...")
            st.video("https://www.w3schools.com")

        st.markdown('</div>', unsafe_allow_html=True)









