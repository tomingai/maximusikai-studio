import streamlit as st
import replicate
import os

# --- 1. SYSTEMKONFIGURATION ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

# API-nyckel hantering
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# State-hantering för fönster och resultat
if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None

# --- 2. RYMD-DESIGN (CSS) ---
def apply_space_ui():
    st.markdown("""
        <style>
        /* RYMDBAKGRUND (James Webb - Carina Nebula) */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), 
                              url("https://4kwallpapers.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }

        /* Gör Streamlit-containrar osynliga */
        .main, .stAppHeader, .stAppViewBlockContainer {
            background: transparent !important;
        }

        /* SKRIVBORDS-IKONER (STÖRRE + NATURBILDER) */
        .desktop-icon {
            background-size: cover;
            background-position: center;
            border: 2px solid rgba(0, 242, 255, 0.2);
            border-radius: 25px;
            height: 240px; /* Rejäl storlek */
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 15px 40px rgba(0,0,0,0.6);
            position: relative;
            overflow: hidden;
        }
        
        .desktop-icon:hover {
            border-color: #00f2ff;
            transform: scale(1.05) translateY(-5px);
            box-shadow: 0 0 50px rgba(0, 242, 255, 0.4);
        }

        .icon-label {
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(10px);
            width: 100%;
            text-align: center;
            padding: 15px 0;
            color: #00f2ff;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            letter-spacing: 4px;
            font-size: 16px;
        }

        /* FÖNSTER (GLASMORPHISM) */
        .window-pane {
            background: rgba(0, 0, 0, 0.85) !important;
            backdrop-filter: blur(25px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 30px;
            padding: 40px;
            box-shadow: 0 0 100px rgba(0,0,0,1);
            color: white;
        }

        /* DÖLJ STANDARD-KNAPPAR ÖVER IKONER */
        .stButton>button {
            position: absolute; width: 100%; height: 100%; top: 0; left: 0;
            opacity: 0; z-index: 10; cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:5rem; font-weight:900; letter-spacing:-2px;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:15px; margin-bottom:60px;'>CORE_SYSTEM_V3</p>", unsafe_allow_html=True)
    
    # Tre kolumner för ikonerna
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # SKOG
        st.markdown('''
            <div class="desktop-icon" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">SYNTHESIS</div>
            </div>''', unsafe_allow_html=True)
        if st.button("S", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with col2:
        # BERG
        st.markdown('''
            <div class="desktop-icon" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">AUDIO</div>
            </div>''', unsafe_allow_html=True)
        if st.button("A", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with col3:
        # VATTENFALL/NATUR
        st.markdown('''
            <div class="desktop-icon" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">VIDEO</div>
            </div>''', unsafe_allow_html=True)
        if st.button("V", key="btn_v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()

# --- 4. FÖNSTER-VY ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.05, 1, 0.05])
    
    with win_col:
        st.markdown('<div class="window-pane">', unsafe_allow_html=True)
        
        # Header med stäng-knapp
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:white; margin:0;'>🗔 {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✖", key="exit"):
            st.session_state.active_window = None
            st.session_state.last_res = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid rgba(0,242,255,0.2); margin:25px 0;'>", unsafe_allow_html=True)

        # --- MODUL: SYNTHESIS (BILDER) ---
        if st.session_state.active_window == "SYNTHESIS":
            c1, c2 = st.columns(2)
            with c1:
                prompt = st.text_area("BESKRIV DIN VISION", height=150)
                if st.button("GENERA BILD", use_container_width=True):
                    with st.spinner("PROCESSAR KVANTDATA..."):
                        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                        st.session_state.last_res = res
                    st.rerun()
            with c2:
                if st.session_state.last_res:
                    st.image(st.session_state.last_res, use_container_width=True)
                else:
                    st.info("System redo. Väntar på prompt...")

        # --- MODUL: AUDIO (MUSIK) ---
        elif st.session_state.active_window == "AUDIO":
            st.subheader("AI Musik-generering")
            audio_p = st.text_input("Vilken typ av ljud/musik vill du skapa?")
            if st.button("SKAPA LJUD", use_container_width=True):
                st.info("Kopplar upp mot Meta MusicGen...")
                # Exempel: res = replicate.run("facebookresearch/musicgen:...", input={"prompt": audio_p})

        # --- MODUL: VIDEO ---
        elif st.session_state.active_window == "VIDEO":
            st.warning("Video-modulen kräver hög beräkningskraft. Under konstruktion.")

        st.markdown('</div>', unsafe_allow_html=True)







