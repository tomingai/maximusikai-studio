import streamlit as st
import replicate
import os

# --- 1. SYSTEM BOOT ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# State-hantering
if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None

# --- 2. RYMD-INJEKTION & UI ---
def apply_space_ui():
    st.markdown("""
        <style>
        /* RYMDBAKGRUND */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }

        /* Gör containrar transparenta */
        .main, .stAppHeader, .stAppViewBlockContainer {
            background: transparent !important;
        }

        /* STÖRRE OCH BILD-BASERADE IKONER */
        .desktop-icon {
            background-size: cover;
            background-position: center;
            border: 2px solid rgba(0, 242, 255, 0.2);
            border-radius: 25px;
            height: 220px; /* Ännu lite större */
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            align-items: center;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            position: relative;
            overflow: hidden;
        }
        
        .desktop-icon:hover {
            border-color: #00f2ff;
            transform: scale(1.08);
            box-shadow: 0 0 50px rgba(0, 242, 255, 0.4);
        }

        .icon-label {
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(5px);
            width: 100%;
            text-align: center;
            padding: 12px 0;
            color: #00f2ff;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            letter-spacing: 3px;
            font-size: 14px;
        }

        /* FÖNSTER (GLASMORPHISM) */
        .window-pane {
            background: rgba(0, 0, 0, 0.85) !important;
            backdrop-filter: blur(25px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 30px;
            padding: 40px;
            box-shadow: 0 0 100px rgba(0,0,0,1);
        }

        /* OSYNLIG KNAPP ÖVER IKON */
        .stButton>button {
            position: absolute; width: 100%; height: 100%; top: 0; left: 0;
            opacity: 0; z-index: 10; cursor: pointer;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-family:sans-serif; font-weight:900; font-size:5rem; letter-spacing:-2px;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:15px; margin-bottom:50px;'>SPACE_CORE_V2</p>", unsafe_allow_html=True)
    
    # Kolumner för de stora ikonerna
    _, i1, i2, i3, _ = st.columns([0.4, 1, 1, 1, 0.4])
    
    with i1:
        # SKOG
        st.markdown('''
            <div class="desktop-icon" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">SYNTHESIS</div>
            </div>''', unsafe_allow_html=True)
        if st.button("S", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with i2:
        # BERG
        st.markdown('''
            <div class="desktop-icon" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">AUDIO</div>
            </div>''', unsafe_allow_html=True)
        if st.button("A", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with i3:
        # NATUR/DAL
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
    _, win_col, _ = st.columns([0.1, 1, 0.1])
    
    with win_col:
        st.markdown('<div class="window-pane">', unsafe_allow_html=True)
        
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='color:white; margin:0;'>🗔 {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        
        if h2.button("✖", key="exit"):
            st.session_state.active_window = None
            st.session_state.last_res = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid rgba(0,242,255,0.2); margin:20px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            col_in, col_out = st.columns(2)
            with col_in:
                p = st.text_area("VAD VILL DU SKAPA?", placeholder="En astronaut som rider på en skogsvarelse...")
                if st.button("STARTA GENERERING", use_container_width=True):
                    with st.status("PROCESSAR DATA...", expanded=True):
                        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                        st.session_state.last_res = res if isinstance(res, list) else res
                    st.rerun()
            with col_out:
                if st.session_state.last_res:
                    st.image(st.session_state.last_res, use_container_width=True, caption="RESULTAT")
                else:
                    st.info("Väntar på input...")
        
        # Audio & Video är placeholders tills vi väljer modeller
        elif st.session_state.active_window in ["AUDIO", "VIDEO"]:
            st.warning(f"Modulen {st.session_state.active_window} är under konstruktion.")
            
        st.markdown('</div>', unsafe_allow_html=True)






