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
VERSION = "NR 1.1.9" 
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
    url = ""
    if isinstance(output, list) and len(output) > 0: url = str(output)
    elif hasattr(output, 'url'): url = str(output.url)
    else: url = str(output)
    url = url.replace("['", "").replace("']", "").replace("[", "").replace("]", "").replace("'", "").replace('"', "").strip()
    return url if url.startswith("http") else None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", 
        "library": [], 
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
        background-position: center !important;
    }}
    .glass {{ 
        background: rgba(0, 10, 30, 0.75); backdrop-filter: blur(40px); 
        border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px;
    }}
    .stImage, .stVideo {{
        max-width: 80% !important;
        margin: auto !important;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
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
            bar = st.progress(0)
            timer_text = st.empty()
            start = time.time()
            try:
                prediction = replicate.predictions.create(
                    model="black-forest-labs/flux-schnell",
                    input={"prompt": user_p, "aspect_ratio": "16:9"}
                )
                while prediction.status not in ["succeeded", "failed", "canceled"]:
                    elapsed = int(time.time() - start)
                    bar.progress(min(elapsed * 20, 99))
                    timer_text.markdown(f"**Syntetiserar:** {prediction.status}... ({elapsed}s)")
                    time.sleep(0.5)
                    prediction.reload()
                
                if prediction.status == "succeeded":
                    url = sanitize_url(prediction.output)
                    resp = requests.get(url, timeout=20)
                    if resp.status_code == 200:
                        st.session_state.last_img = resp.content
                        st.session_state.library.append({"id": time.time(), "data": resp.content, "url": url, "prompt": user_p})
                        st.rerun()
            except Exception as e: st.error(f"Synth Error: {e}")
                
    if st.session_state.last_img:
        _, mid, _ = st.columns([0.1, 0.8, 0.1])
        with mid: st.image(st.session_state.last_img, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🎬 CINEMA OS (SVD)</h2>", unsafe_allow_html=True)
    if st.session_state.last_img:
        _, mid_pre, _ = st.columns([0.3, 0.4, 0.3])
        with mid_pre: st.image(st.session_state.last_img, caption="Startpunkt", use_container_width=True)
        
        motion = st.slider("RÖRELSE:", 1, 255, 127)
        if st.button("🎬 ANIMERA"):
            bar = st.progress(0)
            timer_text = st.empty()
            start = time.time()
            try:
                img_stream = io.BytesIO(st.session_state.last_img)
                prediction = replicate.predictions.create(
                    model="stability-ai/stable-video-diffusion",
                    input={"input_image": img_stream, "motion_bucket_id": motion}
                )
                while prediction.status not in ["succeeded", "failed", "canceled"]:
                    elapsed = int(time.time() - start)
                    bar.progress(min(elapsed * 2, 99))
                    timer_text.markdown(f"**Renderar film:** {prediction.status}... ({elapsed}s)")
                    time.sleep(3)
                    prediction.reload()
                if prediction.status == "succeeded":
                    st.session_state.last_vid = sanitize_url(prediction.output)
                    st.session_state.video_library.append({"id": time.time(), "url": st.session_state.last_vid, "prompt": "Animation"})
                    st.rerun()
            except Exception as e: st.error(f"Movie Error: {e}")
    
    if st.session_state.last_vid:
        _, mid_vid, _ = st.columns([0.1, 0.8, 0.1])
        with mid_vid: st.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    t_img, t_vid = st.tabs(["🖼️ BILDER", "🎬 FILMER"])
    with t_img:
        grid = st.columns(4)
        for i, item in enumerate(list(reversed(st.session_state.library))):
            with grid[i % 4]:
                st.image(item['data'], use_container_width=True)
                c1, c2 = st.columns(2)
                if c1.button("🖼️", key=f"bg_{item['id']}"): st.session_state.wallpaper = item['url']; st.rerun()
                if c2.button("🗑️", key=f"del_{item['id']}"): 
                    st.session_state.library = [img for img in st.session_state.library if img['id'] != item['id']]; st.rerun()
    with t_vid:
        for v in reversed(st.session_state.video_library):
            _, mid_v, _ = st.columns([0.2, 0.6, 0.2])
            with mid_v:
                st.video(v['url'])
                st.markdown(f"[📥 HÄMTA VIDEO]({v['url']})", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
