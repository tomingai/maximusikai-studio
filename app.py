import replicate
import os
import json
import time
import re
from datetime import datetime
import streamlit as st
import requests

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.3.6-MOVIE-PRO"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR & CLEANER (Frysta & Förstärkta) ---
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
        "page": "SYNTH", "library": [], "audio_library": [], "movie_library": [],
        "accent": "#00f2ff", "last_img": None, "last_audio": None, "last_vid": None,
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
    .neural-console {{ background: rgba(0,0,0,0.8); border: 1px solid {accent}44; padding: 12px; border-radius: 8px; font-family: monospace; color: {accent}; font-size: 0.8rem; margin-top: 10px; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
c_nav, c_dim = st.columns([0.75, 0.25])
with c_nav:
    nc = st.columns(6)
    nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",False), ("🎬","MOVIE",False), ("📚","ARKIV",False), ("⚙️","SYSTEM",True)]
    for i, (icon, target, locked) in enumerate(nav):
        if not locked:
            if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
        else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)
with c_dim:
    st.session_state.bg_opacity = st.slider("DIM", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---

# --- SYNTH STATION ---
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
    if st.session_state.last_img: st.image(st.session_state.last_img, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- MOVIE STATION (Med Process-logg) ---
elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🎬 MOVIE GENERATOR</h2>", unsafe_allow_html=True)
    
    movie_mode = st.radio("METOD:", ["Text-to-Video", "Image-to-Video (Från Arkiv)"], horizontal=True)
    
    movie_input_prompt = ""
    image_to_animate = None

    if movie_mode == "Image-to-Video (Från Arkiv)":
        if not st.session_state.library:
            st.warning("Arkivet är tomt.")
        else:
            img_options = {f"Bild: {img['prompt'][:30]}...": img for i, img in enumerate(reversed(st.session_state.library))}
            choice = st.selectbox("VÄLJ BILD ATT ANIMERA:", list(img_options.keys()))
            image_to_animate = img_options[choice]['url']
            movie_input_prompt = st.text_input("BESKRIV RÖRELSEN:", placeholder="Kameran panorerar åt höger...")
            st.image(image_to_animate, width=300)
    else:
        movie_input_prompt = st.text_input("VAD SKALL HÄNDA I FILMEN?", placeholder="En rymdfärja landar på Mars...")

    if st.button("🎬 STARTA RENDERING"):
        if movie_input_prompt or image_to_animate:
            console_placeholder = st.empty()
            logs = ["› INITIALIZING MOVIE ENGINE..."]
            console_placeholder.markdown(f'<div class="neural-console">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
            
            with st.spinner(""):
                # Steg 1: Analys
                logs.append("› PREPARING SOURCE MATERIAL...")
                console_placeholder.markdown(f'<div class="neural-console">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                
                params = {"prompt": movie_input_prompt}
                if image_to_animate:
                    logs.append(f"› IMAGE DETECTED: {image_to_animate[:30]}...")
                    params["image"] = image_to_animate
                
                # Steg 2: Rendering
                logs.append("› CONNECTING TO LUMA DREAM MACHINE...")
                console_placeholder.markdown(f'<div class="neural-console">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                
                vid_url = safe_replicate_run("luma/dream-machine", params)
                
                if vid_url:
                    logs.append("› RENDERING COMPLETE. FINALIZING MP4...")
                    console_placeholder.markdown(f'<div class="neural-console">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
                    st.session_state.last_vid = vid_url
                    st.session_state.movie_library.append({"id": time.time(), "url": vid_url, "prompt": movie_input_prompt if movie_input_prompt else "Animated Image"})
                    time.sleep(1)
                    st.rerun()
    
    if st.session_state.last_vid: st.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

# --- AUDIO & ARKIV (BEVARADE) ---
elif st.session_state.page == "AUDIO":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    audio_p = st.text_input("BESKRIV LJUDET:", placeholder="80s synthwave...")
    if st.button("🎵 KOMPONERA"):
        if audio_p:
            res = safe_replicate_run("facebookresearch/musicgen", {"prompt": audio_p, "duration": 8})
            if res:
                st.session_state.last_audio = res
                st.session_state.audio_library.append({"id": time.time(), "url": res, "prompt": audio_p})
                st.rerun()
    if st.session_state.last_audio: st.audio(st.session_state.last_audio)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🖼️ BILDER", "🎵 LJUD", "🎬 FILMER"])
    with t1:
        grid = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.image(item['url'], use_container_width=True)
                if st.button("VÄLJ", key=f"s_{item['id']}"): st.session_state.wallpaper = item['url']; st.rerun()
                if st.button("SLÄNG", key=f"d_{item['id']}"): st.session_state.library = [x for x in st.session_state.library if x['id'] != item['id']]; st.rerun()
    with t2:
        for item in reversed(st.session_state.audio_library):
            st.audio(item['url']); st.markdown(f"*{item['prompt']}*")
    with t3:
        for item in reversed(st.session_state.movie_library):
            st.video(item['url']); st.markdown(f"*{item['prompt']}*")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK OS {VERSION}</div>', unsafe_allow_html=True)























































































































































































































































































































































































































































































































































