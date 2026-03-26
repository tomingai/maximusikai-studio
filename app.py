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

# --- 2. RYMD-INJEKTION (FORCE BACKGROUND) ---
def apply_space_ui():
    st.markdown("""
        <style>
        /* Tvinga bakgrundsbilden på rot-nivå */
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }

        /* Gör alla Streamlit-containrar transparenta så rymden syns igenom */
        .main, .stAppHeader, .stAppViewBlockContainer {
            background: transparent !important;
        }

        /* FÖNSTER (GLASMORPHISM) */
        .window-pane {
            background: rgba(0, 0, 0, 0.8) !important;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 0 50px rgba(0,0,0,1);
        }

        /* SKRIVBORDS-IKONER */
        .desktop-icon {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            transition: 0.3s;
            position: relative;
        }
        .desktop-icon:hover {
            border-color: #00f2ff;
            background: rgba(0, 242, 255, 0.1);
            transform: translateY(-5px);
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
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-family:sans-serif; font-weight:900; font-size:4rem;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:10px;'>SPACE_CORE_OS</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Ikoner
    _, i1, i2, i3, _ = st.columns([1, 1.2, 1.2, 1.2, 1])
    
    with i1:
        st.markdown('<div class="desktop-icon"><h3>🌌</h3><p style="color:white; font-size:10px;">SYNTH</p></div>', unsafe_allow_html=True)
        if st.button("S", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()

    with i2:
        st.markdown('<div class="desktop-icon"><h3>🎵</h3><p style="color:white; font-size:10px;">AUDIO</p></div>', unsafe_allow_html=True)
        if st.button("A", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()

    with i3:
        st.markdown('<div class="desktop-icon"><h3>🎬</h3><p style="color:white; font-size:10px;">VIDEO</p></div>', unsafe_allow_html=True)
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
        h1.markdown(f"<h3 style='color:white;'>🗔 {st.session_state.active_window}</h3>", unsafe_allow_html=True)
        
        if h2.button("✖", key="exit"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid #222;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            col_in, col_out = st.columns(2)
            with col_in:
                p = st.text_area("PROMPT")
                if st.button("GENERATE", use_container_width=True):
                    with st.status("WORKING..."):
                        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                        st.session_state.last_res = res if isinstance(res, list) else res
                    st.rerun()
            with col_out:
                if st.session_state.last_res:
                    st.image(st.session_state.last_res, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)





