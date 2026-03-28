import replicate
import os
import json
import time
import re
import io # NY: För stabilare nedladdning
from datetime import datetime
import streamlit as st
import requests

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.4.2-GLOW-STABLE"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR & CLEANER ---
def clean_prompt(text):
    if not text: return ""
    return str(text).replace('"', '').replace('Prompt:', '').strip()

def get_safe_filename(text):
    if not text: return "genererad_bild"
    clean = re.sub(r'[^a-zA-Z0-9åäöÅÄÖ]', '_', text)
    return f"MAX_{clean[:30]}"

def sanitize_url(output):
    if not output: return None
    target = output[0] if isinstance(output, list) else output
    if hasattr(target, 'url'): return str(target.url)
    url = str(target)
    for char in ["['", "']", "[", "]", "'", '"']:
        url = url.replace(char, "")
    return url.strip()

def safe_replicate_run(model, input_data):
    if not os.environ.get("REPLICATE_API_TOKEN"):
        st.error("🔑 API-nyckel saknas i Secrets!")
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
        "page": "SYNTH", 
        "library": [], 
        "audio_library": [],
        "accent": "#00f2ff", 
        "last_img": None,
        "last_prompt": "bild",
        "wallpaper": "https://images.unsplash.com",
        "style": "Cinematic", 
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
with c_dim:
    st.session_state.bg_opacity = st.slider("DIM", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---

if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 NEURAL SYNTH STATION</h2>", unsafe_allow_html=True)
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Beskriv din vision...")
    c1, c2 = st.columns([0.7, 0.3])
    with c1:
        st.session_state.style = st.selectbox("STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Digital Art", "Oil Painting"])
    with c2:
        aspect = st.selectbox("FORMAT:", ["1:1", "16:9", "9:16", "3:2", "4:3", "21:9"], index=1)

    if st.button("🚀 GENERERA"):
        if user_p:
            with st.status("Neural kedja aktiv...", expanded=True):
                st.session_state.last_prompt = user_p
                url = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": user_p, "aspect_ratio": aspect})
                if url:
                    resp = requests.get(url, timeout=20)
                    if resp.status_code == 200:
                        st.session_state.last_img = resp.content
                        st.session_state.library.append({"id": time.time(), "data": resp.content, "prompt": user_p})
                        st.rerun()
    
    if st.session_state.last_img:
        st.image(st.session_state.last_img, use_container_width=True)
        # IMPACT ANALYSIS FIX: Stabiliserad nedladdning via BytesIO
        fname = get_safe_filename(st.session_state.last_prompt)
        img_buffer = io.BytesIO(st.session_state.last_img)
        st.download_button(
            label=f"💾 SPARA: {fname}.jpg",
            data=img_buffer,
            file_name=f"{fname}.jpg",
            mime="image/jpeg"
        )
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if not st.session_state.library: st.info("Arkivet är tomt.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(list(reversed(st.session_state.library))):
            with grid[i % 3]:
                st.image(item['data'], use_container_width=True)
                fname_arkiv = get_safe_filename(item['prompt'])
                # Stabiliserad nedladdning även här
                arkiv_buffer = io.BytesIO(item['data'])
                st.download_button(label="💾 JPG", data=arkiv_buffer, file_name=f"{fname_arkiv}.jpg", mime="image/jpeg", key=f"dl_{item['id']}")
                if st.button("SLÄNG", key=f"del_{item['id']}"):
                    st.session_state.library = [img for img in st.session_state.library if img['id'] != item['id']]
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# (Ljudmodulen lämnas oförändrad för stabilitet)
st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK OS {VERSION}</div>', unsafe_allow_html=True)

