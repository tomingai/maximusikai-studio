import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.3.6"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR & CLEANER (Regel 21 & 12) ---
def clean_prompt(text):
    """Tar bort citattecken och LLM-brus"""
    if not text: return ""
    clean = str(text).replace('"', '').replace('Prompt:', '').strip()
    return clean

def sanitize_url(output):
    if isinstance(output, list) and len(output) > 0: return str(output[0])
    return str(output)

def safe_replicate_run(model, input_data):
    try:
        res = replicate.run(model, input=input_data)
        if "moondream" in model or "llama" in model: return res
        return sanitize_url(res)
    except Exception as e:
        # Auto-Fix vid fel: Kör en bas-prompt
        if "flux" in model:
            try:
                fallback = replicate.run(model, input={"prompt": input_data.get("prompt", "A futuristic vision")})
                return sanitize_url(fallback)
            except: return None
        return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "accent": "#00f2ff", "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Photorealistic", "process_log": [], "analysis": ""
    })

# --- 4. UI ENGINE (Neural Gloss) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    @keyframes pulse-green {{ 0% {{ border-color: {accent}44; }} 50% {{ border-color: #00ff88; }} 100% {{ border-color: {accent}44; }} }}
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.95), rgba(0,0,0,0.98)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 5, 20, 0.92); backdrop-filter: blur(50px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; }}
    .success-box {{ border: 2px solid #00ff88; animation: pulse-green 2s infinite; border-radius: 12px; padding: 10px; text-align: center; color: #00ff88; font-family: monospace; }}
    .neural-console {{ background: rgba(0,0,0,0.7); border: 1px solid {accent}22; padding: 12px; border-radius: 8px; font-family: monospace; color: {accent}; font-size: 0.75rem; }}
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

# --- 6. SYNTH MODUL ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 STABILIZED PIPELINE v{VERSION}</h2>", unsafe_allow_html=True)
    
    user_p = st.text_input("VISION PROMPT:", placeholder="The Quantum Alchemist...")
    c1, c2 = st.columns([0.7, 0.3])
    st.session_state.style = c1.selectbox("STYLE:", ["Photorealistic", "Cinematic", "Cyberpunk", "Digital Art"])
    aspect = c2.selectbox("FORMAT:", ["1:1", "16:9", "9:16"], index=1)

    if st.button("🚀 EXEKVERA"):
        if user_p:
            prog = st.progress(0)
            console = st.empty()
            log = [f"› [{datetime.now().strftime('%H:%M:%S')}] BOOTING NEURAL ENGINE..."]
            
            # STEG 1: LLM (Expansion & Cleaning)
            prog.progress(20, text="EXPANDING VISION...")
            raw_expanded = "".join(list(replicate.run("meta/meta-llama-3-8b-instruct", input={
                "prompt": f"Act as a professional cinematographer. Expand this to a {st.session_state.style} 8k image prompt: {user_p}. Respond only with the prompt, no conversational text.",
                "max_new_tokens": 150
            })))
            expanded = clean_prompt(raw_expanded)
            log.append(f"› PROMPT CLEANED & EXPANDED.")
            console.markdown(f'<div class="neural-console">{"<br>".join(log)}</div>', unsafe_allow_html=True)
            
            # STEG 2: FLUX (Rendering)
            prog.progress(50, text="RENDERING PIXELS...")
            url = safe_replicate_run("black-forest-labs/flux-schnell", {
                "prompt": expanded, 
                "aspect_ratio": aspect.replace(":", "x")
            })
            
            if url:
                prog.progress(100, text="COMPLETE")
                st.session_state.last_img = url
                st.session_state.library.append({"url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                st.markdown('<div class="success-box">✅ PIPELINE SUCCESSFUL</div>', unsafe_allow_html=True)
                time.sleep(1)
                st.rerun()
        else: st.error("Prompt missing.")

    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, use_column_width=True)
        if st.button("🖼 SET WALLPAPER"): st.session_state.wallpaper = st.session_state.last_img; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


















































































































































