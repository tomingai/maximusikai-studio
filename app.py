import streamlit as st
import replicate
import os

# --- 1. SYSTEMKONFIGURATION ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None

# --- 2. PURE DESKTOP DESIGN (CSS) ---
def apply_space_ui():
    st.markdown("""
        <style>
        /* RYMDBAKGRUND */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }
        
        /* KVADRATISKA IKONER */
        .desktop-wrapper {
            position: relative;
            width: 100%;
            aspect-ratio: 1/1;
            margin-bottom: 20px;
        }
        .icon-card {
            width: 100%;
            height: 100%;
            border-radius: 35px;
            border: 2px solid rgba(0, 242, 255, 0.5);
            background-size: cover;
            background-position: center;
            box-shadow: 0 15px 45px rgba(0,0,0,0.8);
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: flex;
            align-items: flex-end;
            overflow: hidden;
        }
        .desktop-wrapper:hover .icon-card {
            transform: scale(1.05) translateY(-10px);
            border-color: #00f2ff;
            box-shadow: 0 0 50px rgba(0, 242, 255, 0.5);
        }
        .icon-label {
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            width: 100%;
            text-align: center;
            padding: 15px 0;
            color: #00f2ff;
            font-family: monospace;
            font-weight: bold;
            font-size: 1.1rem;
            letter-spacing: 3px;
        }
        
        /* OSYNLIG KNAPP SOM TÄCKER HELA IKONEN */
        .stButton button {
            position: absolute !important;
            top: 0; left: 0; width: 100%; height: 100%;
            background: transparent !important;
            border: none !important;
            color: transparent !important;
            z-index: 10;
            cursor: pointer;
        }

        /* FÖNSTER (GLASSMORPHISM) */
        .window-pane {
            background: rgba(0, 0, 0, 0.9) !important;
            backdrop-filter: blur(50px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 40px;
            padding: 40px;
            box-shadow: 0 0 100px rgba(0,0,0,1);
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:5rem; font-weight:900;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:15px; margin-bottom:60px;'>CORE_V13_STABLE</p>", unsafe_allow_html=True)
    
    _, col1, col2, col3, _ = st.columns([0.1, 1, 1, 1, 0.1])
    
    with col1:
        st.markdown('''<div class="desktop-wrapper">
            <div class="icon-card" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">SYNTHESIS</div>
            </div></div>''', unsafe_allow_html=True)
        if st.button("S", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with col2:
        st.markdown('''<div class="desktop-wrapper">
            <div class="icon-card" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">AUDIO</div>
            </div></div>''', unsafe_allow_html=True)
        if st.button("A", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with col3:
        st.markdown('''<div class="desktop-wrapper">
            <div class="icon-card" style="background-image: url('https://images.unsplash.com');">
                <div class="icon-label">VIDEO</div>
            </div></div>''', unsafe_allow_html=True)
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

        if st.session_state.active_window == "SYNTHESIS":
            p = st.text_area("VAD VILL DU SKAPA?")
            if st.button("GENERA", key="real_gen"):
                with st.spinner("PROCESSAR..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_res = res
                st.rerun()
            if st.session_state.last_res: st.image(st.session_state.last_res, use_container_width=True)

        elif st.session_state.active_window == "AUDIO":
            st.subheader("Musik-modul")
            st.audio("https://www.soundhelix.com")

        elif st.session_state.active_window == "VIDEO":
            st.subheader("Video-modul")
            st.video("https://www.w3schools.com")

        st.markdown('</div>', unsafe_allow_html=True)










