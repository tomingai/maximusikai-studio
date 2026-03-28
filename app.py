import streamlit as st
import replicate
import os
import random
import requests
import json
import traceback
import time
from datetime import datetime

# --- 1. SYSTEM-KONFIGURATION & REGLER ---
# VERSION: 9.2.8 | STATUS: PROGRESS TRACKING ACTIVE | REGLER 1-17
st.set_page_config(page_title="MAXIMUSIK AI OS v9.2.8", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"
ERROR_LOG_FILE = "system_errors.log"

# --- 2. DIAGNOSTIK & LOGGNING ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    if is_error: st.session_state.system_alert = True
    prefix = "⚠️ ERROR" if is_error else "INFO"
    st.session_state.logs.append(f"[{timestamp}] {prefix}: {message}")
    if len(st.session_state.logs) > 25: st.session_state.logs.pop(0)

def safe_replicate_run(model, input_data, context="GENERAL"):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            res = replicate.run(model, input=input_data)
            return res
        except Exception:
            if attempt == max_retries - 1:
                report_error(context)
                return None
            time.sleep(2)

def report_error(context):
    error_data = traceback.format_exc()
    with open(ERROR_LOG_FILE, "a") as f:
        f.write(f"\n--- ERROR {datetime.now()} IN {context} ---\n{error_data}\n")

def load_history():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return []
    return []

def save_history():
    try:
        with open(DB_FILE, "w") as f: json.dump(st.session_state.library, f)
    except: report_error("SAVE_HISTORY")

# --- 3. CORE LOGIC (Med Progress Tracking) ---
def clean_url(res):
    try:
        if isinstance(res, list) and len(res) > 0: return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except: return None

def sonify_logic(image_url, prompt_context, progress_bar):
    progress_bar.progress(60, text="SONIFY: Analyserar mood...")
    descr_res = safe_replicate_run("lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                                 {"image": image_url, "prompt": "Music mood in 5 words."}, "SONIFY_ANALYSIS")
    if descr_res:
        progress_bar.progress(80, text=f"SONIFY: Skapar ljud ({descr_res})...")
        snd_res = safe_replicate_run("meta/musicgen:671ac645", 
                                   {"prompt": f"{descr_res}, {prompt_context}", "duration": 8}, "SONIFY_GEN")
        url = clean_url(snd_res)
        if url:
            st.session_state.library.append({"type": "audio", "url": url, "prompt": f"Mood: {descr_res}"})
            save_history()
            return url
    return None

# --- 4. LÅSTA SYSTEM-STATES ---
states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "brightness": 0.5,
    "library": load_history(),
    "logs": ["OS v9.2.8 ONLINE", "PROGRESS ENGINE ACTIVE"],
    "system_alert": False,
    "last_synth_p": "",
    "last_image_res": None, "last_audio_res": None
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 5. UI ENGINE ---
def apply_ui():
    accent = st.session_state.accent_color
    bright = st.session_state.brightness
    overlay = 1.0 - bright 
    alert_c = "#ff0000" if st.session_state.system_alert else "#00ff00"
    
    if st.session_state.system_alert:
        st.markdown('<audio autoplay><source src="https://www.soundjay.com" type="audio/mpeg"></audio>', unsafe_allow_html=True)

    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,{overlay}), rgba(0,0,0,{overlay + 0.1})), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important;
        }}
        .window-box {{ background: rgba(0, 5, 15, 0.94); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 25px; padding: 25px; }}
        .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.6); padding: 8px; border-radius: 12px; margin-bottom: 15px; border: 1px solid {accent}22; }}
        .stProgress > div > div > div > div {{ background-color: {accent} !important; }}
        .status-dot {{ 
            height: 12px; width: 12px; background-color: {alert_c}; border-radius: 50%; display: inline-block;
            box-shadow: 0 0 10px {alert_c}; animation: {"blink 1s infinite" if st.session_state.system_alert else "none"};
        }}
        @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
        h1, h2, h3 {{ color: {accent} !important; font-family: 'Courier New', monospace; }}
        .log-box {{ background: #000; color: #0f0; font-family: 'Courier New', monospace; padding: 10px; border-radius: 5px; font-size: 0.75rem; height: 180px; overflow-y: scroll; border: 1px solid #0f03; }}
        .stButton > button {{ background: rgba(0,0,0,0.4) !important; border: 1px solid {accent}33 !important; color: {accent} !important; }}
        audio, video {{ filter: sepia(1) saturate(5) hue-rotate(160deg); width: 100%; border-radius: 12px; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 6. NAVIGATION & WINDOWS ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:20px; padding-top:20vh; font-size:4rem; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    cols = st.columns(6)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("🎬 MOVIE", "MOVIE"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        if cols[i].button(label, use_container_width=True):
            st.session_state.page = target; st.rerun()
else:
    st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
    nc = st.columns(8)
    nav_items = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "LIBRARY"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
    for i, (icon, target) in enumerate(nav_items):
        if nc[i].button(icon, key=f"n_{target}"):
            st.session_state.page = target; st.rerun()
    nc.markdown(f'<div style="text-align:center;"><span class="status-dot"></span><br><small style="color:white; font-size:0.5rem;">{("ALERT" if st.session_state.system_alert else "SAFE")}</small></div>', unsafe_allow_html=True)
    st.markdown('</div><div class="window-box">', unsafe_allow_html=True)

    if st.session_state.page == "SYNTH":
        st.write("### 🪄 NEURAL SYNTH")
        p = st.text_area("PROMPT:", value=st.session_state.last_synth_p)
        if st.button("🔥 RENDER", use_container_width=True):
            progress = st.progress(0, text="Initierar Neural Länk...")
            add_log(f"IMAGE: Renderar '{p[:15]}...'")
            
            progress.progress(20, text="SYNTH: Ansluter till Replicate...")
            img_res = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": p}, "SYNTH_RENDER")
            url = clean_url(img_res)
            
            if url:
                progress.progress(50, text="SYNTH: Bild klar. Startar Sonifiering...")
                st.session_state.last_image_res = url
                st.session_state.library.append({"type": "image", "url": url, "prompt": p})
                st.session_state.last_audio_res = sonify_logic(url, p, progress)
                
                progress.progress(100, text="SYSTEM: Generering slutförd.")
                save_history(); st.rerun()
            else:
                progress.empty()
        
        if st.session_state.last_image_res: st.image(st.session_state.last_image_res, width=400)
        if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

    elif st.session_state.page == "SYSTEM":
        c1, c2 = st.columns(2)
        with c1:
            st.write("### ⚙️ OS")
            st.session_state.accent_color = st.color_picker("ACCENT", st.session_state.accent_color)
            if st.button("🟢 RESET ALERT"):
                st.session_state.system_alert = False; st.rerun()
        with c2:
            st.write("### 📜 LIVE LOG")
            log_text = "<br>".join(st.session_state.logs[::-1])
            st.markdown(f'<div class="log-box">{log_text}</div>', unsafe_allow_html=True)

    elif st.session_state.page == "LIBRARY":
        for i, item in enumerate(reversed(st.session_state.library)):
            st.write(f"**{item['type'].upper()}**")
            st.download_button(f"Spara #{i}", requests.get(item['url']).content, key=f"dl_{i}")

    st.markdown('</div>', unsafe_allow_html=True)

















































