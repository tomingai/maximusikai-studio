import streamlit as st
import replicate
import os
import requests
import random
from io import BytesIO

# --- 1. CONFIG ---
st.set_page_config(page_title="MAXIMUSIK AI GALAXY", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session State
if "active_window" not in st.session_state: st.session_state.active_window = None
if "synth_res" not in st.session_state: st.session_state.synth_res = None
if "world_name" not in st.session_state: st.session_state.world_name = "DEEP_SPACE_VOID"
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

def generate_random_prompt():
    subjects = ["nebula", "black hole", "supernova", "alien planet", "cybernetic moon"]
    colors = ["neon purple", "electric cyan", "deep crimson", "emerald green"]
    return f"Cinematic 8k shot of a {random.choice(subjects)} with {random.choice(colors)}, swirling cosmic dust."

def generate_world_name():
    prefix = ["NEO", "VOID", "AURA", "CYBER", "STAR", "CORE", "OMEGA"]
    suffix = ["PRIME", "ALPHA", "MATRIX", "SECTOR", "GALAXY", "ZONE"]
    return f"{random.choice(prefix)}_{random.choice(suffix)}_{random.randint(100,999)}"

# --- 3. DESIGN (CSS) ---
def apply_ui():
    accent = st.session_state.accent_color
    st.markdown(f"""
        <style>
        .stAppViewContainer {{
            background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.7)), 
                              url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; background-position: center !important;
        }}
        .main, .stAppHeader, .stAppViewBlockContainer {{ background: transparent !important; }}

        /* MIKROSKOPISK TEXT (10X MINDRE) */
        .space-title {{ text-align: center; color: white; font-size: 0.5rem; letter-spacing: 2px; margin-top: 20px; opacity: 0.5; }}
        .world-status {{ text-align: center; color: {accent}; font-family: monospace; letter-spacing: 4px; font-size: 0.3rem; text-transform: uppercase; opacity: 0.3; }}
        .label {{ text-align: center; color: {accent}; font-family: monospace; margin-top: 10px; letter-spacing: 2px; font-size: 0.3rem; text-transform: uppercase; opacity: 0.5; }}
        
        /* KNAPPAR SKRIVBORD */
        div[data-testid="stButton"] > button {{
            width: 200px !important; height: 200px !important;
            border-radius: 50px !important; border: 1px solid {accent}22 !important;
            background: rgba(255, 255, 255, 0.02) !important;
            backdrop-filter: blur(10px) !important;
        }}
        div[data-testid="stButton"] > button p {{
            font-size: 8rem !important; margin: 0 !important;
        }}

        /* MINIMALISTISKA KNAPPAR I FÖNSTER */
        div[data-testid="stButton"] button {{
            font-size: 0.4rem !important; letter-spacing: 1px !important; padding: 2px 5px !important;
        }}

        .window {{ background: rgba(0, 5, 10, 0.98) !important; backdrop-filter: blur(40px); border: 1px solid {accent}11; border-radius: 20px; padding: 20px; color: white; }}
        h2 {{ font-size: 0.6rem !important; opacity: 0.7; }}
        textarea, input {{ font-size: 0.5rem !important; font-family: monospace !important; background: transparent !important; color: {accent} !important; border: 1px solid {accent}11 !important; }}
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
        if st.button("🌌", key="s"): st.session_state.active_window = "SYNTH"; st.rerun()
        st.markdown('<p class="label">SYNTH</p>', unsafe_allow_html=True)
    with c2:
        if st.button("👽", key="a"): st.session_state.active_window = "AUDIO"; st.rerun()
        st.markdown('<p class="label">AUDIO</p>', unsafe_allow_html=True)
    with c3:
        if st.button("🛸", key="v"): st.session_state.active_window = "VIDEO"; st.rerun()
        st.markdown('<p class="label">VIDEO</p>', unsafe_allow_html=True)
    with c4:
        if st.button("🖼️", key="wp"): st.session_state.active_window = "ENGINE"; st.rerun()
        st.markdown('<p class="label">ENGINE</p>', unsafe_allow_html=True)
    with c5:
        if st.button("☄️", key="sys"): st.session_state.active_window = "SYSTEM"; st.rerun()
        st.markdown('<p class="label">SYSTEM</p>', unsafe_allow_html=True)

# --- 5. WINDOW MANAGER ---
else:
    st.markdown("<br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.2, 1, 0.2])
    with win_col:
        st.markdown('<div class="window">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.95, 0.05])
        h1.markdown(f"<h2>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()

        if st.session_state.active_window == "ENGINE":
            if st.button("BRAIN_RANDOM", use_container_width=True):
                st.session_state.temp_prompt = generate_random_prompt()
                st.rerun()
            bg_p = st.text_area("CMD:", value=st.session_state.get('temp_prompt', ''))
            theme_color = st.color_picker("HEX:", st.session_state.accent_color)
            if st.button("EXEC_SYNC", use_container_width=True):
                with st.status("..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": bg_p, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = res
                    st.session_state.accent_color = theme_color
                    st.session_state.world_name = generate_world_name()
                    st.session_state.bg_gallery.append(res)
                st.rerun()

        elif st.session_state.active_window == "SYNTH":
            p = st.text_area("GEN:")
            if st.button("RUN", use_container_width=True):
                with st.status("..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res:
                st.image(st.session_state.synth_res)
                data = get_media_data(st.session_state.synth_res)
                if data: st.download_button("SAVE", data, "art.png", "image/png")

        st.markdown('</div>', unsafe_allow_html=True)

















