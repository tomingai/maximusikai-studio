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
    .stButton>button, .stDownloadButton>button {{ 
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
                        st.session_state.library.append({"id": time.time(), "data": resp.content, "url": url, "prompt": user_p})
                        st.rerun()
    if st.session_state.last_img:
        st.image(st.session_state.last_img, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🎬 CINEMA OS (SVD)</h2>", unsafe_allow_html=True)
    if st.session_state.last_img:
        st.image(st.session_state.last_img, caption="Startbild klar", width=300)
        motion = st.slider("RÖRELSE:", 1, 255, 127)
        if st.button("🎬 ANIMERA"):
            progress_bar = st.progress(0)
            try:
                img_stream = io.BytesIO(st.session_state.last_img)
                model = replicate.models.get("stability-ai/stable-video-diffusion")
                prediction = replicate.predictions.create(version=model.latest_version.id, input={"input_image": img_stream, "motion_bucket_id": motion})
                start_time = time.time()
                while prediction.status not in ["succeeded", "failed", "canceled"]:
                    elapsed = int(time.time() - start_time)
                    progress_bar.progress(min(elapsed * 2, 99))
                    time.sleep(4)
                    prediction.reload()
                if prediction.status == "succeeded":
                    progress_bar.progress(100)
                    vid_url = sanitize_url(prediction.output)
                    st.session_state.last_vid = vid_url
                    st.session_state.video_library.append({"id": time.time(), "url": vid_url, "prompt": "Animation"})
                    st.rerun()
            except Exception as e: st.error(f"Error: {e}")
    else: st.warning("Skapa bild i SYNTH först.")
    if st.session_state.last_vid:
        st.video(st.session_state.last_vid)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    t_img, t_vid = st.tabs(["🖼️ BILDER", "🎬 FILMER"])
    with t_img:
        if not st.session_state.library: st.info("Bildarkivet är tomt.")
        else:
            grid = st.columns(3)
            for i, item in enumerate(list(reversed(st.session_state.library))):
                with grid[i % 3]:
                    st.image(item['data'], use_container_width=True)
                    if st.button("🖼️", key=f"bg_{item['id']}"):
                        st.session_state.wallpaper = item['url']; st.rerun()
                    if st.button("🗑️", key=f"del_{item['id']}"):
                        st.session_state.library = [img for img in st.session_state.library if img['id'] != item['id']]; st.rerun()
    with t_vid:
        if not st.session_state.video_library: st.info("Videoarkivet är tomt.")
        else:
            for v in reversed(st.session_state.video_library):
                st.video(v['url'])
                # NYTT: Direktlänk för nedladdning av video
                st.markdown(f"[📥 LADDA NER VIDEO]({v['url']})", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_v_{v['id']}"):
                    st.session_state.video_library = [vid for vid in st.session_state.video_library if vid['id'] != v['id']]; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK AI OS {VERSION}</div>', unsafe_allow_html=True)
