import streamlit as st
import replicate
import os
import requests
import random
from io import BytesIO

# --- 1. CONFIG ---
st.set_page_config(page_title="MAXIMUSIK AI", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session State Init
if "active_window" not in st.session_state: st.session_state.active_window = None
if "synth_res" not in st.session_state: st.session_state.synth_res = None
if "world_name" not in st.session_state: st.session_state.world_name = "VOID_SECTOR_01"
if "wallpaper" not in st.session_state: 
    st.session_state.wallpaper = "https://images.unsplash.com"
if "accent_color" not in st.session_state:
    st.session_state.accent_color = "#00f2ff"

# --- 2. HJÄLPFUNKTIONER ---
def get_media_data(url):
    try:
        response = requests.get(url, timeout=10)
        return BytesIO(response.content)
    except: return None

# --- 3. DESIGN (CSS) ---
def apply_ui():
    accent = st.session_state.accent_color
    st.markdown(f"""
        <style>
        .stAppViewContainer {{
            background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6)), 
                              url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; background-position: center !important;
        }}
        .main, .stAppHeader, .stAppViewBlockContainer {{ background: transparent !important; }}

        /* SCANNING LINE ANIMATION */
        @keyframes scan {{
            0% {{ top: -100%; }}
            100% {{ top: 100%; }}
        }}

        /* KNAPPAR - TRANSPARENTA MED BILDER */
        div[data-testid="stButton"] > button {{
            width: 200px !important; height: 200px !important;
            border-radius: 40px !important; border: 1px solid {accent}33 !important;
            background-color: transparent !important; /* BORTTAGEN BAKGRUNDSFÄRG */
            position: relative !important;
            overflow: hidden !important;
            transition: 0.4s ease-in-out !important;
        }}

        /* BILDERNA */
        div[data-testid="stButton"] > button::before {{
            content: "" !important;
            position: absolute !important;
            top: 0; left: 0; right: 0; bottom: 0 !important;
            background-size: cover !important;
            background-position: center !important;
            opacity: 0.6 !important;
            transition: 0.4s !important;
            z-index: 1 !important;
        }}

        /* SCANNING LINJEN */
        div[data-testid="stButton"] > button::after {{
            content: "" !important;
            position: absolute !important;
            width: 100% !important; height: 50px !important;
            background: linear-gradient(to bottom, transparent, {accent}22, transparent) !important;
            animation: scan 3s linear infinite !important;
            z-index: 2 !important;
            pointer-events: none !important;
        }}

        /* BILD-LÄNKAR */
        div[data-testid="stButton"] > button[key="s"]::before {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="a"]::before {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="v"]::before {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="wp"]::before {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="sys"]::before {{ background-image: url('https://images.unsplash.com') !important; }}

        div[data-testid="stButton"] > button:hover::before {{
            opacity: 1 !important;
            transform: scale(1.1) !important;
        }}
        
        div[data-testid="stButton"] > button:hover {{
            border-color: {accent} !important;
            box-shadow: 0 0 40px {accent}44 !important;
            background-color: rgba(255,255,255,0.05) !important;
        }}

        div[data-testid="stButton"] > button p {{ display: none !important; }}

        /* FÖNSTER - MER TRANSPARENT */
        .window {{ 
            background: rgba(0, 5, 10, 0.8) !important; /* MER GENOMSKINLIGT */
            backdrop-filter: blur(30px); 
            border: 1px solid {accent}22; 
            border-radius: 30px; padding: 40px; color: white; 
        }}

        .label {{ text-align: center; color: {accent}; font-family: monospace; margin-top: 15px; letter-spacing: 2px; font-size: 1rem; text-transform: uppercase; opacity: 0.9; }}
        .space-title {{ text-align: center; color: white; font-size: 1.5rem; letter-spacing: 2px; margin-top: 30px; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<h1 class='space-title'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:{st.session_state.accent_color}; font-family:monospace; letter-spacing:5px; font-size:1rem;'>{st.session_state.world_name}</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    _, c1, c2, c3, c4, c5, _ = st.columns([0.1, 1, 1, 1, 1, 1, 0.1])
    
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

# --- 5. WINDOW MANAGER ---
else:
    st.markdown("<br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.2, 1, 0.2])
    with win_col:
        st.markdown('<div class="window">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='font-size:1.2rem; font-family:monospace;'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()

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
            bg_p = st.text_area("ENVIRONMENT COMMAND:")
            if st.button("SYNC", use_container_width=True):
                with st.status("..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": bg_p, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = res
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)



















