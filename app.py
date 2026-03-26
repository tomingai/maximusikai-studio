import streamlit as st
import replicate
import os
import requests
import json
from datetime import datetime

# --- 1. SYSTEM CONFIG & BOOT ---
st.set_page_config(page_title="MAXIMUSIKAI PREMIER", layout="wide", initial_sidebar_state="expanded")

# API Setup
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. THEME ENGINE DATA ---
WORKSPACES = {
    "⚡ SYNTHESIS": {
        "bg": "https://images.unsplash.com",
        "accent": "#00f2ff",
        "tag": "NEURAL_VISUAL_CORE"
    },
    "🎵 AUDIO_LAB": {
        "bg": "https://images.unsplash.com",
        "accent": "#ff00ea",
        "tag": "SONIC_WAVEFORM_SYNTH"
    },
    "🎬 VIDEO_MOTION": {
        "bg": "https://images.unsplash.com",
        "accent": "#00ff41",
        "tag": "TEMPORAL_FLUX_ENGINE"
    },
    "📦 VAULT": {
        "bg": "https://images.unsplash.com",
        "accent": "#ffffff",
        "tag": "LOCAL_ASSET_ARCHIVE"
    }
}

# --- 3. SESSION STATE INITIALIZATION ---
if "vault" not in st.session_state: st.session_state.vault = []
if "last_res" not in st.session_state: st.session_state.last_res = None
if "last_audio" not in st.session_state: st.session_state.last_audio = None
if "terminal_logs" not in st.session_state: 
    st.session_state.terminal_logs = [f"[{datetime.now().strftime('%H:%M:%S')}] SYSTEM_READY"]

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
            transition: 0.8s ease-in-out;
        }}
        .stButton>button {{
            border: 1px solid {config['accent']} !important;
            color: {config['accent']} !important;
            background: rgba(0,0,0,0.2) !important;
            width: 100%; border-radius: 0px;
        }}
        .terminal-box {{
            background: rgba(0,0,0,0.9); border: 1px solid {config['accent']};
            padding: 10px; font-family: 'JetBrains Mono', monospace; font-size: 10px;
            color: {config['accent']}; height: 200px; overflow-y: auto;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- 5. WORKSPACE LOGIC ---

if active_ws == "⚡ SYNTHESIS":
    st.markdown(f"## `SYNTHESIS_UNIT // {config['accent']}`", unsafe_allow_html=True)
    col_in, col_out = st.columns([1, 1.5])
    with col_in:
        prompt = st.text_area("NEURAL_PROMPT", placeholder="Ex: Space forest, neon mushrooms...", height=200)
        ratio = st.selectbox("ASPECT_RATIO", ["1:1", "16:9", "9:16"])
        if st.button("EXECUTE_RENDER"):
            if prompt:
                with st.status("GENERATING_VISUALS..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt, "aspect_ratio": ratio})
                    st.session_state.last_res = res[0] if isinstance(res, list) else res
                    st.session_state.vault.append({"url": st.session_state.last_res, "prompt": prompt, "type": "IMAGE"})
                    log_event("VISUAL_RENDER_COMPLETE")
                st.rerun() # FIXAD: Använder st.rerun()

    with col_out:
        if st.session_state.last_res:
            st.image(st.session_state.last_res, use_container_width=True)

elif active_ws == "🎵 AUDIO_LAB":
    st.markdown("## `SONIC_SYNTHESIZER`")
    if st.session_state.last_res:
        c1, c2 = st.columns(2)
        with c1:
            st.image(st.session_state.last_res, caption="SOURCE_IMAGE", width=400)
        with c2:
            st.markdown("### `AUDIO_PARAMETERS`")
            audio_prompt = st.text_input("SONIC_DESCRIPTION", placeholder="E.g. Ambient space techno, 120bpm...")
            duration = st.slider("DURATION (SEC)", 5, 20, 10)
            
            if st.button("SYNTHESIZE_AUDIO"):
                with st.status("COMPOSING_SOUNDTRACK..."):
                    # Kör MusicGen baserat på bild-prompt eller audio-prompt
                    final_prompt = audio_prompt if audio_prompt else "ambient space music"
                    audio_res = replicate.run(
                        "facebookresearch/musicgen:7a76a8258a299f6600c61230623a39e2abc0fa15f8a0da54d9e50f3c5f201089",
                        input={"prompt": final_prompt, "duration": duration}
                    )
                    st.session_state.last_audio = audio_res
                    log_event("AUDIO_SYNTHESIS_COMPLETE")
                st.rerun() # FIXAD: Använder st.rerun()

        if st.session_state.last_audio:
            st.audio(st.session_state.last_audio)
    else:
        st.warning("PLEASE_GENERATE_IMAGE_IN_SYNTHESIS_FIRST")

elif active_ws == "🎬 VIDEO_MOTION":
    st.markdown("## `VIDEO_ENGINE`")
    st.info("VIDEO_FLUX_MODULE_PENDING")
    if st.button("INITIALIZE_TEMPORAL_LINK"):
        log_event("VIDEO_ENGINE_READY")

elif active_ws == "📦 VAULT":
    st.markdown("## `DATABASE_VAULT`")
    if st.session_state.vault:
        v_cols = st.columns(4)
        for i, item in enumerate(reversed(st.session_state.vault)):
            with v_cols[i % 4]:
                st.image(item["url"])
    else:
        st.write("VAULT_IS_EMPTY")

# --- 6. TERMINAL LOGS (Sidebar) ---
with st.sidebar:
    st.markdown("---")
    st.markdown("### `SYSTEM_LOGS`")
    log_content = "\n".join(st.session_state.terminal_logs[::-1])
    st.markdown(f'<div class="terminal-box">{log_content.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)



