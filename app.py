import streamlit as st
import replicate
import os
import requests
from io import BytesIO

# --- 1. CONFIG ---
st.set_page_config(page_title="MAXIMUSIK AI", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session State
if "active_window" not in st.session_state: st.session_state.active_window = None
if "synth_res" not in st.session_state: st.session_state.synth_res = None
if "wallpaper" not in st.session_state: 
    # Sätter en riktigt fet rymdbakgrund som standard
    st.session_state.wallpaper = "https://images.unsplash.com"
if "accent_color" not in st.session_state:
    st.session_state.accent_color = "#00f2ff"

# --- 2. DESIGN (SPACE OS LAYOUT) ---
def apply_ui():
    accent = st.session_state.accent_color
    st.markdown(f"""
        <style>
        /* FIXAR RYMDEN ÖVER HELA SKÄRMEN */
        .stAppViewContainer {{
            background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.5)), 
                              url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; 
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        
        /* RADERA ALLA STANDARD-FÄLT */
        .main, .stAppHeader, .stAppViewBlockContainer, 
        div[data-testid="stVerticalBlock"], 
        div[data-testid="stHorizontalBlock"] {{
            background: transparent !important;
            background-color: transparent !important;
        }}

        /* TITEL UPPE I HÖRNET */
        .os-title {{
            position: fixed; top: 30px; left: 40px;
            color: white; font-size: 1.8rem; font-weight: 900;
            letter-spacing: 5px; text-shadow: 0 0 20px {accent}66;
            font-family: monospace; z-index: 10;
        }}

        /* IKON-GRID */
        .desktop-grid {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 40px;
            padding-top: 150px;
        }}

        /* GIGANTISKA GLASS-IKONER */
        div[data-testid="stButton"] > button {{
            width: 200px !important; height: 200px !important;
            border-radius: 50px !important; 
            border: 1px solid {accent}33 !important;
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(15px) !important;
            position: relative !important;
            overflow: hidden !important;
            transition: 0.5s ease !important;
        }}

        /* BILD-LAGER PÅ KNAPPARNA */
        div[data-testid="stButton"] > button::before {{
            content: "" !important;
            position: absolute !important;
            top: 0; left: 0; right: 0; bottom: 0 !important;
            background-size: cover !important;
            background-position: center !important;
            opacity: 0.6 !important;
            z-index: 1 !important;
        }}

        /* BILD-URLS */
        div[data-testid="stButton"] > button[key="s"]::before {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="a"]::before {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="v"]::before {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="wp"]::before {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="sys"]::before {{ background-image: url('https://images.unsplash.com') !important; }}

        div[data-testid="stButton"] > button:hover {{
            transform: scale(1.1) !important;
            border-color: {accent} !important;
            box-shadow: 0 0 50px {accent}44 !important;
        }}
        div[data-testid="stButton"] > button p {{ display: none !important; }}

        /* GENOMSKINLIGT FÖNSTER */
        .window-content {{
            background: rgba(0, 5, 10, 0.85) !important;
            backdrop-filter: blur(40px);
            border: 1px solid {accent}22;
            border-radius: 40px;
            padding: 40px;
            color: white;
            box-shadow: 0 50px 150px rgba(0,0,0,0.8);
        }}
        
        .label {{ text-align: center; color: {accent}; font-family: monospace; font-size: 1rem; margin-top: 15px; letter-spacing: 3px; text-transform: uppercase; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<div class='os-title'>MAXIMUSIK AI</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='desktop-grid'>", unsafe_allow_html=True)
    cols = st.columns(5)
    
    with cols[0]:
        if st.button("S", key="s"): st.session_state.active_window = "SYNTH"; st.rerun()
        st.markdown('<p class="label">SYNTH</p>', unsafe_allow_html=True)
    with cols[1]:
        if st.button("A", key="a"): st.session_state.active_window = "AUDIO"; st.rerun()
        st.markdown('<p class="label">AUDIO</p>', unsafe_allow_html=True)
    with cols[2]:
        if st.button("V", key="v"): st.session_state.active_window = "VIDEO"; st.rerun()
        st.markdown('<p class="label">VIDEO</p>', unsafe_allow_html=True)
    with cols[3]:
        if st.button("W", key="wp"): st.session_state.active_window = "ENGINE"; st.rerun()
        st.markdown('<p class="label">ENGINE</p>', unsafe_allow_html=True)
    with cols[4]:
        if st.button("Y", key="sys"): st.session_state.active_window = "SYSTEM"; st.rerun()
        st.markdown('<p class="label">SYSTEM</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. WINDOWS ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.15, 1, 0.15])
    
    with win_col:
        st.markdown('<div class="window-content">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='margin:0; font-family:monospace; color:{st.session_state.accent_color};'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown(f"<hr style='border:1px solid {st.session_state.accent_color}22; margin:20px 0;'>", unsafe_allow_html=True)

        if st.session_state.active_window == "SYNTH":
            p = st.text_area("MATRIX_PROMPT:")
            if st.button("EXECUTE", use_container_width=True):
                with st.status("PROCESSING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res:
                st.image(st.session_state.synth_res)

        elif st.session_state.active_window == "ENGINE":
            bg_p = st.text_area("ENVIRONMENT_COMMAND:")
            if st.button("SYNC", use_container_width=True):
                with st.status("..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": bg_p, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = res
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)






















