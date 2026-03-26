import streamlit as st
import replicate
import os

# --- 1. SYSTEM BOOT ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

# API Token Setup
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# State-hantering för fönster
if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None

# --- 2. CSS: SPACE UI ---
def apply_space_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com');
        
        /* RYMDBAKGRUND (DEEP SPACE) */
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), 
                        url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }

        /* FÖNSTER (GLAS-EFFEKT) */
        .window-pane {
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(40px);
            border: 1px solid rgba(0, 242, 255, 0.2);
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 0 50px rgba(0,0,0,1);
            animation: openAnim 0.3s ease-out;
        }
        @keyframes openAnim {
            from { opacity: 0; transform: scale(0.95) translateY(20px); }
            to { opacity: 1; transform: scale(1) translateY(0); }
        }

        /* SKRIVBORDS-IKONER (COMPACT GLASS) */
        .desktop-icon {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 18px;
            padding: 20px 10px;
            text-align: center;
            transition: 0.3s;
            position: relative;
            max-width: 120px;
            margin: auto;
        }
        .desktop-icon:hover {
            background: rgba(0, 242, 255, 0.1);
            border-color: #00f2ff;
            transform: translateY(-5px);
            box-shadow: 0 0 20px rgba(0, 242, 255, 0.2);
        }
        .icon-emoji { font-size: 35px; margin-bottom: 8px; }
        .icon-label { color: white; font-family: 'Inter'; font-size: 11px; font-weight: 800; text-transform: uppercase; }

        /* OSYNLIG KNAPP */
        .stButton>button {
            position: absolute; width: 100%; height: 100%; top: 0; left: 0;
            opacity: 0; z-index: 10; cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORD (STARTSIDA) ---
if st.session_state.active_window is None:
    st.markdown("<br><br><br><br><h1 style='text-align:center; color:white; font-family:Inter; font-weight:900; font-size:4.5rem; letter-spacing:-3px; margin-bottom:0;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:JetBrains Mono; letter-spacing:12px; font-size:10px;'>SPACE_CORE_OS_v5.8</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Ikoner
    _, i1, i2, i3, _ = st.columns([1, 1, 1, 1, 1])
    
    with i1:
        st.markdown('<div class="desktop-icon"><div class="icon-emoji">🌌</div><div class="icon-label">Synth</div></div>', unsafe_allow_html=True)
        if st.button("S", key="os_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with i2:
        st.markdown('<div class="desktop-icon"><div class="icon-emoji">🎵</div><div class="icon-label">Audio</div></div>', unsafe_allow_html=True)
        if st.button("A", key="os_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with i3:
        st.markdown('<div class="desktop-icon"><div class="icon-emoji">🎬</div><div class="icon-label">Video</div></div>', unsafe_allow_html=True)
        if st.button("V", key="os_v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()

# --- 4. FÖNSTER-LAGER (APPAR) ---
else:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.15, 1, 0.15])
    
    with win_col:
        st.markdown('<div class="window-pane">', unsafe_allow_html=True)
        
        # Header med stäng-knapp (X) för att återgå till startsidan
        h1, h2 = st.columns([0.95, 0.05])
        h1.markdown(f"<h3 style='color:white; margin:0;'>🗔 {st.session_state.active_window}_PROCESSOR</h3>", unsafe_allow_html=True)
        
        if h2.button("✖", key="exit_window"):
            st.session_state.active_window = None # Går tillbaka till rymden
            st.rerun()
        
        st.markdown("<hr style='border: 0.5px solid rgba(255,255,255,0.1); margin: 20px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            col_a, col_b = st.columns(2)
            with col_a:
                prompt = st.text_area("CORE_PROMPT", height=150, placeholder="Define cosmic vision...")
                if st.button("RENDER", use_container_width=True):
                    with st.status("PROCESSING..."):
                        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                        st.session_state.last_res = res if isinstance(res, list) else res
                    st.rerun()
            with col_b:
                if st.session_state.last_res:
                    st.image(st.session_state.last_res, use_container_width=True)

        elif st.session_state.active_window == "AUDIO":
            st.info("🎵 SONIC_ENGINE_READY: Awaiting frequency link.")
            
        elif st.session_state.active_window == "VIDEO":
            st.warning("🎬 VIDEO_BUFFER_SYNC: Initializing temporal flux.")

        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. SYSTEM TRAY ---
st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.9); padding: 5px; border-top: 1px solid #111; text-align: center;">
        <span style="color: #444; font-family: 'JetBrains Mono'; font-size: 8px;">MAXIMUSIKAI // NEURAL_SPACE_STABLE</span>
    </div>
""", unsafe_allow_html=True)




