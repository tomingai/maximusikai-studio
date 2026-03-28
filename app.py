import replicate
import os
import json
import time
from datetime import datetime
import streamlit as st

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.3.6-GLOW-LUMINA"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR & CLEANER (Regel 3: Fix för FileOutput-objekt) ---
def clean_prompt(text):
    if not text: return ""
    return str(text).replace('"', '').replace('Prompt:', '').strip()

def sanitize_url(output):
    if not output: return None
    if hasattr(output, 'url'): return str(output.url)
    if isinstance(output, list) and len(output) > 0:
        val = output[0]
        return str(val.url) if hasattr(val, 'url') else str(val)
    url = str(output)
    for char in ["['", "']", "[", "]", "'", '"']: url = url.replace(char, "")
    return url.strip()

def safe_replicate_run(model, input_data):
    if not os.environ.get("REPLICATE_API_TOKEN"):
        st.error("🔑 API-nyckel saknas!")
        return None
    try:
        res = replicate.run(model, input=input_data)
        if "llama" in model: return res
        return sanitize_url(res)
    except Exception as e:
        st.error(f"Neural Error: {e}")
        return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "audio_library": [],
        "accent": "#00f2ff", "last_img": None, "last_audio": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Cinematic", "bg_opacity": 0.80
    })

# --- 4. UI ENGINE ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,{st.session_state.bg_opacity}), rgba(0,0,0,{st.session_state.bg_opacity})), 
                    url("{st.session_state.wallpaper}"); 
        background-size: cover !important; background-attachment: fixed !important;
    }}
    .glass {{ 
        background: rgba(0, 10, 30, 0.75); backdrop-filter: blur(40px); 
        border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px;
    }}
    h1, h2, h3, label, p {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }}
    .stButton>button {{ border: 1px solid {accent}66 !important; background: {accent}11 !important; color: white !important; border-radius: 12px; font-weight: bold; width: 100%; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
c_nav, c_dim = st.columns([0.75, 0.25])
with c_nav:
    nc = st.columns(6)
    nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",False), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("⚙️","SYSTEM",True)]
    for i, (icon, target, locked) in enumerate(nav):
        if not locked:
            if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
        else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0;">{icon}</p>', unsafe_allow_html=True)
with c_dim:
    st.session_state.bg_opacity = st.slider("DIM", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 SYNTH STATION</h2>", unsafe_allow_html=True)
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Beskriv visionen...")
    if st.button("🚀 GENERERA BILD"):
        if user_p:
            with st.status("Neural kedja aktiv..."):
                url = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": user_p, "aspect_ratio": "16:9"})
                if url:
                    st.session_state.last_img = url
                    st.session_state.library.append({"id": time.time(), "url": url, "prompt": user_p})
                    st.rerun()
    if st.session_state.last_img:
        st.image(st.session_state.last_img, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "AUDIO":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🎧 AUDIO GENERATOR</h2>", unsafe_allow_html=True)
    audio_prompt = st.text_input("BESKRIV LJUDET:", placeholder="Dark techno loop...")
    duration = st.slider("LÄNGD (SEK):", 5, 20, 8)
    if st.button("🎵 KOMPONERA"):
        if audio_prompt:
            with st.status("Komponerar..."):
                res = safe_replicate_run("facebookresearch/musicgen", {"prompt": audio_prompt, "duration": duration})
                if res:
                    st.session_state.last_audio = res
                    st.session_state.audio_library.append({"id": time.time(), "url": res, "prompt": audio_prompt})
                    st.rerun()
    if st.session_state.last_audio:
        st.audio(st.session_state.last_audio)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🖼️ BILDER", "🎵 LJUD"])
    with t1:
        grid = st.columns(3)
        for i, img in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.image(img['url'], use_container_width=True)
                if st.button("VÄLJ", key=f"set_{img['id']}"):
                    st.session_state.wallpaper = img['url']; st.rerun()
                if st.button("SLÄNG", key=f"del_{img['id']}"):
                    st.session_state.library = [x for x in st.session_state.library if x['id'] != img['id']]
                    st.rerun()
    with t2:
        for audio in reversed(st.session_state.audio_library):
            st.audio(audio['url'])
            if st.button("RADERA", key=f"del_aud_{audio['id']}"):
                st.session_state.audio_library = [x for x in st.session_state.audio_library if x['id'] != audio['id']]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)














































































































































































































































































































































































































































































































































































