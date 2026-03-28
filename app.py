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
VERSION = "NR 1.1.8" 
st.set_page_config(page_title=f"MAXIMUSIK AI OS - {VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR & CLEANER ---
def get_safe_filename(text):
    if not text: return "genererad_fil"
    clean = re.sub(r'[^a-zA-Z0-9åäöÅÄÖ]', '_', text)
    return f"MAX_{clean[:30]}"

def sanitize_url(output):
    if not output: return None
    if isinstance(output, list): target = output[0]
    elif hasattr(output, 'url'): target = str(output.url)
    else: target = str(output)
    
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
        "video_library": [],
        "accent": "#00f2ff", 
        "last_img": None,
        "last_vid": None,
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
        background-size: cover !important; background-attachment: fixed !important;
    }}
    .glass {{ 
        background: rgba(0, 10, 30, 0.75); backdrop-filter: blur(40px); 
        border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px;
    }}
    .stButton>button {{ 
        border: 1px solid {accent}66 !important; background: {accent}11 !important; 
        color: white !important; border-radius: 12px; font-weight: bold; width: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
c_nav, c_dim = st.columns([0.8, 0.2])
with c_nav:
    nc = st.columns(6)
    if nc[0].button("🏠"): st.session_state.page = "SYNTH"; st.rerun()
    if nc[1].button("🪄"): st.session_state.page = "SYNTH"; st.rerun()
    if nc[2].button("🎧"): st.session_state.page = "AUDIO"; st.rerun()
    if nc[3].button("🎬"): st.session_state.page = "MOVIE"; st.rerun()
    if nc[4].button("📚"): st.session_state.page = "ARKIV"; st.rerun()
with c_dim:
    st.session_state.bg_opacity = st.slider("DIM", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---

if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 NEURAL SYNTH STATION</h2>", unsafe_allow_html=True)
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Beskriv visionen...")
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
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🎬 CINEMA OS (SVD-XT ENGINE)</h2>", unsafe_allow_html=True)
    st.info("SVD-XT kräver en startbild. Generera en bild i SYNTH först.")
    
    if st.session_state.last_img:
        st.image(st.session_state.last_img, caption="Startpunkt för animation", width=300)
        if st.button("🎬 ANIMERA BILD"):
            with st.status("Bearbetar neural rörelse (SVD-XT)..."):
                try:
                    # Spara bytes till temporär fil för uppladdning
                    with open("temp_anim.png", "wb") as f:
                        f.write(st.session_state.last_img)
                    
                    # Kör Stable Video Diffusion
                    output = replicate.run(
                        "stability-ai/stable-video-diffusion:ac7327c20fcb035902adbf7705d59611f6921055b51481855a2983a2d8d0030c",
                        input={"input_image": open("temp_anim.png", "rb"), "video_length": "25_frames_fps_6"}
                    )
                    vid_url = sanitize_url(output)
                    if vid_url:
                        st.session_state.last_vid = vid_url
                        st.session_state.video_library.append({"id": time.time(), "url": vid_url, "prompt": "Animation"})
                        st.rerun()
                except Exception as e:
                    st.error(f"Cinema Error: {e}")
    else:
        st.warning("Gå till SYNTH och skapa en bild först!")

    if st.session_state.last_vid:
        st.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    t_img, t_vid = st.tabs(["🖼️ BILDER", "🎬 FILMER"])
    with t_img:
        for item in reversed(st.session_state.library):
            st.image(item['data'], width=300)
    with t_vid:
        for v in reversed(st.session_state.video_library):
            st.video(v['url'])
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
