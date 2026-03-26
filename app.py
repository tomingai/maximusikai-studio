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
    st.session_state.wallpaper = "https://images.unsplash.com"
if "accent_color" not in st.session_state:
    st.session_state.accent_color = "#00f2ff"

# --- 2. DESIGN (NEW OS LAYOUT) ---
def apply_ui():
    accent = st.session_state.accent_color
    st.markdown(f"""
        <style>
        /* FULLSTÄNDIG TRANSPARENS */
        .stAppViewContainer {{
            background-image: url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; 
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        .main, .stAppHeader, .stAppViewBlockContainer, div[data-testid="stVerticalBlock"] {{
            background: transparent !important;
            background-color: transparent !important;
        }}

        /* SKRIVBORDS-TITEL */
        .os-title {{
            position: fixed; top: 40px; left: 50px;
            color: white; font-size: 2rem; font-weight: 900;
            letter-spacing: -1px; text-shadow: 0 0 20px {accent}44;
            font-family: sans-serif; z-index: 0;
        }}

        /* IKON-GRID LAYOUT */
        .desktop-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, 220px);
            grid-gap: 40px;
            padding: 120px 50px;
            justify-content: center;
        }}

        /* MODERNA GLASS-IKONER */
        div[data-testid="stButton"] > button {{
            width: 200px !important; height: 200px !important;
            border-radius: 40px !important; border: 1px solid {accent}22 !important;
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(15px) !important;
            transition: 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
            position: relative; overflow: hidden;
        }}
        div[data-testid="stButton"] > button::before {{
            content: "" !important; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
            background-size: cover; background-position: center; opacity: 0.6; z-index: 1;
        }}
        
        /* BILDER */
        div[data-testid="stButton"] > button[key="s"]::before {{ background-image: url('https://images.unsplash.com'); }}
        div[data-testid="stButton"] > button[key="a"]::before {{ background-image: url('https://images.unsplash.com'); }}
        div[data-testid="stButton"] > button[key="v"]::before {{ background-image: url('https://images.unsplash.com'); }}
        div[data-testid="stButton"] > button[key="wp"]::before {{ background-image: url('https://images.unsplash.com'); }}
        div[data-testid="stButton"] > button[key="sys"]::before {{ background-image: url('https://images.unsplash.com'); }}

        div[data-testid="stButton"] > button:hover {{
            transform: scale(1.05) translateY(-5px) !important;
            border-color: {accent} !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
        }}
        div[data-testid="stButton"] > button p {{ display: none !important; }}

        /* FLYTANDE FÖNSTER */
        .window-overlay {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.4); backdrop-filter: blur(10px);
            display: flex; align-items: center; justify-content: center; z-index: 9999;
        }}
        .window-content {{
            width: 800px; max-height: 80vh; overflow-y: auto;
            background: rgba(10, 15, 20, 0.9) !important;
            border: 1px solid {accent}44; border-radius: 40px;
            padding: 50px; box-shadow: 0 50px 100px rgba(0,0,0,0.5);
            color: white; position: relative;
        }}
        
        .label {{ color: {accent}; font-family: monospace; font-size: 0.9rem; text-align: center; margin-top: 10px; letter-spacing: 2px; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP INTERFACE ---
if st.session_state.active_window is None:
    st.markdown("<div class='os-title'>MAXIMUSIK AI</div>", unsafe_allow_html=True)
    
    # Grid-layout för ikoner
    st.markdown("<div class='desktop-grid'>", unsafe_allow_html=True)
    
    # Vi använder Streamlits kolumner inuti vår CSS-grid för att få knapparna klickbara
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        if st.button("S", key="s"): st.session_state.active_window = "SYNTH"; st.rerun()
        st.markdown('<p class="label">SYNTH</p>', unsafe_allow_html=True)
    with c2:
        if st.button("A", key="a"): st.session_state.active_window = "AUDIO"; st.rerun()
        st.markdown('<p class="label">AUDIO</p>', unsafe_allow_html=True)
    with c3:
        if st.button("V", key="v"): st.session_state.active_window = "VIDEO"; st.rerun()
        st.markdown('<p class="label">VIDEO</p>', unsafe_allow_html=True)
    with c4:
        if st.button("W", key="wp"): st.session_state.active_window = "ENGINE"; st.rerun()
        st.markdown('<p class="label">ENGINE</p>', unsafe_allow_html=True)
    with c5:
        if st.button("Y", key="sys"): st.session_state.active_window = "SYSTEM"; st.rerun()
        st.markdown('<p class="label">SYSTEM</p>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- 4. WINDOW MANAGER (POPUP) ---
else:
    st.markdown('<div class="window-overlay">', unsafe_allow_html=True)
    st.markdown('<div class="window-content">', unsafe_allow_html=True)
    
    h1, h2 = st.columns([0.9, 0.1])
    h1.markdown(f"<h2 style='margin:0; font-family:monospace;'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
    if h2.button("✕", key="close"):
        st.session_state.active_window = None
        st.rerun()
    
    st.markdown(f"<hr style='border:1px solid {st.session_state.accent_color}22; margin:25px 0;'>", unsafe_allow_html=True)

    if st.session_state.active_window == "SYNTH":
        p = st.text_area("PROMPT:")
        if st.button("GENERATE", use_container_width=True):
            with st.status("PROCESSING..."):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                st.session_state.synth_res = res
            st.rerun()
        if st.session_state.synth_res:
            st.image(st.session_state.synth_res)

    elif st.session_state.active_window == "ENGINE":
        bg_p = st.text_area("NEW ENVIRONMENT:")
        if st.button("SYNC", use_container_width=True):
            with st.status("..."):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": bg_p, "aspect_ratio": "16:9"})
                st.session_state.wallpaper = res
            st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)





















