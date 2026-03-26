import streamlit as st
import replicate
import os
import requests
import json
import base64
from datetime import datetime
from io import BytesIO
from PIL import Image

# --- 1. SYSTEM CONFIG & BOOT ---
st.set_page_config(page_title="MAXIMUSIKAI PREMIER", layout="wide", initial_sidebar_state="expanded")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. THEME ENGINE (Hanterar bakgrunder per flik) ---
WORKSPACES = {
    "⚡ SYNTHESIS": {
        "bg": "https://images.unsplash.com", # Galax/Rymd
        "accent": "#00f2ff",
        "tag": "NEURAL_VISUAL_CORE"
    },
    "🎵 AUDIO_LAB": {
        "bg": "https://images.unsplash.com", # Studio/Synth
        "accent": "#ff00ea",
        "tag": "SONIC_WAVEFORM_SYNTH"
    },
    "🎬 VIDEO_MOTION": {
        "bg": "https://images.unsplash.com", # Mörk Skog
        "accent": "#00ff41",
        "tag": "TEMPORAL_FLUX_ENGINE"
    },
    "📦 VAULT": {
        "bg": "https://images.unsplash.com", # Digitalt Nätverk
        "accent": "#ffffff",
        "tag": "LOCAL_ASSET_ARCHIVE"
    }
}

# --- 3. SESSION STATE INITIALIZATION ---
if "vault" not in st.session_state: st.session_state.vault = []
if "last_res" not in st.session_state: st.session_state.last_res = None
if "terminal_logs" not in st.session_state: st.session_state.terminal_logs = []

def log_event(msg):
    st.session_state.terminal_logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# --- 4. DYNAMIC UI INJECTOR ---
with st.sidebar:
    st.title("MAXIMUS_OS")
    active_ws = st.selectbox("WORKSPACE_SELECT", list(WORKSPACES.keys()))
    config = WORKSPACES[active_ws]
    
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), 
                        url("{config['bg']}") !important;
            background-size: cover !important;
            background-attachment: fixed !important;
            transition: 1s ease-in-out;
        }}
        .stButton>button {{
            border: 1px solid {config['accent']} !important;
            color: {config['accent']} !important;
            background: rgba(0,0,0,0.4) !important;
            text-transform: uppercase; letter-spacing: 2px;
        }}
        .terminal-box {{
            background: rgba(0,0,0,0.8); border: 1px solid {config['accent']};
            padding: 10px; font-family: 'JetBrains Mono'; font-size: 10px;
            color: {config['accent']}; height: 150px; overflow-y: auto;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    st.info(f"STATUS: {config['tag']}")

# --- 5. WORKSPACE LOGIC ---

if active_ws == "⚡ SYNTHESIS":
    st.markdown("## `NEURAL_GENERATION`")
    col_in, col_out = st.columns([1, 2])
    with col_in:
        prompt = st.text_area("VISUAL_PROMPT", placeholder="Deep forest in space, bioluminescent plants...", height=200)
        ratio = st.selectbox("ASPECT", ["1:1", "16:9", "9:16"])
        if st.button("EXECUTE_RENDER"):
            with st.status("GENERATING..."):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": ratio})
                st.session_state.last_res = res[0] if isinstance(res, list) else res
                st.session_state.vault.append({"url": st.session_state.last_res, "prompt": prompt, "type": "IMAGE"})
                log_event("IMAGE_GENERATED")
            st.rerun()
    with col_out:
        if st.session_state.last_res:
            st.image(st.session_state.last_res, use_container_width=True)

elif active_ws == "🎵 AUDIO_LAB":
    st.markdown("## `SONIC_SYNTHESIZER`")
    if st.session_state.last_res:
        st.image(st.session_state.last_res, width=300)
        st.markdown("<label>IMAGE_TO_MUSIC_PARAMETERS</label>", unsafe_allow_html=True)
        duration = st.slider("DURATION (SEC)", 5, 30, 10)
        if st.button("GENERATE_SOUNDTRACK"):
            with st.status("COMPOSING_AUDIO..."):
                # Simulerat anrop (Här lägger vi MusicGen i nästa steg)
                log_event("AUDIO_PROCESS_INITIATED")
                st.success("Musikmotorn är redo för implementation.")
    else:
        st.warning("Ladda en bild i SYNTHESIS först för att skapa musik till den.")

elif active_ws == "🎬 VIDEO_MOTION":
    st.markdown("## `TEMPORAL_ANIMATION`")
    st.info("Här kan du förvandla din rymdskog till en levande video.")
    if st.button("START_VIDEO_RENDER"):
        log_event("VIDEO_RENDER_QUEUED")

elif active_ws == "📦 VAULT":
    st.markdown("## `DATABASE_ARCHIVE`")
    if st.session_state.vault:
        cols = st.columns(4)
        for i, item in enumerate(reversed(st.session_state.vault)):
            with cols[i % 4]:
                st.image(item["url"])
                st.caption(item["prompt"][:30] + "...")

# --- 6. LOGS (Alltid synliga i sidebaren) ---
with st.sidebar:
    st.markdown("### `SYSTEM_LOGS`")
    logs = "\n".join(st.session_state.terminal_logs[::-1])
    st.markdown(f'<div class="terminal-box">{logs.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
rerun()



