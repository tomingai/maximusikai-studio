import replicate
import os
import json
import time
import re
from datetime import datetime
import streamlit as st
import requests

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.3.6-GLOW"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR & CLEANER (Regel 3: Maximal URL-tvätt) ---
def clean_prompt(text):
    if not text: return ""
    return str(text).replace('"', '').replace('Prompt:', '').strip()

def sanitize_url(output):
    if not output: return None
    # REGEL 3: Tvinga fram en ren sträng och extrahera URL
    s = str(output).strip()
    match = re.search(r'https?://[^\s\'"\]]+', s)
    if match:
        url = match.group(0)
        # Rensa bort hängande tecken som kan lura Streamlits filhanterare
        for char in ["'", '"', "]", "[", ",", "(", ")"]:
            url = url.replace(char, "")
        return url.strip()
    return None

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
    .prompt-label {{ font-size: 0.75rem; color: {accent}; opacity: 0.8; margin-bottom: 5px; line-height: 1.2; height: 40px; overflow: hidden; font-family: monospace; }}
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
        else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)
with c_dim:
    st.session_state.bg_opacity = st.slider("DIM", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---

if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 SYNTH STATION</h2>", unsafe_allow_html=True)
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Beskriv visionen...")
    c1, c2 = st.columns([0.7, 0.3])
    with c1:
        st.session_state.style = st.selectbox("STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Digital Art", "Oil Painting"])
    with c2:
        aspect = st.selectbox("FORMAT:", ["1:1", "16:9", "9:16", "3:2", "4:3", "21:9"], index=1)

    if st.button("🚀 GENERERA BILD"):
        if user_p:
            with st.status("Neural kedja aktiv...", expanded=True):
                final_p = user_p
                try:
                    raw = ""
                    for ev in replicate.stream("meta/meta-llama-3-8b-instruct", input={"prompt": f"Expand image prompt: {user_p} ({st.session_state.style}). Max 50 words."}):
                        raw += str(ev)
                    final_p = clean_prompt(raw)
                except: pass
                url = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": final_p, "aspect_ratio": aspect})
                if url:
                    # Dubbel-säkring av URL-strängen
                    clean_url = str(url)
                    st.session_state.last_img = clean_url
                    st.session_state.library.append({"id": str(time.time()), "url": clean_url, "prompt": user_p, "expanded_prompt": final_p, "ts": datetime.now().strftime("%H:%M")})
                    st.rerun()
    
    if st.session_state.last_img:
        try:
            # REGEL 3: Försök visa bilden, annars rensa för att rädda appen
            st.image(st.session_state.last_img, use_container_width=True)
        except Exception:
            st.session_state.last_img = None
            st.error("⚠️ Systemet upptäckte en korrupt bild-URL. Försök generera igen.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "AUDIO":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🎧 AUDIO GENERATOR</h2>", unsafe_allow_html=True)
    source = st.radio("METOD:", ["Manuellt", "Från Arkiv (Neural Sync)"], horizontal=True)
    audio_prompt = ""
    if source == "Från Arkiv (Neural Sync)":
        if not st.session_state.library: st.warning("Arkivet är tomt.")
        else:
            img_map = {f"🎵 {img['expanded_prompt'][:40]}...": img for i, img in enumerate(reversed(st.session_state.library))}
            selected_img = img_map[st.selectbox("VÄLJ MUSIKALISK BILD:", list(img_map.keys()))]
            st.image(selected_img['url'], width=300)
            audio_prompt = selected_img.get('expanded_prompt', selected_img['prompt'])
    else: audio_prompt = st.text_input("BESKRIV LJUDET:", placeholder="Dark techno loop...")

    duration = st.slider("LÄNGD (SEK):", 5, 20, 8)
    if st.button("🎵 KOMPONERA"):
        if audio_prompt:
            with st.status("Neural audio aktiv...", expanded=True):
                res = safe_replicate_run("facebookresearch/musicgen", {"prompt": audio_prompt, "duration": duration, "model_version": "stereo-small"})
                if res:
                    st.session_state.last_audio = res
                    st.session_state.audio_library.append({"id": str(time.time()), "url": res, "prompt": audio_prompt, "ts": datetime.now().strftime("%H:%M")})
                    st.rerun()
    if st.session_state.last_audio: st.audio(st.session_state.last_audio)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    t1, t2 = st.tabs(["🖼️ BILDER", "🎵 LJUD"])
    with t1:
        if not st.session_state.library: st.info("Tomt.")
        else:
            grid = st.columns(3)
            for i, item in enumerate(reversed(st.session_state.library)):
                with grid[i % 3]:
                    st.markdown(f"<div class='prompt-label'>🎵 {item.get('expanded_prompt', item['prompt'])[:60]}...</div>", unsafe_allow_html=True)
                    st.image(item['url'], use_container_width=True)
                    b1, b2 = st.columns(2)
                    if b1.button("VÄLJ", key=f"set_{item['id']}"):
                        st.session_state.wallpaper = item['url']; st.rerun()
                    if b2.button("SLÄNG", key=f"del_{item['id']}"):
                        st.session_state.library = [img for img in st.session_state.library if img['id'] != item['id']]
                        st.rerun()
    with t2:
        for item in reversed(st.session_state.audio_library):
            st.markdown(f"**{item['prompt']}**")
            st.audio(item['url'])
            if st.button("RADERA", key=f"del_aud_{item['id']}"):
                st.session_state.audio_library = [a for a in st.session_state.audio_library if a['id'] != item['id']]
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK OS {VERSION}</div>', unsafe_allow_html=True)





























































































































































































































































































































































































































































































































































































