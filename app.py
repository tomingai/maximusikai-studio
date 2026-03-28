import streamlit as st
import replicate
import os
import random
import requests
import json
import traceback
from datetime import datetime

# --- 1. SYSTEM-KONFIGURATION & REGLER ---
# VERSION: 9.2.3 | STATUS: DIAGNOSTICS ACTIVE | REGLER 1-14
st.set_page_config(page_title="MAXIMUSIK AI OS v9.2.3", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"
ERROR_LOG_FILE = "system_errors.log"

# --- 2. DIAGNOSTIK & LOGGNING (Regel 13 & 14) ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    prefix = "⚠️ ERROR" if is_error else "INFO"
    st.session_state.logs.append(f"[{timestamp}] {prefix}: {message}")
    if len(st.session_state.logs) > 25: st.session_state.logs.pop(0)

def report_error(context):
    """Fångar hela krasch-rapporten och sparar till fil (Regel 14)."""
    error_data = traceback.format_exc()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ERROR_LOG_FILE, "a") as f:
        f.write(f"\n--- ERROR AT {timestamp} IN {context} ---\n{error_data}\n")
    add_log(f"Kritisk krasch i {context}. Se systemlogg.", is_error=True)

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

# Initialisera states
states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "brightness": 0.5,
    "library": load_history(),
    "logs": ["OS DIAGNOSTICS V1 ACTIVE", "KERNEL READY"],
    "last_synth_p": "",
    "last_audio_res": None, "last_image_res": None, "last_video_res": None
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 3. CORE LOGIC ---
def get_url(res):
    try:
        if isinstance(res, list): return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except: return str(res)

def sonify_logic(image_url, prompt_context):
    try:
        add_log("AI: Analyserar bild för sonifiering...")
        descr = replicate.run("lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                             input={"image": image_url, "prompt": "Music mood in 5 words."})
        res = replicate.run("meta/musicgen:671ac645", 
                             input={"prompt": f"{descr}, {prompt_context}", "duration": 8})
        url = get_url(res)
        st.session_state.library.append({"type": "audio", "url": url, "prompt": f"Sonify: {descr}"})
        save_history(); return url
    except:
        report_error("SONIFY_LOGIC")
        return None

# --- 4. UI ENGINE (Regel 2 & 9) ---
def apply_ui():
    accent = st.session_state.accent_color
    bright = st.session_state.brightness
    overlay = 1.0 - bright 
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,{overlay}), rgba(0,0,0,{overlay + 0.1})), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; background-attachment: fixed !important;
        }}
        .window-box {{ background: rgba(0, 5, 15, 0.94); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 25px; padding: 25px; margin-top: 5px; }}
        .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.6); padding: 8px; border-radius: 12px; margin-bottom: 15px; border: 1px solid {accent}22; }}
        .log-box {{ background: #000; color: #0f0; font-family: 'Courier New', monospace; padding: 10px; border-radius: 5px; font-size: 0.75rem; border: 1px solid #0f03; height: 300px; overflow-y: scroll; }}
        h1, h2, h3, p, label {{ color: {accent} !important; font-family: 'Courier New', monospace !important; text-shadow: 0 0 8px {accent}44; }}
        .stButton > button {{ background: rgba(0,0,0,0.4) !important; border: 1px solid {accent}33 !important; color: {accent} !important; border-radius: 8px !important; }}
        audio, video {{ filter: sepia(1) saturate(5) hue-rotate(160deg); width: 100%; border-radius: 12px; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 5. NAVIGATION ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:20px; padding-top:20vh; font-size:4rem; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    cols = st.columns(6)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("🎬 MOVIE", "MOVIE"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"d_nav_{target}"):
                st.session_state.page = target; st.rerun()

else:
    _, win_col, _ = st.columns([0.02, 0.96, 0.02])
    with win_col:
        st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
        nc = st.columns(7)
        nav_items = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "LIBRARY"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
        for i, (icon, target) in enumerate(nav_items):
            if nc[i].button(icon, key=f"win_nav_{target}", use_container_width=True):
                st.session_state.page = target; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="window-box">', unsafe_allow_html=True)

        # SYNTH
        if st.session_state.page == "SYNTH":
            p = st.text_area("IMAGE PROMPT:", value=st.session_state.last_synth_p)
            if st.button("RENDER UNIVERSE", use_container_width=True):
                try:
                    add_log(f"IMAGE: Renderar '{p[:15]}...'")
                    img_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_image_res = get_url(img_res)
                    st.session_state.library.append({"type": "image", "url": st.session_state.last_image_res, "prompt": p})
                    st.session_state.last_audio_res = sonify_logic(st.session_state.last_image_res, p)
                    save_history(); st.rerun()
                except: report_error("SYNTH_RENDER")
            if st.session_state.last_image_res: st.image(st.session_state.last_image_res, width=400)

        # AUDIO
        elif st.session_state.page == "AUDIO":
            ap = st.text_input("AUDIO PROMPT:")
            if st.button("GENERATE"):
                try:
                    add_log(f"AUDIO: Skapar '{ap[:15]}'")
                    res = replicate.run("meta/musicgen:671ac645", input={"prompt": ap, "duration": 10})
                    st.session_state.last_audio_res = get_url(res)
                    st.session_state.library.append({"type": "audio", "url": st.session_state.last_audio_res, "prompt": ap})
                    save_history(); st.rerun()
                except: report_error("AUDIO_GEN")
            if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

        # MOVIE
        elif st.session_state.page == "MOVIE":
            if st.session_state.last_image_res:
                if st.button("ANIMATE SOURCE"):
                    try:
                        add_log("VIDEO: Renderar motion...")
                        res = replicate.run("stability-ai/video-diffusion:3f0457148a1aa577d638be204a4002c1d58ce1bd57b7f7c4d328b3d24883990c", 
                                            input={"input_image": st.session_state.last_image_res})
                        st.session_state.last_video_res = get_url(res)
                        st.session_state.library.append({"type": "video", "url": st.session_state.last_video_res, "prompt": "AI Motion"})
                        save_history(); st.rerun()
                    except: report_error("VIDEO_RENDER")
            if st.session_state.last_video_res: st.video(st.session_state.last_video_res)

        # ARKIV
        elif st.session_state.page == "LIBRARY":
            st.write("### 📚 ARKIV")
            for i, item in enumerate(reversed(st.session_state.library)):
                with st.expander(f"{item['type'].upper()} - {item['prompt'][:15]}"):
                    if item['type'] == "image": st.image(item['url'])
                    elif item['type'] == "audio": st.audio(item['url'])
                    elif item['type'] == "video": st.video(item['url'])
                    try:
                        resp = requests.get(item['url'])
                        st.download_button("💾 DOWNLOAD", resp.content, file_name=f"maxi_{i}.bin", key=f"dl_{i}")
                    except: add_log(f"DOWNLOAD: Kunde inte hämta fil {i}", is_error=True)

        # ENGINE
        elif st.session_state.page == "ENGINE":
            wp_p = st.text_input("NEW WALLPAPER:")
            if st.button("GENERATE"):
                try:
                    img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": wp_p})
                    st.session_state.wallpaper = get_url(img); st.rerun()
                except: report_error("WALLPAPER_GEN")

        # SYSTEM (Med Live-logg & Error Report)
        elif st.session_state.page == "SYSTEM":
            col1, col2 = st.columns(2)
            with col1:
                st.write("### ⚙️ SETTINGS")
                st.session_state.accent_color = st.color_picker("ACCENT", st.session_state.accent_color)
                st.session_state.brightness = st.slider("BRIGHTNESS", 0.1, 1.0, st.session_state.brightness)
                if os.path.exists(ERROR_LOG_FILE):
                    with open(ERROR_LOG_FILE, "r") as f:
                        st.download_button("📂 HÄMTA FEL-LOGG FÖR FIX", f.read(), file_name="diagnostics.log")
            with col2:
                st.write("### 📜 LIVE LOG")
                log_text = "\n".join(st.session_state.logs[::-1])
                st.markdown(f'<div class="log-box">{log_text.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)















































