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
if "bg_gallery" not in st.session_state or not isinstance(st.session_state.bg_gallery, list):
    st.session_state.bg_gallery = ["https://images.unsplash.com"]

# --- 2. HJÄLPFUNKTIONER ---
def get_media_data(url):
    try:
        response = requests.get(url, timeout=10)
        return BytesIO(response.content)
    except: return None

def generate_world_name():
    prefix = ["NEO", "VOID", "CORE", "OMEGA", "ZION", "ASTRO"]
    suffix = ["PRIME", "ALPHA", "STATION", "MATRIX", "ZONE"]
    return f"{random.choice(prefix)}_{random.choice(suffix)}_{random.randint(10,99)}"

# --- 3. DESIGN (CSS) ---
def apply_ui():
    accent = st.session_state.accent_color
    st.markdown(f"""
        <style>
        .stAppViewContainer {{
            background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.8)), 
                              url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; background-position: center !important;
        }}
        .main, .stAppHeader, .stAppViewBlockContainer {{ background: transparent !important; }}

        /* TEXTINSTÄLLNINGAR 1REM */
        .space-title {{ text-align: center; color: white; font-size: 1.5rem; letter-spacing: 2px; margin-top: 30px; }}
        .world-status {{ text-align: center; color: {accent}; font-family: monospace; letter-spacing: 5px; font-size: 1rem; text-transform: uppercase; opacity: 0.8; }}
        .label {{ text-align: center; color: {accent}; font-family: monospace; margin-top: 15px; letter-spacing: 2px; font-size: 1rem; text-transform: uppercase; }}

        /* KNAPPAR MED BILDER ISTÄLLET FÖR EMOJIS */
        div[data-testid="stButton"] > button {{
            width: 200px !important; height: 200px !important;
            border-radius: 40px !important; 
            border: 2px solid {accent}44 !important;
            background-size: cover !important;
            background-position: center !important;
            color: transparent !important; /* Döljer eventuell text i knappen */
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 15px 50px rgba(0,0,0,0.8) !important;
        }}

        /* SPECIFIKA BILDER FÖR VARJE KNAPP */
        div[data-testid="stButton"] > button[key="s"] {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="a"] {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="v"] {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="wp"] {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stButton"] > button[key="sys"] {{ background-image: url('https://images.unsplash.com') !important; }}
        
        div[data-testid="stButton"] > button:hover {{
            transform: scale(1.1) translateY(-10px) !important;
            border-color: {accent} !important;
            box-shadow: 0 0 70px {accent}66 !important;
        }}

        /* KNAPPAR I FÖNSTER */
        div[data-testid="stButton"] button {{
            font-size: 1rem !important; letter-spacing: 1px !important; padding: 5px 15px !important;
            background: rgba(255,255,255,0.1) !important;
            color: white !important;
            border-radius: 10px !important;
        }}
        
        .window {{ background: rgba(0, 5, 10, 0.98) !important; backdrop-filter: blur(50px); border: 1px solid {accent}11; border-radius: 25px; padding: 30px; color: white; }}
        h2 {{ font-size: 1.2rem !important; font-family: monospace; opacity: 0.9; }}
        textarea, input {{ font-size: 1rem !important; font-family: monospace !important; background: transparent !important; color: {accent} !important; border: 1px solid {accent}22 !important; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.active_window is None:
    st.markdown("<h1 class='space-title'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='world-status'>{st.session_state.world_name}</p>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    _, c1, c2, c3, c4, c5, _ = st.columns([0.1, 1, 1, 1, 1, 1, 0.1])
    
    with c1:
        if st.button(" ", key="s"): st.session_state.active_window = "SYNTH"; st.rerun()
        st.markdown('<p class="label">SYNTH</p>', unsafe_allow_html=True)
    with c2:
        if st.button(" ", key="a"): st.session_state.active_window = "AUDIO"; st.rerun()
        st.markdown('<p class="label">AUDIO</p>', unsafe_allow_html=True)
    with c3:
        if st.button(" ", key="v"): st.session_state.active_window = "VIDEO"; st.rerun()
        st.markdown('<p class="label">VIDEO</p>', unsafe_allow_html=True)
    with c4:
        if st.button(" ", key="wp"): st.session_state.active_window = "ENGINE"; st.rerun()
        st.markdown('<p class="label">ENGINE</p>', unsafe_allow_html=True)
    with c5:
        if st.button(" ", key="sys"): st.session_state.active_window = "SYSTEM"; st.rerun()
        st.markdown('<p class="label">SYSTEM</p>', unsafe_allow_html=True)

# --- 5. WINDOW MANAGER ---
else:
    st.markdown("<br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.2, 1, 0.2])
    with win_col:
        st.markdown('<div class="window">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()

        if st.session_state.active_window == "ENGINE":
            bg_p = st.text_area("MATRIX_COMMAND:", placeholder="Beskriv din nya värld...")
            theme_color = st.color_picker("TEMA_FÄRG:", st.session_state.accent_color)
            if st.button("EXEC_ENVIRONMENT_SYNC", use_container_width=True):
                with st.status("..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": bg_p, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = res
                    st.session_state.accent_color = theme_color
                    st.session_state.world_name = generate_world_name()
                st.rerun()

        elif st.session_state.active_window == "SYNTH":
            p = st.text_area("IMAGE_PROMPT:")
            if st.button("GENERATE", use_container_width=True):
                with st.status("..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res:
                st.image(st.session_state.synth_res)
                data = get_media_data(st.session_state.synth_res)
                if data: st.download_button("DOWNLOAD", data, "art.png", "image/png")

        st.markdown('</div>', unsafe_allow_html=True)


















