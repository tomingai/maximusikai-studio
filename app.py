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
# VERSION: 9.9.2 | STATUS: RECOVERY COMMAND READY | REGLER 1-18
st.set_page_config(page_title="MAXIMUSIK AI OS v9.9.2", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"
ERROR_LOG_FILE = "system_errors.log"

# --- 2. DIAGNOSTIK & PERSISTENCE ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    if is_error: st.session_state.system_alert = True
    st.session_state.logs.append(f"[{timestamp}] {'⚠️' if is_error else '🤖'} {message}")
    if len(st.session_state.logs) > 20: st.session_state.logs.pop(0)

def safe_replicate_run(model, input_data, context="GENERAL"):
    for attempt in range(3):
        try:
            return replicate.run(model, input=input_data)
        except:
            if attempt == 2:
                report_error(context)
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

# --- 3. AI LOGIC (Sonify-kedja) ---
def sonify_logic(image_url, prompt_context, progress_bar):
    progress_bar.progress(70, text="SONIFY: Analyserar...")
    descr = safe_replicate_run("lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                              {"image": image_url, "prompt": "Music mood in 5 words."}, "SONIFY_ANALYSIS")
    progress_bar.progress(85, text="SONIFY: Skapar ljud...")
    snd = safe_replicate_run("meta/musicgen:671ac645", {"prompt": f"{descr}, {prompt_context}", "duration": 8}, "SONIFY_GEN")
    url = clean_url(snd)
    if url:
        st.session_state.library.append({"type": "audio", "url": url, "prompt": f"Mood: {descr}"})
        return url
    return None

# --- 4. UI & STATES ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "DESKTOP",
        "wallpaper": "https://images.unsplash.com",
        "accent_color": "#00f2ff",
        "brightness": 0.5,
        "library": load_history(),
        "logs": ["OS v9.9.2 BOOT COMPLETE"],
        "system_alert": False,
        "last_image_res": None, "last_audio_res": None, "last_video_res": None,
        "last_synth_p": ""
    })

def apply_ui():
    accent = st.session_state.accent_color
    bright = st.session_state.brightness
    overlay = 1.0 - bright 
    alert_c = "#ff0000" if st.session_state.system_alert else "#00ff00"
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,{overlay}), rgba(0,0,0,{overlay + 0.1})), url("{st.session_state.wallpaper}") !important; background-size: cover !important; }}
        .window-box {{ background: rgba(0, 5, 15, 0.95); backdrop-filter: blur(40px); border: 1px solid {accent}44; border-radius: 20px; padding: 25px; min-height: 80vh; }}
        .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.8); padding: 10px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {accent}22; }}
        .status-dot {{ height: 10px; width: 10px; background-color: {alert_c}; border-radius: 50%; box-shadow: 0 0 10px {alert_c}; display: inline-block; }}
        h1, h2, h3, p {{ color: {accent} !important; font-family: 'Courier New', monospace; }}
        .stButton > button {{ background: {accent}11 !important; border: 1px solid {accent}33 !important; color: {accent} !important; }}
        audio, video {{ filter: sepia(1) saturate(5) hue-rotate(160deg); border-radius: 10px; }}
        .log-box {{ background: #000; color: #0f0; font-family: 'Courier New', monospace; padding: 10px; border-radius: 10px; font-size: 0.75rem; height: 120px; border: 1px solid #0f02; overflow-y: scroll; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 5. NAVIGATION ---
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

    if st.session_state.page == "SYNTH":
        p = st.text_area("PROMPT:", value=st.session_state.last_synth_p)
        if st.button("🔥 GENERERA KEDJA"):
            prog = st.progress(0, text="Renderar...")
            img = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": p})
            url = clean_url(img)
            if url:
                st.session_state.last_image_res = url
                st.session_state.library.append({"type": "image", "url": url, "prompt": p})
                st.session_state.last_audio_res = sonify_logic(url, p, prog)
                save_history(); st.rerun()
        if st.session_state.last_image_res: st.image(st.session_state.last_image_res, width=400)

    elif st.session_state.page == "AUDIO":
        ap = st.text_input("MANUAL PROMPT:")
        if st.button("🔊 SKAPA"):
            res = safe_replicate_run("meta/musicgen:671ac645", {"prompt": ap, "duration": 10})
            url = clean_url(res)
            if url:
                st.session_state.last_audio_res = url
                st.session_state.library.append({"type": "audio", "url": url, "prompt": ap})
                save_history(); st.rerun()
        if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

    elif st.session_state.page == "MOVIE":
        if st.session_state.last_image_res:
            if st.button("🎞 ANIMERA"):
                res = safe_replicate_run("stability-ai/video-diffusion:3f0457148a1aa577d638be204a4002c1d58ce1bd57b7f7c4d328b3d24883990c", {"input_image": st.session_state.last_image_res})
                url = clean_url(res)
                if url:
                    st.session_state.last_video_res = url
                    st.session_state.library.append({"type": "video", "url": url, "prompt": "Motion"})
                    save_history(); st.rerun()
        if st.session_state.last_video_res: st.video(st.session_state.last_video_res)

    elif st.session_state.page == "LIBRARY":
        for i, item in enumerate(reversed(st.session_state.library)):
            with st.expander(f"{item['type'].upper()} - {item['prompt'][:20]}"):
                if item['type'] == "image": st.image(item['url'])
                elif item['type'] == "audio": st.audio(item['url'])
                elif item['type'] == "video": st.video(item['url'])
                if st.button("🗑 RADERA", key=f"del_{i}"):
                    st.session_state.library.pop(len(st.session_state.library)-1-i)
                    save_history(); st.rerun()

    elif st.session_state.page == "SYSTEM":
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.accent_color = st.color_picker("FÄRG", st.session_state.accent_color)
            if st.button("🟢 RESET ALERT"): st.session_state.system_alert = False; st.rerun()
            st.success("MBR & RULES 1-18 LOCKED")
        with c2:
            log_text = "<br>".join(st.session_state.logs[::-1])
            st.markdown(f'<div class="log-box">{log_text}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)





















































