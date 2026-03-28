import replicate
import os
import json
import time
from datetime import datetime
import streamlit as st

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.3.6-GLOW"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR & CLEANER ---
def clean_prompt(text):
    if not text: return ""
    return str(text).replace('"', '').replace('Prompt:', '').strip()

def sanitize_url(output):
    if isinstance(output, list) and len(output) > 0: return str(output[0])
    return str(output)

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
    h1, h2, h3, label, p {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }}
    .stButton>button {{ 
        border: 1px solid {accent}66 !important; background: {accent}11 !important; 
        color: white !important; border-radius: 12px; font-weight: bold; width: 100%;
    }}
    .stButton>button[key^="del_"] {{ border: 1px solid #ff4b4b66 !important; background: #ff4b4b22 !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION & KONTROLLER ---
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
c_nav, c_dim = st.columns([0.75, 0.25])
with c_nav:
    nc = st.columns(6)
    nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",False), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("⚙️","SYSTEM",True)]
    for i, (icon, target, locked) in enumerate(nav):
        if not locked:
            if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
        else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)
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
            with st.status("Neural kedja aktiv...", expanded=True) as status:
                final_prompt = user_p
                try:
                    raw_exp = ""
                    for event in replicate.stream("meta/meta-llama-3-8b-instruct", input={"prompt": f"Expand: {user_p} in {st.session_state.style} style. Max 60 words."}):
                        raw_exp += str(event)
                    if raw_exp: final_prompt = clean_prompt(raw_exp)
                except: pass
                url = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": final_prompt, "aspect_ratio": aspect})
                if url:
                    st.session_state.last_img = url
                    st.session_state.library.append({"id": time.time(), "url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                    st.rerun()
        else: st.error("Skriv något först.")
    if st.session_state.last_img:
        st.image(st.session_state.last_img, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "AUDIO":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🎧 AUDIO GENERATOR</h2>", unsafe_allow_html=True)
    audio_prompt = st.text_input("BESKRIV LJUDET:", placeholder="Dark techno loop...")
    duration = st.slider("LÄNGD (SEK):", 5, 20, 8)
    if st.button("🎵 GENERERA"):
        if audio_prompt:
            res = safe_replicate_run("facebookresearch/musicgen", {"prompt": audio_prompt, "duration": duration})
            if res:
                st.session_state.audio_library.append({"id": time.time(), "url": res, "prompt": audio_prompt})
                st.rerun()
    for item in reversed(st.session_state.audio_library):
        st.audio(item['url'])
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if not st.session_state.library: st.info("Arkivet är tomt.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(list(reversed(st.session_state.library))):
            with grid[i % 3]:
                st.image(item['url'], use_container_width=True)
                b1, b2 = st.columns(2)
                if b1.button("VÄLJ", key=f"set_{item['id']}"):
                    st.session_state.wallpaper = item['url']; st.rerun()
                if b2.button("SLÄNG", key=f"del_{item['id']}"):
                    st.session_state.library = [img for img in st.session_state.library if img['id'] != item['id']]
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK OS {VERSION}</div>', unsafe_allow_html=True)


























































































































































































































































































































































































































































































































































































