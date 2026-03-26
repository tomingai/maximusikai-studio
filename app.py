import streamlit as st
import replicate
import os

# --- 1. SYSTEMKONFIGURATION ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None

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
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }

        /* STYLA OM KNAPPARNA TILL STORA KVADRATISKA IKONER (160px) */
        div.stButton > button {
            display: block;
            margin: 0 auto;
            width: 160px !important;
            height: 160px !important;
            border-radius: 25px !important;
            border: 2px solid rgba(0, 242, 255, 0.4) !important;
            background-size: cover !important;
            background-position: center !important;
            color: transparent !important;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7) !important;
        }

        div.stButton > button:hover {
            transform: scale(1.1) translateY(-10px) !important;
            border-color: #00f2ff !important;
            box-shadow: 0 0 40px rgba(0, 242, 255, 0.5) !important;
        }

        /* SPECIFIKA BILDER FÖR VARJE MODUL */
        div.stButton > button[key="btn_s"] {
            background-image: url('https://images.unsplash.com') !important;
        }
        div.stButton > button[key="btn_a"] {
            background-image: url('https://images.unsplash.com') !important;
        }
        div.stButton > button[key="btn_v"] {
            background-image: url('https://images.unsplash.com') !important;
        }

        /* FÖNSTER (GLASSMORPHISM) */
        .window-pane {
            background: rgba(0, 0, 0, 0.9) !important;
            backdrop-filter: blur(50px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 40px;
            padding: 40px;
            color: white;
            box-shadow: 0 0 100px rgba(0,0,0,1);
        }

        .icon-text {
            text-align: center;
            color: #00f2ff;
            font-family: monospace;
            font-weight: bold;
            letter-spacing: 3px;
            margin-top: 10px;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:5rem; font-weight:900;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:15px; margin-bottom:60px;'>CORE_V14_LARGE</p>", unsafe_allow_html=True)
    
    # Centrerad layout för de stora ikonerna
    _, c1, c2, c3, _ = st.columns([1, 1.2, 1.2, 1.2, 1])
    
    with c1:
        if st.button(".", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()
        st.markdown('<p class="icon-text">SYNTHESIS</p>', unsafe_allow_html=True)

    with c2:
        if st.button(".", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()
        st.markdown('<p class="icon-text">AUDIO</p>', unsafe_allow_html=True)

    with c3:
        if st.button(".", key="btn_v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()
        st.markdown('<p class="icon-text">VIDEO</p>', unsafe_allow_html=True)

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
        
        st.markdown("<hr style='border:0.5px solid rgba(0,242,255,0.2); margin:20px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            p = st.text_area("VAD VILL DU GENERERA?", height=100)
            if st.button("STARTA GENERERING", key="real_gen"):
                with st.status("PROCESSAR DATA..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_res = res
                st.rerun()
            if st.session_state.last_res:
                st.image(st.session_state.last_res, use_container_width=True)

        elif st.session_state.active_window == "AUDIO":
            st.subheader("🎵 Musik-modul")
            st.info("Här kopplar vi snart in MusicGen.")

        elif st.session_state.active_window == "VIDEO":
            st.subheader("🎬 Video-modul")
            st.info("Här kopplar vi snart in Stable Video Diffusion.")

        st.markdown('</div>', unsafe_allow_html=True)












