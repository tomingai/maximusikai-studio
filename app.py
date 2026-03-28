import streamlit as st
import replicate
import os
import random
import requests
import json
import traceback
import time
from datetime import datetime

# --- 1. SYSTEM-KONFIGURATION ---
# VERSION: 9.9.8 | STATUS: SMART FALLBACK ACTIVE | REGLER 1-20
st.set_page_config(page_title="MAXIMUSIK AI OS v9.9.8", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"
ERROR_LOG_FILE = "system_errors.log"

# --- 2. DIAGNOSTIK & LOGGNING (Regel 19 & 20) ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    if is_error: st.session_state.system_alert = True
    st.session_state.logs.append(f"[{timestamp}] {'⚠️' if is_error else '🤖'} {message}")
    if len(st.session_state.logs) > 20: st.session_state.logs.pop(0)

def safe_replicate_run(model, input_data, context="GENERAL"):
    for attempt in range(2): # Snabbare retry
        try:
            return replicate.run(model, input=input_data)
        except Exception as e:
            if attempt == 1:
                report_error(f"{context}: {str(e)[:40]}")
                return None
            time.sleep(1)

def report_error(context):
    error_data = traceback.format_exc()
    try:
        with open(ERROR_LOG_FILE, "a") as f:
            f.write(f"\n--- ERROR {datetime.now()} IN {context} ---\n{error_data}\n")
    except: pass
    add_log(f"Krasch i {context}.", is_error=True)

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

def clean_url(res):
    try:
        if isinstance(res, list) and len(res) > 0: return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except: return None

# --- 3. AUTO-LOGIC ENGINE (Smart Fallback) ---
def sonify_logic(image_url, prompt_context, progress_bar):
    progress_bar.progress(65, text="SONIFY: Analyserar bild (Steg 1/2)...")
    
    # Försök 1: Bildanalys
    descr = safe_replicate_run("lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                              {"image": image_url, "prompt": "Describe mood in 5 words."}, "SONIFY_ANALYSIS")
    
    # Regel 20: Om analysen misslyckas, använd prompten direkt (Fallback)
    if not descr:
        add_log("SONIFY: Bildanalys misslyckades. Använder text-fallback.")
        mood_p = f"Cinematic music, {prompt_context}"
    else:
        mood_p = f"{descr}, {prompt_context}"
        add_log(f"SONIFY: Analys klar: {descr}")

    progress_bar.progress(85, text="SONIFY: Skapar musik (Steg 2/2)...")
    snd = safe_replicate_run("meta/musicgen:671ac645", {"prompt": mood_p, "duration": 8}, "SONIFY_GEN")
    
    url = clean_url(snd)
    if url:
        st.session_state.library.append({"type": "audio", "url": url, "prompt": f"Mood: {descr if descr else 'Auto'}"})
        return url
    return None

# --- 4. UI ENGINE ---
def apply_ui():
    accent = st.session_state.accent_color
    bright = st.session_state.brightness
    overlay = 1.0 - bright 
    alert_c = "#ff0000" if st.session_state.system_alert else "#00ff00"
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{ 
            background: linear-gradient(rgba(0,0,0,{overlay}), rgba(0,0,0,{overlay + 0.1})), 
                        url("{st.session_state.wallpaper}") !important; 
            background-size: cover !important; background-attachment: fixed !important;
        }}
        .window-box {{ background: rgba(0, 5, 15, 0.93); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; min-height: 80vh; }}
        .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.6); padding: 10px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {accent}11; }}
        h1, h2, h3, p, label {{ color: {accent} !important; font-family: 'Courier New', monospace !important; }}
        [data-testid="stButton"] button {{ background: transparent !important; color: {accent} !important; border: 1px solid {accent}55 !important; width: 100%; border-radius: 10px !important; }}
        [data-testid="stButton"] button:hover {{ background: {accent}11 !important; border-color: {accent} !important; }}
        .status-dot {{ height: 10px; width: 10px; background-color: {alert_c}; border-radius: 50%; box-shadow: 0 0 10px {alert_c}; display: inline-block; }}
        .log-box {{ background: #000; color: #0f0; font-family: 'Courier New', monospace; padding: 10px; border-radius: 10px; font-size: 0.75rem; height: 150px; border: 1px solid #0f02; overflow-y: scroll; }}
        audio, video {{ filter: sepia(1) saturate(5) hue-rotate(160deg); border-radius: 10px; }}
        </style>
    """, unsafe_allow_html=True)

# --- 5. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "DESKTOP",
        "wallpaper": "https://images.unsplash.com",
        "accent_color": "#00f2ff",
        "brightness": 0.5,
        "library": load_history(),
        "logs": ["OS v9.9.8 KERNEL SECURED"],
        "system_alert": False,
        "last_image_res": None, "last_audio_res": None, "last_synth_p": ""
    })

apply_ui()

# --- 6. NAVIGATION & MODULER ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:20vh; font-size:4rem; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    cols = st.columns(6)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("🎬 MOVIE", "MOVIE"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        if cols[i].button(label): st.session_state.page = target; st.rerun()
else:
    st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
    nc = st.columns([1,1,1,1,1,1,1,0.5])
    nav_items = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "LIBRARY"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
    for i, (icon, target) in enumerate(nav_items):
        if nc[i].button(icon, key=f"n_{target}"): st.session_state.page = target; st.rerun()
    with nc[-1]: st.markdown(f'<div style="text-align:center; padding-top:5px;"><span class="status-dot"></span></div>', unsafe_allow_html=True)
    st.markdown('</div><div class="window-box">', unsafe_allow_html=True)

    if st.session_state.page == "SYNTH":
        p = st.text_area("PROMPT:", value=st.session_state.last_synth_p)
        if st.button("🔥 GENERERA KEDJA"):
            prog = st.progress(0, text="Renderar bild (Flux)...")
            img = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": p}, "SYNTH_IMAGE")
            url = clean_url(img)
            if url:
                st.session_state.last_image_res = url
                st.session_state.library.append({"type": "image", "url": url, "prompt": p})
                st.session_state.last_audio_res = sonify_logic(url, p, prog)
                prog.progress(100, text="KEDJA SLUTFÖRD.")
                save_history(); st.rerun()
        if st.session_state.last_image_res: st.image(st.session_state.last_image_res, width=400)
        if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

    elif st.session_state.page == "SYSTEM":
        st.write("### ⚙️ SYSTEM & SJÄLVTEST")
        col_ctrl, col_log = st.columns(2)
        with col_ctrl:
            st.session_state.accent_color = st.color_picker("ACCENT", st.session_state.accent_color)
            if st.button("🟢 RESET ALERT"): st.session_state.system_alert = False; st.rerun()
            if os.path.exists(ERROR_LOG_FILE):
                with open(ERROR_LOG_FILE, "r") as f:
                    st.download_button("📂 HÄMTA DIAGNOSTIK", f.read(), file_name="errors.log")
        with col_log:
            st.markdown(f'<div class="log-box">{"<br>".join(st.session_state.logs[::-1])}</div>', unsafe_allow_html=True)

    elif st.session_state.page == "LIBRARY":
        for i, item in enumerate(reversed(st.session_state.library)):
            with st.expander(f"{item['type'].upper()} - {item['prompt'][:20]}"):
                if item['type'] == "image": st.image(item['url'])
                elif item['type'] == "audio": st.audio(item['url'])
                if st.button("🗑 RADERA", key=f"del_{i}"):
                    st.session_state.library.pop(len(st.session_state.library)-1-i)
                    save_history(); st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
























































