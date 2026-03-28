import streamlit as st
import replicate
import os
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.3.6-GLOW"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

# Säkerställ API-nyckel
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR-FUNKTIONER ---
def clean_prompt(text):
    if not text: return ""
    return str(text).replace('"', '').replace('Prompt:', '').strip()

def safe_replicate_run(model, input_data):
    try:
        res = replicate.run(model, input=input_data)
        return res
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
        "style": "Cinematic"
    })

# --- 4. UI ENGINE (CSS) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed;
    }}
    .glass {{ 
        background: rgba(0, 10, 25, 0.85); 
        backdrop-filter: blur(20px); 
        border: 1px solid {accent}33; 
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
    }}
    h1, h2, h3, label, p {{ color: white !important; font-family: 'Inter', sans-serif; }}
    .stButton>button {{ 
        border: 1px solid {accent}88 !important; 
        background: {accent}22 !important; color: white !important; 
        border-radius: 10px; width: 100%; transition: 0.3s;
    }}
    .neural-console {{ 
        background: rgba(0,0,0,0.9); border: 1px solid {accent}44; 
        padding: 10px; border-radius: 5px; font-family: monospace; 
        color: {accent}; font-size: 0.85rem; height: 100px; overflow-y: auto;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 5px 15px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
for i, (icon, target, locked) in enumerate(nav):
    if not locked:
        if nc[i].button(f"{icon} {target}", key=f"nav_{target}"): 
            st.session_state.page = target
            st.rerun()
    else:
        nc[i].markdown(f'<p style="text-align:center; opacity:0.2; margin-top:10px;">{icon}</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---

# --- MODUL: SYNTH STATION ---
if st.session_state.page == "SYNTH":
    st.markdown(f"<h2 style='color:{accent};'>🪄 NEURAL SYNTH STATION</h2>", unsafe_allow_html=True)
    
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="En futuristisk stad under vatten...")
    
    c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
    with c1:
        st.session_state.style = st.selectbox("VISUELL STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Anime", "Digital Art"])
    with c2:
        # VIKTIGT: Dessa strängar matchar exakt vad FLUX kräver
        aspect = st.selectbox("FORMAT:", ["1:1", "16:9", "9:16", "3:2", "4:3", "21:9"], index=1)
    with c3:
        model_choice = st.selectbox("MOTOR:", ["FLUX Schnell", "FLUX Dev"])

    if st.button("🚀 STARTA GENERERING"):
        if user_p:
            log_placeholder = st.empty()
            logs = ["› INITIALIZING...", "› OPTIMIZING PROMPT..."]
            log_placeholder.markdown(f'<div class="neural-console">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
            
            # 1. Expandera prompt
            raw_expanded = "".join(list(replicate.run("meta/meta-llama-3-8b-instruct", input={
                "prompt": f"Expand this to a {st.session_state.style} image prompt: {user_p}. Max 80 words. Output ONLY prompt.",
                "max_new_tokens": 120
            })))
            expanded = clean_prompt(raw_expanded)
            
            logs.append(f"› RENDERING PIXELS ({aspect})...")
            log_placeholder.markdown(f'<div class="neural-console">{"<br>".join(logs)}</div>', unsafe_allow_html=True)
            
            # 2. Generera bild (Här skickas aspect exakt som sträng "16:9")
            model_path = "black-forest-labs/flux-schnell" if "Schnell" in model_choice else "black-forest-labs/flux-dev"
            output = safe_replicate_run(model_path, {
                "prompt": expanded, 
                "aspect_ratio": aspect, 
                "output_format": "webp"
            })

            if output:
                img_url = output[0] if isinstance(output, list) else output
                st.session_state.last_img = img_url
                st.session_state.library.append({"url": img_url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                st.rerun()
        else:
            st.error("Skriv in en beskrivning!")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.last_img:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.image(st.session_state.last_img, use_container_width=True)
        if st.button("🖼 ANVÄND SOM BAKGRUND"):
            st.session_state.wallpaper = st.session_state.last_img
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- MODUL: ARKIV ---
elif st.session_state.page == "ARKIV":
    st.markdown(f"<h2 style='color:{accent};'>📚 ARKIV</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.info("Inga bilder sparade än.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.markdown('<div class="glass">', unsafe_allow_html=True)
                st.image(item['url'], use_container_width=True)
                if st.button("LADDA", key=f"arch_{i}"):
                    st.session_state.last_img = item['url']
                    st.session_state.page = "SYNTH"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# --- MODUL: ENGINE ---
elif st.session_state.page == "ENGINE":
    st.markdown(f"<h2 style='color:{accent};'>🖼️ VISION ENGINE</h2>", unsafe_allow_html=True)
    if st.session_state.last_img:
        st.image(st.session_state.last_img, width=500)
        if st.button("🔍 DJUPANALYS"):
            res = safe_replicate_run("lucataco/moondream2", {
                "image": st.session_state.last_img, 
                "prompt": "Describe this image in detail."
            })
            st.success(res)
    else:
        st.info("Skapa en bild först.")

# --- FOOTER ---
st.markdown(f'<div style="text-align:right; opacity:0.4; font-size:0.7rem; color:white; padding:10px;">OS VERSION: {VERSION}</div>', unsafe_allow_html=True)
























































































































































