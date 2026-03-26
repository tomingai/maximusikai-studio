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

# --- 2. RYMD-DESIGN (CSS) ---
def apply_space_ui():
    st.markdown("""
        <style>
        /* 4K RYMDBAKGRUND */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }

        .main, .stAppHeader, .stAppViewBlockContainer {
            background: transparent !important;
        }

        /* STORA IKONER MED NATUR */
        .desktop-icon {
            background-size: cover;
            background-position: center;
            border: 1px solid rgba(0, 242, 255, 0.4);
            border-radius: 30px;
            height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            transition: 0.5s ease;
            box-shadow: 0 20px 50px rgba(0,0,0,0.8);
            position: relative;
            overflow: hidden;
        }
        
        .desktop-icon:hover {
            transform: scale(1.05);
            border-color: #00f2ff;
            box-shadow: 0 0 60px rgba(0, 242, 255, 0.5);
        }

        .icon-label {
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(15px);
            width: 100%;
            text-align: center;
            padding: 20px 0;
            color: #00f2ff;
            font-family: 'Courier New', monospace;
            font-weight: 900;
            letter-spacing: 5px;
            font-size: 18px;
        }

        /* FÖNSTER (GLASMORPHISM) */
        .window-pane {
            background: rgba(0, 0, 0, 0.9) !important;
            backdrop-filter: blur(30px);
            border: 1px solid rgba(0, 242, 255, 0.2);
            border-radius: 35px;
            padding: 40px;
            box-shadow: 0 0 100px rgba(0,0,0,1);
            color: white;
        }

        .stButton>button {
            position: absolute; width: 100%; height: 100%; top: 0; left: 0;
            opacity: 0; z-index: 10; cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:6rem; font-weight:900; letter-spacing:-3px;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:20px; margin-bottom:80px;'>ULTRA_CORE_V4</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="desktop-icon" style="background-image: url(\'https://images.unsplash.com\');"><div class="icon-label">SYNTHESIS</div></div>', unsafe_allow_html=True)
        if st.button("S", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with col2:
        st.markdown('<div class="desktop-icon" style="background-image: url(\'https://images.unsplash.com\');"><div class="icon-label">AUDIO</div></div>', unsafe_allow_html=True)
        if st.button("A", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with col3:
        st.markdown('<div class="desktop-icon" style="background-image: url(\'https://images.unsplash.com\');"><div class="icon-label">VIDEO</div></div>', unsafe_allow_html=True)
        if st.button("V", key="btn_v"):
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

        # --- MODUL: SYNTHESIS ---
        if st.session_state.active_window == "SYNTHESIS":
            c1, c2 = st.columns(2)
            with c1:
                p = st.text_area("BILD-PROMPT", placeholder="En futuristisk stad i skogen...")
                if st.button("GENERA BILD", use_container_width=True):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_res = res
                    st.rerun()
            with c2:
                if st.session_state.last_res: st.image(st.session_state.last_res, use_container_width=True)

        # --- MODUL: AUDIO (MUSICGEN AKTIVERAD) ---
        elif st.session_state.active_window == "AUDIO":
            c1, c2 = st.columns(2)
            with c1:
                ap = st.text_area("MUSIK-BESKRIVNING", placeholder="Lo-fi hip hop med rymd-syntar och tunga beats...")
                dur = st.slider("Längd (sekunder)", 5, 30, 15)
                if st.button("GENERA MUSIK", use_container_width=True):
                    with st.status("KOMPONERAR..."):
                        audio_res = replicate.run(
                            "meta/musicgen:671ac645cf51591bc3754da5ff3f4523d44373308dfc9496883cd2050119e8de",
                            input={"prompt": ap, "duration": dur}
                        )
                        st.session_state.last_audio = audio_res
                    st.rerun()
            with c2:
                if st.session_state.last_audio:
                    st.audio(st.session_state.last_audio)
                    st.success("Musik genererad!")

        # --- MODUL: VIDEO ---
        elif st.session_state.active_window == "VIDEO":
            st.info("Klicka på Synthesis först för att skapa en bild, sedan kan vi animera den här.")

        st.markdown('</div>', unsafe_allow_html=True)
True)







