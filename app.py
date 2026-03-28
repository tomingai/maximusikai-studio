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
# VERSION: 10.1.0 | STATUS: DYNAMIC ROUTING & AUTO-FIX | REGLER 1-21
st.set_page_config(page_title="MAXIMUSIK AI OS v10.1.0", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"
ERROR_LOG_FILE = "system_errors.log"

# --- 2. DIAGNOSTIK & AUTO-FIX (Regel 19 & 21) ---
def run_system_check():
    status = {}
    status["API_KEY"] = "REPLICATE_API_TOKEN" in st.secrets or os.environ.get("REPLICATE_API_TOKEN") is not None
    try:
        with open(DB_FILE, "r") as f: json.load(f)
        status["DATABASE"] = True
    except: status["DATABASE"] = False
    try:
        # Testar anslutning till huvudmodellen
        replicate.models.get("black-forest-labs/flux-schnell")
        status["AI_ENGINE"] = True
    except: status["AI_ENGINE"] = False
    return status

def repair_database():
    """Regel 21: Auto-Fix för korrupt historikfil."""
    try:
        backup_file = f"backup_{datetime.now().strftime('%Y%m%d')}.json"
        if os.path.exists(DB_FILE):
            os.rename(DB_FILE, backup_file)
        with open(DB_FILE, "w") as f:
            json.dump([], f)
        st.session_state.library = []
        add_log("SYSTEM: Databas återställd och backup skapad.")
        return True
    except: return False

def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    if is_error: st.session_state.system_alert = True
    st.session_state.logs.append(f"[{timestamp}] {'⚠️' if is_error else '🤖'} {message}")
    if len(st.session_state.logs) > 20: st.session_state.logs.pop(0)

def safe_replicate_run(model_alias, input_data, context="GENERAL"):
    """Dynamic Routing: Använder alias istället för fasta hashar (Regel 21)."""
    # Mappa alias till stabila sökvägar
    models = {
        "FLUX": "black-forest-labs/flux-schnell",
        "MUSIC": "meta/musicgen",
        "VISION": "lucataco/moondream2",
        "VIDEO": "stability-ai/video-diffusion"
    }
    target = models.get(model_alias, model_alias)
    
    for attempt in range(2):
        try:
            return replicate.run(target, input=input_data)
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

# --- 3. UI ENGINE ---
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
        .window-box {{ background: rgba(0, 5, 15, 0.9); backdrop-filter: blur(30px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; min-height: 80vh; }}
        .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.6); padding: 10px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {accent}11; }}
        h1, h2, h3, p, label {{ color: {accent} !important; font-family: 'Courier New', monospace !important; }}
        div[data-testid="stButton"] button {{
            background: transparent !important; color: {accent} !important;
            border: 1px solid {accent}55 !important; width: 100%; border-radius: 10px !important; height: 3rem;
        }}
        div[data-testid="stButton"] button:hover {{ background: {accent}11 !important; border-color: {accent} !important; }}
        .status-dot {{ height: 10px; width: 10px; background-color: {alert_c}; border-radius: 50%; box-shadow: 0 0 10px {alert_c}; display: inline-block; }}
        .log-box {{ background: #000; color: #0f0; font-family: 'Courier New', monospace; padding: 10px; border-radius: 10px; font-size: 0.75rem; height: 150px; border: 1px solid #0f02; overflow-y: scroll; }}
        audio, video {{ filter: sepia(1) saturate(5) hue-rotate(160deg); border-radius: 10px; width: 100%; }}
        </style>
    """, unsafe_allow_html=True)

# --- 4. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "DESKTOP",
        "wallpaper": "https://images.unsplash.com",
        "accent_color": "#00f2ff",
        "brightness": 0.5,
        "library": load_history(),
        "logs": ["OS v10.1.0 KERNEL LOADED"],
        "system_alert": False,
        "last_image_res": None, "last_audio_res": None, "last_synth_p": ""
    })

apply_ui()

# --- 5. NAVIGATION & MODULER ---
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
        if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
    with nc[-1]: st.markdown(f'<div style="text-align:center; padding-top:5px;"><span class="status-dot"></span></div>', unsafe_allow_html=True)
    st.markdown('</div><div class="window-box">', unsafe_allow_html=True)

    # MODUL: SYSTEM (Återställd med Självtest & Auto-Fix)
    if st.session_state.page == "SYSTEM":
        st.write("### ⚙️ SYSTEM-DIAGNOSTIK")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔍 KÖR SJÄLVTEST"):
                results = run_system_check()
                for k, v in results.items(): st.write(f"{'✅' if v else '❌'} {k}")
            if st.button("🛠 REPARERA DATABAS"):
                if repair_database(): st.success("Åtgärdat!")
            st.session_state.accent_color = st.color_picker("ACCENT", st.session_state.accent_color)
            if st.button("🟢 RESET ALERT"): st.session_state.system_alert = False; st.rerun()
        with c2:
            st.write("### 📜 LIVE LOG")
            log_text = "<br>".join(st.session_state.logs[::-1])
            st.markdown(f'<div class="log-box">{log_text}</div>', unsafe_allow_html=True)

    # MODUL: SYNTH (Med Dynamic Routing)
    elif st.session_state.page == "SYNTH":
        st.write("### 🪄 NEURAL SYNTH")
        p = st.text_area("PROMPT:", value=st.session_state.last_synth_p)
        if st.button("🔥 GENERERA"):
            prog = st.progress(0, text="Renderar bild...")
            img = safe_replicate_run("FLUX", {"prompt": p}, "SYNTH_IMAGE")
            url = clean_url(img)
            if url:
                st.session_state.last_image_res = url
                st.session_state.library.append({"type": "image", "url": url, "prompt": p})
                prog.progress(70, text="Skapar ljud (Dynamic Route)...")
                snd = safe_replicate_run("MUSIC", {"prompt": p, "duration": 8}, "SYNTH_AUDIO")
                st.session_state.last_audio_res = clean_url(snd)
                if st.session_state.last_audio_res:
                    st.session_state.library.append({"type": "audio", "url": st.session_state.last_audio_res, "prompt": p})
                prog.progress(100, text="KLART.")
                save_history(); st.rerun()
        if st.session_state.last_image_res: st.image(st.session_state.last_image_res, width=400)
        if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

    elif st.session_state.page == "LIBRARY":
        for i, item in enumerate(reversed(st.session_state.library)):
            with st.expander(f"{item['type'].upper()} - {item['prompt'][:20]}"):
                if item['type'] == "image": st.image(item['url'])
                elif item['type'] == "audio": st.audio(item['url'])
                if st.button("🗑 RADERA", key=f"del_{i}"):
                    st.session_state.library.pop(len(st.session_state.library)-1-i)
                    save_history(); st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


























































