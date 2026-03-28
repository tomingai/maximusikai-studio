import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- SYSTEM UPGRADE v10.1.8 ---
# STATUS: OPTIMIZED | REGEL 21: ENHANCED VERSION STRIPPING
st.set_page_config(page_title="MAXIMUSIK AI OS v10.1.8", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    icon = "⚠️" if is_error else "🤖"
    st.session_state.logs.append(f"[{timestamp}] {icon} {message}")
    if len(st.session_state.logs) > 12: st.session_state.logs.pop(0)

def improved_safe_run(model_alias, input_data):
    """FÖRBÄTTRING: Smart version-mapping för att eliminera 'Invalid v.'"""
    models = {
        "FLUX": "black-forest-labs/flux-schnell",
        "MUSIC": "facebookresearch/musicgen", # Borttagen hash för auto-resolve till senaste stabila
        "VISION": "lucataco/moondream2"
    }
    target = models.get(model_alias, model_alias)
    
    # Progress Bar UI (Regel 12)
    p_bar = st.progress(0, text="Neural Handshake...")
    try:
        # Dynamisk optimering: Om det är ljud, använd MusicGen-specifika parametrar
        if model_alias == "MUSIC":
            input_data.setdefault("model_version", "stereo-large")
            
        for i in range(1, 11):
            time.sleep(0.05)
            p_bar.progress(i * 10, text=f"Computing {model_alias}...")
            
        output = replicate.run(target, input=input_data)
        p_bar.empty()
        return output
    except Exception as e:
        p_bar.empty()
        add_log(f"AUTO-FIX TRIGGERED: {str(e)[:30]}", is_error=True)
        # Förbättring: Om versionen bråkar, kör vi rå-strängen som fallback
        return replicate.run(target.split(":")[0], input=input_data)

# UI INITIALISERING
if "page" not in st.session_state:
    st.session_state.update({
        "page": "DESKTOP",
        "logs": ["v10.1.8: ENHANCED KERNEL LOADED"],
        "accent": "#ff00ff", # Ny accent för v10.1.8
        "wallpaper": "https://images.unsplash.com"
    })

# CSS GLASMORPHISM (Ständigt förbättrad)
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: #0a0a0f; background-image: radial-gradient({st.session_state.accent}11 1px, transparent 1px); background-size: 30px 30px; }}
    .glass-panel {{ background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(15px); border: 1px solid {st.session_state.accent}22; border-radius: 20px; padding: 25px; }}
    .stButton>button {{ border: 1px solid {st.session_state.accent}44 !important; background: transparent !important; color: {st.session_state.accent} !important; border-radius: 12px; }}
    </style>
""", unsafe_allow_html=True)

# MAIN INTERFACE
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:15px; color:{st.session_state.accent};'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    if cols[0].button("🪄 SYNTH"): st.session_state.page = "SYNTH"; st.rerun()
    if cols[1].button("🎧 AUDIO"): st.session_state.page = "AUDIO"; st.rerun()
    if cols[2].button("⚙️ SYSTEM"): st.session_state.page = "SYSTEM"; st.rerun()
    
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    st.write("### 📟 ACTIVE LOGS")
    for log in reversed(st.session_state.logs):
        st.code(log)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "AUDIO":
    st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
    if st.button("⬅ EXIT"): st.session_state.page = "DESKTOP"; st.rerun()
    prompt = st.text_input("SONIC PROMPT (e.g. '80s Synthwave, 120bpm'):")
    if st.button("GENERATE"):
        res = improved_safe_run("MUSIC", {"prompt": prompt, "duration": 5})
        if res:
            st.audio(res)
            add_log(f"Success: {prompt[:15]}")
    st.markdown('</div>', unsafe_allow_html=True)






























































