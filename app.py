import streamlit as st
import replicate
import os

# --- 1. SYSTEMKONFIGURATION ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

# API-nyckel hantering från Streamlit Secrets
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# State-hantering för fönster och AI-resultat
if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None
if "last_audio" not in st.session_state: st.session_state.last_audio = None

# --- 2. RYMD-DESIGN & GLASSMORPHISM (CSS) ---
def apply_space_ui():
    st.markdown("""
        <style>
        /* 4K RYMDBAKGRUND - CARINA NEBULA */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }

        /* Gör Streamlit-containrar genomskinliga */
        .main, .stAppHeader, .stAppViewBlockContainer {
            background: transparent !important;
        }

        /* STORA DESKTOP-IKONER MED NATURBILDER */
        .desktop-icon {
            background-size: cover;
            background-position: center;
            border: 2px solid rgba(0, 242, 255, 0.4);
            border-radius: 30px;
            height: 280px; /* Maximerad storlek */
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 20px 50px rgba(0,0,0,0.8);
            position: relative;
            overflow: hidden;
        }
        
        .desktop-icon:hover {
            transform: scale(1.05) translateY(-10px);
            border-color: #00f2ff;
            box-shadow: 0 0 60px rgba(0, 242, 255, 0.5);
        }

        .icon-label {
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(15px);
            width: 100%;
            text-align: center;
            padding: 20px 0;
            color: #00f2ff;
            font-family: 'Courier New', monospace;
            font-weight: 900;
            letter-spacing: 5px;
            font-size: 20px;
            border-top: 1px solid rgba(0, 242, 255, 0.2);
        }

        /* FÖNSTER-DESIGN (GLASSMORPHISM) */
        .window-pane {
            background: rgba(0, 0, 0, 0.9) !important;
            backdrop-filter: blur(30px);
            border: 1px solid rgba(0, 242, 255, 0.2);
            border-radius: 35px;
            padding: 40px;
            box-shadow: 0 0 100px rgba(0,0,0,1);
            color: white;
        }

        /* OSYNLIG KNAPP SOM TÄCKER HELA IKONEN */
        .stButton>button {
            position: absolute; width: 100%; height: 100%; top: 0; left: 0;
            opacity: 0; z-index: 10; cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY (START) ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:6rem; font-weight:900; letter-spacing:-3px;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:20px; margin-bottom:80px;'>ULTRA_CORE_V4</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # SYNTHESIS - SKOG
        st.markdown('''
            <div class="desktop-icon" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">SYNTHESIS</div>
            </div>''', unsafe_allow_html=True)
        if st.button("S", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with col2:
        # AUDIO - BERG
        st.markdown('''
            <div class="desktop-icon" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">AUDIO</div>
            </div>''', unsafe_allow_html=True)
        if st.button("A", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with col3:
        # VIDEO - SJÖ
        st.markdown('''
            <div class="desktop-icon" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">VIDEO</div>
            </div>''', unsafe_allow_html=True)
        if st.button("V", key="btn_v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()

# --- 4. FÖNSTER-VY (MODULER) ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.05, 1, 0.05])
    
    with win_col:
        st.markdown('<div class="window-pane">', unsafe_allow_html=True)
        
        # Header med Kryss-knapp
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:white; margin:0;'>🗔 {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✖", key="exit"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid rgba(0,242,255,0.2); margin:25px 0;'>", unsafe_allow_html=True)

        # --- MODUL: SYNTHESIS (BILDER) ---
        if st.session_state.active_window == "SYNTHESIS":
            c1, c2 = st.columns(2)
            with c1:
                p = st.text_area("VAD SKALL SKAPAS?", placeholder="En rymd-skog i neonfärger...")
                if st.button("GENERA VISION", use_container_width=True):
                    with st.status("KOPPLAR TILL FLUX..."):
                        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                        st.session_state.last_res = res
                    st.rerun()
            with c2:
                if st.session_state.last_res:
                    st.image(st.session_state.last_res, use_container_width=True, caption="Genererad Vision")

        # --- MODUL: AUDIO (MUSICGEN) ---
        elif st.session_state.active_window == "AUDIO":
            c1, c2 = st.columns(2)
            with c1:
                ap = st.text_area("LJUD-PROMPT", placeholder="Ambient space music with deep bass and forest echoes...")
                dur = st.slider("Längd (sek)", 5, 30, 10)
                if st.button("GENERA LJUD", use_container_width=True):
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
                    st.success("Ljudfil klar!")

        # --- MODUL: VIDEO ---
        elif st.session_state.active_window == "VIDEO":
            st.info("Video-modul redo. Härnäst kopplar vi in Stable Video Diffusion.")

        st.markdown('</div>', unsafe_allow_html=True)






