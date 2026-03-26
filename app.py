import streamlit as st
import replicate
import os

# --- 1. SYSTEM BOOT ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# State för att hantera fönster-status
if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None

# --- 2. CSS: DESKTOP & WINDOW REFINEMENT ---
def apply_os_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com');
        
        /* DESKTOP BACKGROUND (DEEP SPACE) */
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), 
                        url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }

        /* FLOATING WINDOW CONTAINER */
        .window-pane {
            background: rgba(8, 8, 8, 0.9);
            backdrop-filter: blur(30px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 40px 80px rgba(0,0,0,0.9);
            animation: slideUp 0.3s ease-out;
            z-index: 1000;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(30px) scale(0.95); }
            to { opacity: 1; transform: translateY(0) scale(1); }
        }

        /* COMPACT DESKTOP ICONS */
        .desktop-icon {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 25px 15px;
            text-align: center;
            transition: 0.3s;
            position: relative;
        }
        .desktop-icon:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: #00f2ff;
            transform: translateY(-5px);
        }
        .icon-emoji { font-size: 40px; margin-bottom: 10px; }
        .icon-label { color: white; font-family: 'Inter'; font-size: 13px; font-weight: 900; text-transform: uppercase; }

        /* HIDE STREAMLIT BUTTON OVER ICON */
        .stButton>button {
            position: absolute; width: 100%; height: 100%; top: 0; left: 0;
            opacity: 0; z-index: 10; cursor: pointer;
        }

        /* WINDOW HEADER */
        .win-title { font-family: 'JetBrains Mono'; color: #00f2ff; font-size: 12px; letter-spacing: 2px; }
        
        /* CLOSE BUTTON (X) CUSTOM STYLE */
        .close-btn {
            background: rgba(255, 0, 0, 0.2) !important;
            border: 1px solid rgba(255, 0, 0, 0.5) !important;
            color: white !important;
            font-weight: 900 !important;
        }
        </style>
    """, unsafe_allow_html=True)

apply_os_ui()

# --- 3. DESKTOP LAYER (Bakgrunden med ikoner) ---
if st.session_state.active_window is None:
    st.markdown("<br><br><br><h1 style='text-align:center; color:white; font-family:Inter; font-weight:900; font-size:4.5rem; letter-spacing:-4px;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:JetBrains Mono; letter-spacing:8px; font-size:11px;'>NEURAL_CORE_OS_v5.4</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Ikoner för att starta appar
    _, i1, i2, i3, _ = st.columns([1, 1.2, 1.2, 1.2, 1], gap="medium")
    
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

# --- 4. WINDOW LAYER (När ett fönster är öppet) ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Centrerat fönster
    _, win_col, _ = st.columns([0.1, 1, 0.1])
    
    with win_col:
        st.markdown('<div class="window-pane">', unsafe_allow_html=True)
        
        # WINDOW HEADER
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f'<div class="win-title">PROCESSOR_RUNNING: {st.session_state.active_window}</div>', unsafe_allow_html=True)
        
        # STÄNG-KNAPP (X) - Denna tar dig tillbaka till startsidan
        if h2.button("✖", key="close_win"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border: 0.5px solid #222; margin: 20px 0;'>", unsafe_allow_html=True)

        # APP CONTENT
        if st.session_state.active_window == "SYNTHESIS":
            s1, s2 = st.columns(2)
            with s1:
                prompt = st.text_area("NEURAL_PARAMETERS", placeholder="Ex: A futuristic forest with cosmic stars...", height=200)
                if st.button("EXECUTE_RENDER", use_container_width=True):
                    with st.status("GEN_STREAMING..."):
                        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                        st.session_state.last_res = res if isinstance(res, list) else res
                    st.rerun()
            with s2:
                if st.session_state.last_res:
                    st.image(st.session_state.last_res, use_container_width=True)
                else:
                    st.markdown("<div style='height:300px; border:1px dashed #222; display:flex; align-items:center; justify-content:center; color:#333; font-family:JetBrains Mono;'>AWAITING_VISUAL_SOURCE</div>", unsafe_allow_html=True)

        elif st.session_state.active_window == "AUDIO":
            st.title("🎵 AUDIO_WAVEFORM_LAB")
            st.info("Sonic engine online. Ready to synthesize frequencies.")
            
        elif st.session_state.active_window == "VIDEO":
            st.title("🎬 TEMPORAL_VIDEO_FLUX")
            st.warning("Video buffer initializing... Standby.")

        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. SYSTEM TRAY (Footer) ---
st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.9); padding: 8px 25px; border-top: 1px solid #111; display: flex; justify-content: space-between;">
        <span style="color: #444; font-family: 'JetBrains Mono'; font-size: 9px;">SYSTEM_STATUS: STABLE</span>
        <span style="color: #444; font-family: 'JetBrains Mono'; font-size: 9px;">© MAXIMUSIKAI_PREMIER</span>
    </div>
""", unsafe_allow_html=True)
rerun()


