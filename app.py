import streamlit as st
import replicate
import os

# --- 1. SYSTEM BOOT ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

# API Token Setup (Säkerställ att denna finns i din Streamlit Secrets)
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# State-hantering
if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None

# --- 2. CSS: GALAX-TEMA & DESKTOP UI ---
def apply_os_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com');
        
        /* FULLSKÄRMS GALAX-BAKGRUND */
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), 
                        url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center center !important;
            background-attachment: fixed !important;
        }

        /* FÖNSTER-DESIGN (GLASSMORPHISM) */
        .window-pane {
            background: rgba(5, 5, 10, 0.85);
            backdrop-filter: blur(25px);
            border: 1px solid rgba(0, 242, 255, 0.2);
            border-radius: 25px;
            padding: 40px;
            box-shadow: 0 50px 100px rgba(0,0,0,0.9);
            animation: slideUp 0.4s ease-out;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(40px) scale(0.98); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* SKRIVBORDS-IKONER (COMPACT) */
        .desktop-icon {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px 10px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
            max-width: 160px;
            margin: auto;
        }
        .desktop-icon:hover {
            background: rgba(0, 242, 255, 0.1);
            border-color: #00f2ff;
            transform: translateY(-10px);
            box-shadow: 0 0 30px rgba(0, 242, 255, 0.3);
        }
        .icon-emoji { font-size: 50px; margin-bottom: 15px; }
        .icon-label { 
            color: white; 
            font-family: 'Inter'; 
            font-size: 14px; 
            font-weight: 900; 
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* DOLD KNAPP ÖVER IKON */
        .stButton>button {
            position: absolute; width: 100%; height: 100%; top: 0; left: 0;
            opacity: 0; z-index: 10; cursor: pointer;
        }
        
        /* SYSTEM TRAY */
        .system-tray {
            position: fixed; bottom: 0; left: 0; width: 100%; 
            background: rgba(0,0,0,0.85); padding: 10px; 
            border-top: 1px solid rgba(255,255,255,0.05); 
            text-align: center; z-index: 999;
        }
        </style>
    """, unsafe_allow_html=True)

apply_os_ui()

# --- 3. SKRIVBORD (STARTSIDA) ---
if st.session_state.active_window is None:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:white; font-family:Inter; font-weight:900; font-size:5rem; letter-spacing:-4px; margin-bottom:0;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:JetBrains Mono; letter-spacing:10px; font-size:12px; opacity:0.8;'>GALACTIC_CORE_OS_v5.6</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Ikon-rader
    _, i1, i2, i3, _ = st.columns([1, 1.2, 1.2, 1.2, 1], gap="large")
    
    with i1:
        st.markdown('<div class="desktop-icon"><div class="icon-emoji">🌌</div><div class="icon-label">Synthesis</div></div>', unsafe_allow_html=True)
        if st.button("OPEN_SYNTH", key="btn_synth"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with i2:
        st.markdown('<div class="desktop-icon"><div class="icon-emoji">🎵</div><div class="icon-label">Audio Lab</div></div>', unsafe_allow_html=True)
        if st.button("OPEN_AUDIO", key="btn_audio"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with i3:
        st.markdown('<div class="desktop-icon"><div class="icon-emoji">🎬</div><div class="icon-label">Video Flux</div></div>', unsafe_allow_html=True)
        if st.button("OPEN_VIDEO", key="btn_video"):
            st.session_state.active_window = "VIDEO"
            st.rerun()

# --- 4. FÖNSTER-LAGER (APPAR) ---
else:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.1, 1, 0.1])
    
    with win_col:
        st.markdown('<div class="window-pane">', unsafe_allow_html=True)
        
        # Fönster-kontroller
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h3 style='color:white; margin:0;'>🗔 {st.session_state.active_window}_PROCESSOR</h3>", unsafe_allow_html=True)
        
        if h2.button("✖", key="exit_window"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border: 0.5px solid rgba(0,242,255,0.2);'>", unsafe_allow_html=True)

        # Innehåll per app
        if st.session_state.active_window == "SYNTHESIS":
            col_in, col_out = st.columns(2)
            with col_in:
                p = st.text_area("DESCRIBE_VISION", height=150, placeholder="E.g. A neon-lit nebula forest...")
                if st.button("EXECUTE_SYNTH", use_container_width=True):
                    with st.status("STREAMING_FROM_CORE..."):
                        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                        st.session_state.last_res = res if isinstance(res, list) else res
                    st.rerun()
            with col_out:
                if st.session_state.last_res:
                    st.image(st.session_state.last_res, use_container_width=True)

        elif st.session_state.active_window == "AUDIO":
            st.info("🎵 SONIC_WAVEFORM_ENGINE: Online. Ready to compose.")
            
        elif st.session_state.active_window == "VIDEO":
            st.warning("🎬 TEMPORAL_VIDEO_FLUX: Initializing buffer...")

        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. SYSTEM TRAY ---
st.markdown("""
    <div class="system-tray">
        <span style="color: #444; font-family: 'JetBrains Mono'; font-size: 9px;">MAXIMUSIKAI // NEURAL_OS_STABLE_REL_2024</span>
    </div>
""", unsafe_allow_html=True)



