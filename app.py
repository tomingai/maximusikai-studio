import streamlit as st
import replicate
import os
import random
import json
import traceback
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION (v10.1.5) ---
st.set_page_config(page_title="MAXIMUSIK AI OS v10.1.5", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"
ERROR_LOG_FILE = "system_errors.log"

# --- 2. ENGINE & REPAIR LOGIK ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    if is_error: st.session_state.system_alert = True
    st.session_state.logs.append(f"[{timestamp}] {'⚠️' if is_error else '🤖'} {message}")
    if len(st.session_state.logs) > 15: st.session_state.logs.pop(0)

def safe_replicate_run(model_alias, input_data, context="GENERAL"):
    """Regel 21: Auto-Fix för 'Invalid v.' och Dynamic Routing."""
    models = {
        "FLUX": "black-forest-labs/flux-schnell",
        "MUSIC": "facebookresearch/musicgen:7a76a825701904677340e68d71563f69dba84f3353a16134a413d70f0322d7ad",
        "VISION": "lucataco/moondream2:60039868779900c6d59b0222956c214c7760925703f6f3286f78a2e46b281f6d",
        "VIDEO": "stability-ai/video-diffusion:3f0bd67d0246b0336ca149257e3df179c3f3f5022137090b8f6c561ec9d77583"
    }
    
    target = models.get(model_alias, model_alias)
    
    # Neural Progress Bar simulation
    bar = st.progress(0, text=f"Initialiserar {model_alias}...")
    
    for attempt in range(2):
        try:
            for p in range(10, 90, 20):
                time.sleep(0.1)
                bar.progress(p, text=f"Processar via {context}...")
            
            output = replicate.run(target, input=input_data)
            bar.progress(100, text="Slutfört.")
            time.sleep(0.5)
            bar.empty()
            return output
        except Exception as e:
            err_msg = str(e)
            if "Invalid v" in err_msg:
                add_log(f"Auto-fixing version string for {model_alias}...", is_error=True)
                # Force fallback to base model string if version fails
                target = target.split(":")[0] 
            if attempt == 1:
                add_log(f"Krasch i {context}: {err_msg[:30]}", is_error=True)
                bar.empty()
                return None
            time.sleep(1)

def save_history():
    try:
        with open(DB_FILE, "w") as f:
            json.dump(st.session_state.library, f)
    except: add_log("Kunde inte spara till DB", is_error=True)

# --- 3. GLASMORMISM UI ---
def apply_ui():
    accent = st.session_state.accent_color
    bright = st.session_state.brightness
    alert_c = "#ff0000" if st.session_state.system_alert else accent
    
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,{1-bright}), rgba(0,0,0,{1-bright})), 
                        url("{st.session_state.wallpaper}") no-repeat center center fixed;
            background-size: cover;
        }}
        .glass {{
            background: rgba(15, 15, 25, 0.85);
            backdrop-filter: blur(20px);
            border: 1px solid {accent}33;
            border-radius: 25px;
            padding: 2rem;
            margin-top: 20px;
        }}
        .stButton>button {{
            border: 1px solid {accent}77 !important;
            background: rgba(255,255,255,0.05) !important;
            color: {accent} !important;
            border-radius: 10px !important;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        .log-box {{
            background: #000;
            color: {alert_c};
            font-family: 'Courier New', monospace;
            padding: 10px;
            border-radius: 10px;
            font-size: 0.8rem;
            border: 1px solid {alert_c}44;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- 4. SESSION STATE ---
if "library" not in st.session_state:
    st.session_state.update({
        "page": "DESKTOP",
        "library": [],
        "logs": ["KERNEL v10.1.5 READY"],
        "accent_color": "#00ffcc",
        "brightness": 0.5,
        "wallpaper": "https://images.unsplash.com",
        "system_alert": False,
        "last_img": None
    })

apply_ui()

# --- 5. MAIN ROUTING ---
if st.session_state.page == "DESKTOP":
    st.markdown("<br><br><h1 style='text-align:center; font-size:4rem; letter-spacing:15px;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("🪄 SYNTH"): st.session_state.page = "SYNTH"; st.rerun()
    if c2.button("🎧 AUDIO"): st.session_state.page = "AUDIO"; st.rerun()
    if c3.button("⚙️ SYSTEM"): st.session_state.page = "SYSTEM"; st.rerun()
    
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.write("### 📜 SYSTEM LOG")
    logs = "<br>".join(st.session_state.logs[::-1])
    st.markdown(f'<div class="log-box">{logs}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.button("⬅ TILLBAKA"): st.session_state.page = "DESKTOP"; st.rerun()
    prompt = st.text_input("IMAGE PROMPT:")
    if st.button("GENERATE IMAGE"):
        res = safe_replicate_run("FLUX", {"prompt": prompt}, "SYNTH_IMAGE")
        if res:
            st.session_state.last_img = res[0]
            st.image(res[0])
            st.session_state.library.append({"type": "IMG", "url": res[0], "prompt": prompt})
            save_history()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "AUDIO":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.button("⬅ TILLBAKA"): st.session_state.page = "DESKTOP"; st.rerun()
    a_prompt = st.text_input("AUDIO PROMPT (STYLE, BPM):")
    if st.button("GENERATE AUDIO"):
        res = safe_replicate_run("MUSIC", {"prompt": a_prompt, "duration": 8}, "SYNTH_AUDIO")
        if res:
            st.audio(res)
            st.session_state.library.append({"type": "AUDIO", "url": res, "prompt": a_prompt})
            save_history()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "SYSTEM":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.button("⬅ TILLBAKA"): st.session_state.page = "DESKTOP"; st.rerun()
    st.session_state.accent_color = st.color_picker("ACCENT COLOR", st.session_state.accent_color)
    st.session_state.brightness = st.slider("WALLPAPER BRIGHTNESS", 0.0, 1.0, st.session_state.brightness)
    if st.button("RESET SYSTEM ALERT"): 
        st.session_state.system_alert = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)




























































