import replicate
import os
import json
import time
from datetime import datetime
import streamlit as st

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.3.6-GLOW"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

# Hämtar token från Streamlit Secrets
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR & CLEANER ---
def clean_prompt(text):
    if not text: return ""
    return str(text).replace('"', '').replace('Prompt:', '').strip()

def sanitize_url(output):
    # Flux returnerar ofta en lista, vi extraherar första URL:en
    if isinstance(output, list) and len(output) > 0: return str(output[0])
    return str(output)

def safe_replicate_run(model, input_data):
    if not os.environ.get("REPLICATE_API_TOKEN"):
        st.error("🔑 API-nyckel saknas! Lägg till REPLICATE_API_TOKEN i Secrets.")
        return None
    try:
        res = replicate.run(model, input=input_data)
        # För textmodeller returneras strängar, för bildmodeller kallas sanitize_url
        if "moondream" in model or "llama" in model: return res
        return sanitize_url(res)
    except Exception as e:
        st.error(f"Neural Error: {e}")
        return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", 
        "library": [], 
        "accent": "#00f2ff", 
        "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Cinematic", 
        "bg_opacity": 0.80
    })

# --- 4. UI ENGINE (Dynamic CSS) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    /* Fixerad bakgrund som täcker hela skärmen */
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,{st.session_state.bg_opacity}), rgba(0,0,0,{st.session_state.bg_opacity})), 
                    url("{st.session_state.wallpaper}"); 
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}
    
    /* Glas-paneler */
    .glass {{ 
        background: rgba(0, 10, 30, 0.75); 
        backdrop-filter: blur(40px); 
        border: 1px solid {accent}33; 
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
    }}

    h1, h2, h3, label, p {{ 
        color: white !important; 
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8) !important;
    }}
    
    /* Knappar */
    .stButton>button {{ 
        border: 1px solid {accent}66 !important; 
        background: {accent}11 !important; 
        color: white !important; border-radius: 12px; height: 3.5rem; font-weight: bold;
    }}
    
    /* Input-fält */
    .stTextInput>div>div>input {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: white !important;
        border: 1px solid {accent}22 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION & KONTROLLER ---
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
c_nav, c_dim = st.columns([0.75, 0.25])

with c_nav:
    nc = st.columns(7)
    nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
    for i, (icon, target, locked) in enumerate(nav):
        if not locked:
            if nc[i].button(icon, key=f"nav_{target}"): 
                st.session_state.page = target
                st.rerun()
        else: 
            nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)

with c_dim:
    # Justerar bakgrundens mörkhet i realtid
    st.session_state.bg_opacity = st.slider("BG DIMMER", 0.0, 1.0, st.session_state.bg_opacity, 0.05)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 NEURAL SYNTH STATION</h2>", unsafe_allow_html=True)
    
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Beskriv din vision här...")
    
    c1, c2 = st.columns([0.7, 0.3])
    with c1:
        st.session_state.style = st.selectbox("STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Digital Art", "Oil Painting"])
    with c2:
        aspect = st.selectbox("FORMAT:", ["1:1", "16:9", "9:16", "3:2", "4:3", "21:9"], index=1)

    if st.button("🚀 EXEKVERA GENERERING"):
        if user_p:
            with st.status("Neural kedja aktiv...", expanded=True) as status:
                st.write("Anropar Llama för expansion...")
                
                # Robust expansion via Llama 3
                final_prompt = user_p
                try:
                    raw_exp = ""
                    for event in replicate.stream(
                        "meta/meta-llama-3-8b-instruct",
                        input={"prompt": f"Write a {st.session_state.style} image prompt based on: {user_p}. Max 60 words. Output only the prompt."}
                    ):
                        raw_exp += str(event)
                    if raw_exp: final_prompt = clean_prompt(raw_exp)
                except:
                    pass

                st.write("Renderar pixlar via FLUX...")
                url = safe_replicate_run("black-forest-labs/flux-schnell", {
                    "prompt": final_prompt, 
                    "aspect_ratio": aspect,
                    "output_format": "webp"
                })

                if url:
                    st.session_state.last_img = url
                    st.session_state.library.append({
                        "url": url, 
                        "prompt": user_p, 
                        "ts": datetime.now().strftime("%H:%M")
                    })
                    status.update(label="Generering klar!", state="complete")
                    st.rerun()
        else: 
            st.error("Beskriv din vision först.")

    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, use_container_width=True)
        if st.button("🖼 TILLÄMPA SOM OS-BAKGRUND"): 
            st.session_state.wallpaper = st.session_state.last_img
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 SYSTEM ARCHIVE")
    if not st.session_state.library: 
        st.info("Arkivet är tomt. Skapa något i SYNTH först.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.image(item['url'], use_container_width=True)
                st.caption(f"Prompt: {item['prompt']} ({item['ts']})")
                if st.button("LADDA", key=f"ark_{i}"):
                    st.session_state.last_img = item['url']
                    st.session_state.wallpaper = item['url']
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ENGINE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("🖼️ VISION ANALYSER")
    if st.session_state.last_img:
        st.image(st.session_state.last_img, width=400)
        if st.button("🔍 ANALYSERA DETALJER"):
            res = safe_replicate_run("lucataco/moondream2", {
                "image": st.session_state.last_img, 
                "prompt": "Describe the textures and lighting in this image."
            })
            st.info(res)
    else: 
        st.info("Ingen aktiv bild. Gå till SYNTH för att skapa en.")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer info
st.markdown(f'<div style="text-align:right; opacity:0.3; font-size:0.7rem; color:white;">MAXIMUSIK OS {VERSION}</div>', unsafe_allow_html=True)


















































































































































































































































































































































































































































































































































































































