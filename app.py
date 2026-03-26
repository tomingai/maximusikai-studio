import streamlit as st
import replicate
import os

# --- 1. SYSTEM ---
st.set_page_config(page_title="MAXIMUS_OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

if "active_window" not in st.session_state: st.session_state.active_window = None
if "last_res" not in st.session_state: st.session_state.last_res = None

# --- 2. RYMD-UI & KNAPP-FIX ---
def apply_space_ui():
    st.markdown("""
        <style>
        .stAppViewContainer {
            background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), 
                              url("https://images.unsplash.com") !important;
            background-size: cover !important;
            background-position: center !important;
        }
        .main, .stAppHeader, .stAppViewBlockContainer { background: transparent !important; }

        /* STYLA OM STREAMLITS KNAPPAR TILL SMÅ IKONER */
        div.stButton > button {
            display: block;
            margin: 0 auto;
            width: 80px !important;
            height: 80px !important;
            border-radius: 15px !important;
            border: 2px solid rgba(0, 242, 255, 0.5) !important;
            background-size: cover !important;
            background-position: center !important;
            color: transparent !important; /* Dölj texten på knappen */
            transition: 0.3s transform !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
        }

        div.stButton > button:hover {
            transform: scale(1.2) !important;
            border-color: #00f2ff !important;
            box-shadow: 0 0 20px rgba(0, 242, 255, 0.6) !important;
        }

        /* SPECIFIKA BILDER FÖR VARJE KNAPP */
        /* Synthesis (Skog) */
        div.stButton > button[key="btn_s"] {
            background-image: url('https://images.unsplash.com') !important;
        }
        /* Audio (Berg) */
        div.stButton > button[key="btn_a"] {
            background-image: url('https://images.unsplash.com') !important;
        }
        /* Video (Sjö) */
        div.stButton > button[key="btn_v"] {
            background-image: url('https://images.unsplash.com') !important;
        }

        /* FÖNSTER */
        .window-pane {
            background: rgba(0, 0, 0, 0.9) !important;
            backdrop-filter: blur(40px);
            border: 1px solid rgba(0, 242, 255, 0.3);
            border-radius: 30px;
            padding: 30px;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

apply_space_ui()

# --- 3. SKRIVBORDS-VY ---
if st.session_state.active_window is None:
    st.markdown("<br><br><h1 style='text-align:center; color:white; font-size:4rem; font-weight:900;'>MAXIMUSIKAI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f2ff; font-family:monospace; letter-spacing:10px; margin-bottom:50px;'>OS_CORE_FIXED</p>", unsafe_allow_html=True)
    
    # Centrerad rad för ikonerna
    _, c1, c2, c3, _ = st.columns([1.5, 1, 1, 1, 1.5])
    
    with c1:
        if st.button(".", key="btn_s"):
            st.session_state.active_window = "SYNTHESIS"
            st.rerun()
        st.markdown("<p style='text-align:center; color:#00f2ff; font-size:10px;'>SYNTH</p>", unsafe_allow_html=True)

    with c2:
        if st.button(".", key="btn_a"):
            st.session_state.active_window = "AUDIO"
            st.rerun()
        st.markdown("<p style='text-align:center; color:#00f2ff; font-size:10px;'>AUDIO</p>", unsafe_allow_html=True)

    with c3:
        if st.button(".", key="btn_v"):
            st.session_state.active_window = "VIDEO"
            st.rerun()
        st.markdown("<p style='text-align:center; color:#00f2ff; font-size:10px;'>VIDEO</p>", unsafe_allow_html=True)

# --- 4. FÖNSTER-VY ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.1, 1, 0.1])
    with win_col:
        st.markdown('<div class="window-pane">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h3 style='color:white; margin:0;'>🗔 {st.session_state.active_window}</h3>", unsafe_allow_html=True)
        if h2.button("✖", key="exit"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown("<hr style='border:0.5px solid rgba(0,242,255,0.2); margin:15px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTHESIS":
            p = st.text_area("PROMPT")
            if st.button("GENERATE", key="real_gen"):
                with st.status("WORKING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_res = res
                st.rerun()
            if st.session_state.last_res: st.image(st.session_state.last_res, use_container_width=True)

        elif st.session_state.active_window == "AUDIO":
            st.info("Audio system online.")

        elif st.session_state.active_window == "VIDEO":
            st.info("Video system online.")

        st.markdown('</div>', unsafe_allow_html=True)











