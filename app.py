import replicate
import os
import json
import time
import re
import io
from datetime import datetime
import streamlit as st
import requests

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "NR 1.1" 
st.set_page_config(page_title=f"MAXIMUSIK AI OS - {VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR & CLEANER ---
def clean_prompt(text):
    if not text: return ""
    return str(text).replace('"', '').replace('Prompt:', '').strip()

def get_safe_filename(text):
    if not text: return "genererad_fil"
    clean = re.sub(r'[^a-zA-Z0-9åäöÅÄÖ]', '_', text)
    return f"MAX_{clean[:30]}"

def sanitize_url(output):
    if not output: return None
    target = output if isinstance(output, list) else output
    if hasattr(target, 'url'): return str(target.url)
    url = str(target)
    for char in ["['", "']", "[", "]", "'", '"']:
        url = url.replace(char, "")
    return url.strip()

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", 
        "library": [], 
        "audio_library": [],
        "video_library": [], # NYTT FÖR 1.1
        "accent": "#00f2ff", 
        "last_img": None,
        "last_vid": None,    # NYTT FÖR 1.1
        "last_prompt": "bild",
        "wallpaper": "https://images.unsplash.com",
        "bg_opacity": 0.80
    })

# --- 4. UI ENGINE ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,{st.session_state.bg_opacity}), rgba(0,0,0,{st.session_state.bg_opacity})), 
                    url("{st.session_state.wallpaper}"); 
        background-size: cover !important; background-position: center !important;
        background-repeat: no-repeat !important; background-attachment: fixed !important;
    }}
    .glass {{ 
        background: rgba(0, 10, 30, 0.75); backdrop-filter: blur(40px); 
        border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px;
    }}
    h1, h2, h3, label, p {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }}
    .stButton>button, .stDownloadButton>button {{ 
        border: 1px solid {accent}66 !important; background: {accent}11 !important; 
        color: white !important; border-radius: 12px; font-weight: bold; width: 100%;
    }}
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
            if nc[i].button(icon, key=f"nav_{target}"): 
                st.session_state.page = target
                st.rerun()
        else: 
            nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)
with c_dim:
    st.session_state.bg_opacity = st.slider("DIM", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---

# MODULE: SYNTH (OFÖRÄNDRAD FRÅN NR 1)
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 NEURAL SYNTH STATION</h2>", unsafe_allow_html=True)
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Beskriv din vision...")
    
    if st.button("🚀 GENERERA BILD"):
        if user_p:
            with st.status("Neural kedja aktiv..."):
                st.session_state.last_prompt = user_p
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": user_p, "aspect_ratio": "16:9"})
                url = sanitize_url(res)
                if url:
                    resp = requests.get(url, timeout=15)
                    if resp.status_code == 200:
                        st.session_state.last_img = resp.content
                        st.session_state.library.append({"id": time.time(), "data": resp.content, "prompt": user_p})
                        st.rerun()
    
    if st.session_state.last_img:
        st.image(st.session_state.last_img, use_container_width=True)
        fname = get_safe_filename(st.session_state.last_prompt)
        buf = io.BytesIO(st.session_state.last_img)
        buf.seek(0)
        st.download_button(label=f"💾 SPARA {fname}.jpg", data=buf, file_name=f"{fname}.jpg", mime="image/jpeg")
    st.markdown('</div>', unsafe_allow_html=True)

# MODULE: MOVIE (NY SUB-APP I 1.1)
elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🎬 CINEMA OS (SUB-APP)</h2>", unsafe_allow_html=True)
    
    vid_p = st.text_input("ANIMERA DIN VISION:", placeholder="Bilar som kör i regn...")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎬 SKAPA FILM FRÅN TEXT"):
            if vid_p:
                with st.status("Renderar 5s Cinematic Video..."):
                    # Använder Luma Dream Machine för video
                    output = replicate.run("luma/dream-machine", input={"prompt": vid_p})
                    vid_url = sanitize_url(output)
                    if vid_url:
                        st.session_state.last_vid = vid_url
                        st.session_state.video_library.append({"id": time.time(), "url": vid_url, "prompt": vid_p})
                        st.rerun()
    with c2:
        if st.session_state.last_img:
            if st.button("🪄 ANIMERA SENASTE BILD"):
                st.info("Funktion under utveckling: Skickar SYNTH-bild till Luma...")
        else:
            st.warning("Generera en bild i SYNTH först för Image-to-Video.")

    if st.session_state.last_vid:
        st.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

# MODULE: ARKIV (UPPDATERAD FÖR VIDEO)
elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🖼️ BILDER", "🎬 FILMER"])
    
    with tab1:
        if not st.session_state.library: st.info("Bildarkivet är tomt.")
        else:
            grid = st.columns(3)
            for i, item in enumerate(list(reversed(st.session_state.library))):
                with grid[i % 3]:
                    st.image(item['data'], use_container_width=True)
                    if st.button("SLÄNG", key=f"del_img_{item['id']}"):
                        st.session_state.library = [img for img in st.session_state.library if img['id'] != item['id']]
                        st.rerun()
    
    with tab2:
        if not st.session_state.video_library: st.info("Videoarkivet är tomt.")
        else:
            for v_item in reversed(st.session_state.video_library):
                st.video(v_item['url'])
                st.caption(f"Prompt: {v_item['prompt']}")
                if st.button("RADERA", key=f"del_vid_{v_item['id']}"):
                    st.session_state.video_library = [v for v in st.session_state.video_library if v['id'] != v_item['id']]
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# (AUDIO-modulen lämnas som original)
elif st.session_state.page == "AUDIO":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🎧 AUDIO GENERATOR</h2>", unsafe_allow_html=True)
    audio_prompt = st.text_input("BESKRIV LJUDET:", placeholder="Dark techno loop...")
    if st.button("🎵 GENERERA"):
        if audio_prompt:
            res = replicate.run("facebookresearch/musicgen", input={"prompt": audio_prompt, "duration": 8})
            url = sanitize_url(res)
            if url:
                st.session_state.audio_library.append({"id": time.time(), "url": url, "prompt": audio_prompt})
                st.rerun()
    for item in reversed(st.session_state.audio_library):
        st.audio(item['url'])
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
