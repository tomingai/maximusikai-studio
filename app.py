import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.4.0-LUMINA"
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
    try:
        res = replicate.run(model, input=input_data)
        if "moondream" in model or "llama" in model: return res
        return sanitize_url(res)
    except: return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "accent": "#00f2ff", "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Photorealistic", "brightness": 5 # Startvärde (medel)
    })

# --- 4. UI ENGINE (LUMINA DYNAMIK) ---
accent = st.session_state.accent
# Omvandla 1-10 till 0.1-0.9 för CSS opacity (Overlay)
bright_val = (11 - st.session_state.brightness) / 10

st.markdown(f"""
    <style>
    /* Dynamiskt Neural Overlay för ljusstyrka */
    [data-testid="stAppViewContainer"]::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, {bright_val});
        z-index: -1; transition: 0.5s;
    }}
    [data-testid="stAppViewContainer"] {{ 
        background: url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed; background-position: center;
    }}
    .glass {{ 
        background: rgba(0, 5, 15, 0.82); backdrop-filter: blur(50px); 
        border: 1px solid {accent}44; border-radius: 20px; padding: 25px; 
    }}
    h1, h2, h3, label, p {{ color: white !important; text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }}
    .stButton>button {{ border: 1px solid {accent}66 !important; background: {accent}11 !important; color: white !important; font-weight: bold; border-radius: 12px; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION & LUMINA CONTROL ---
st.markdown('<div class="glass" style="padding: 15px; margin-bottom: 20px;">', unsafe_allow_html=True)
c_nav, c_bright = st.columns([0.7, 0.3])

with c_nav:
    nc = st.columns(7)
    nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
    for i, (icon, target, locked) in enumerate(nav):
        if not locked:
            if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
        else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0;">{icon}</p>', unsafe_allow_html=True)

with c_bright:
    st.session_state.brightness = st.slider("🔅 LUMINA", 1, 10, st.session_state.brightness, help="Justera systemets ljusstyrka")

st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 SYNTH STATION</h2>", unsafe_allow_html=True)
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Din vision...")
    c1, c2 = st.columns([0.7, 0.3])
    st.session_state.style = c1.selectbox("STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Digital Art"])
    aspect = c2.selectbox("FORMAT:", ["1:1", "16:9", "9:16"], index=1)

    if st.button("🚀 EXEKVERA"):
        if user_p:
            prog = st.progress(0)
            with st.status("Neural Pipeline...") as status:
                res_llm = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": f"Expand to 8k {st.session_state.style} prompt: {user_p}"})
                expanded = clean_prompt("".join(list(res_llm)))
                url = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": expanded, "aspect_ratio": aspect.replace(":", "x")})
                if url:
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p})
                    st.rerun()
    
    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, use_column_width=True)
        if st.button("🖼 SÄTT SOM BAKGRUND"): st.session_state.wallpaper = st.session_state.last_img; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 SYSTEM ARCHIVE")
    if not st.session_state.library: st.info("Arkivet är tomt.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.image(item['url'], use_column_width=True)
                if st.button("VÄLJ", key=f"ark_{i}"):
                    st.session_state.last_img = item['url']
                    st.session_state.wallpaper = item['url']; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)




















































































































































