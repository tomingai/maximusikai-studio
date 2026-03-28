import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.2.0"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR & SANITIZER ---
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
        "style": "Photorealistic", "hd_mode": True, "enhance_lvl": 0.8, "process_log": []
    })

# --- 4. UI ENGINE (Neural Gloss) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.93), rgba(0,0,0,0.97)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 5, 25, 0.92); backdrop-filter: blur(50px); border: 1px solid {accent}33; border-radius: 25px; padding: 25px; }}
    .stButton>button {{ border: 1px solid {accent}55 !important; color: white !important; background: {accent}11 !important; border-radius: 12px; height: 3.5rem; }}
    .neural-text {{ font-family: 'Courier New', monospace; color: {accent}; font-size: 0.8rem; opacity: 0.8; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
for i, (icon, target, locked) in enumerate(nav):
    if not locked:
        if nc[i].button(icon, key=f"n_{target}"): st.session_state.page = target; st.rerun()
    else: nc[i].markdown(f'<p style="text-align:center; opacity:0.2; font-size:1.5rem;">{icon}</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent}; letter-spacing:4px;'>🪄 NEURAL VISUALIZER STATION</h2>", unsafe_allow_html=True)
    
    user_p = st.text_input("VISION PROMPT:", placeholder="Skriv din vision...")
    
    col1, col2, col3 = st.columns([0.4, 0.3, 0.3])
    st.session_state.style = col1.selectbox("STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Macro"])
    st.session_state.enhance_lvl = col2.slider("AI DEPTH", 0.0, 1.0, 0.8)
    aspect = col3.selectbox("FORMAT:", ["1:1", "16:9", "9:16"], index=1)

    if st.button("🚀 EXEKVERA NEURAL KEDJA", use_container_width=True):
        if user_p:
            log_area = st.empty()
            with st.status("Initierar Neural Kedja...") as status:
                # STEG 1: LLM ANALYS
                st.session_state.process_log = [f"› Analyserar input: '{user_p}'"]
                log_area.markdown(f'<p class="neural-text">{"<br>".join(st.session_state.process_log)}</p>', unsafe_allow_html=True)
                
                status.update(label="Llama-3 optimerar prompt...")
                prompt_instr = f"Act as a professional cinematographer. Expand to {st.session_state.style} 8k: {user_p}"
                final_p = "".join(list(replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": prompt_instr})))
                
                st.session_state.process_log.append(f"› Prompt expanderad till: {len(final_p)} tecken")
                log_area.markdown(f'<p class="neural-text">{"<br>".join(st.session_state.process_log)}</p>', unsafe_allow_html=True)
                
                # STEG 2: FLUX RENDERING
                status.update(label="FLUX.1 [schnell] renderar pixlar...")
                st.session_state.process_log.append("› Startar latent diffusion (FLUX Engine)")
                log_area.markdown(f'<p class="neural-text">{"<br>".join(st.session_state.process_log)}</p>', unsafe_allow_html=True)
                
                url = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": final_p, "aspect_ratio": aspect.replace(":", "x")})
                
                if url:
                    st.session_state.process_log.append("› Rendering slutförd. Saniterar URL...")
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                    status.update(label="Syntes lyckades!", state="complete")
                    st.rerun()
        else: st.error("Skriv något!")

    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img)
        if st.button("🖼 SÄTT SOM BAKGRUND"): st.session_state.wallpaper = st.session_state.last_img; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# (ENGINE-modulen bibehålls i bakgrunden men döljs här för läsbarhet enligt Regel 12)






































































