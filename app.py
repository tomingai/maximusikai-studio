import streamlit as st
import replicate
import os
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.3.6-GLOW"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR-FUNKTIONER ---
def clean_prompt(text):
    if not text: return ""
    return str(text).replace('"', '').replace('Prompt:', '').strip()

def safe_replicate_run(model, input_data):
    try:
        res = replicate.run(model, input=input_data)
        if "moondream" in model or "llama" in model: return res
        return res[0] if isinstance(res, list) else res
    except Exception as e:
        st.error(f"Neural Error: {e}")
        return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "accent": "#00f2ff", "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Cinematic"
    })

# --- 4. UI ENGINE (CSS) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed;
    }}
    .glass {{ 
        background: rgba(0, 10, 30, 0.85); 
        backdrop-filter: blur(40px); 
        border: 1px solid {accent}44; 
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
    }}
    h1, h2, h3, label, p {{ color: white !important; font-weight: 600 !important; }}
    .stButton>button {{ 
        border: 1px solid {accent}88 !important; 
        background: {accent}22 !important; color: white !important; 
        border-radius: 12px; height: 3.5rem; font-weight: bold; width: 100%;
    }}
    .neural-console {{ 
        background: rgba(0,0,0,0.8); border: 1px solid {accent}44; 
        padding: 12px; border-radius: 8px; font-family: monospace; color: {accent};
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
for i, (icon, target, locked) in enumerate(nav):
    if not locked:
        if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
    else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0;">{icon}</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 SYNTH STATION</h2>", unsafe_allow_html=True)
    
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Bananer förvandlas till ett lejon...")
    
    c1, c2 = st.columns([0.7, 0.3])
    with c1:
        st.session_state.style = st.selectbox("VISUELL STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Digital Art"])
    with c2:
        aspect = st.selectbox("FORMAT:", ["1:1", "16:9", "9:16", "3:2", "4:3", "21:9"], index=1)

    if st.button("🚀 STARTA NEURAL KEDJA"):
        if user_p:
            console = st.empty()
            log = ["› INITIALIZING NEURAL ENGINE..."]
            
            # STEG 1: LLM
            raw_expanded = "".join(list(replicate.run("meta/meta-llama-3-8b-instruct", input={
                "prompt": f"Expand this to a {st.session_state.style} 8k image prompt: {user_p}. Max 100 words. Respond only with prompt.",
                "max_new_tokens": 150
            })))
            expanded = clean_prompt(raw_expanded)
            log.append("› PROMPT OPTIMIZED.")
            console.markdown(f'<div class="neural-console">{"<br>".join(log)}</div>', unsafe_allow_html=True)
            
            # STEG 2: FLUX
            url = safe_replicate_run("black-forest-labs/flux-schnell", {
                "prompt": expanded, "aspect_ratio": aspect, "output_format": "webp"
            })
            
            if url:
                st.session_state.last_img = url
                st.session_state.library.append({"url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                st.rerun()
        else: st.error("Prompt saknas.")

    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, use_container_width=True)
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
                st.image(item['url'], use_container_width=True)
                if st.button("VÄLJ", key=f"ark_{i}"):
                    st.session_state.last_img = item['url']
                    st.session_state.wallpaper = item['url']; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ENGINE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("🖼️ VISION ENGINE")
    if st.session_state.last_img:
        st.image(st.session_state.last_img, width=400)
        if st.button("🔍 ANALYSERA"):
            res = safe_replicate_run("lucataco/moondream2", {"image": st.session_state.last_img, "prompt": "Describe details."})
            st.info(res)
    else: st.info("Skapa en bild först.")
    st.markdown('</div>', unsafe_allow_html=True)









































































































































































































































































































