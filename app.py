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
# VERSION: 9.4.0 | STATUS: ALL APPS ONLINE | REGLER 1-17
st.set_page_config(page_title="MAXIMUSIK AI OS v9.4.0", layout="wide", initial_sidebar_state="collapsed")

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
    for attempt in range(3):
        try:
            return replicate.run(model, input=input_data)
        except Exception:
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

# --- 3. CORE AI LOGIC ---
def clean_url(res):
    try:
        if isinstance(res, list) and len(res) > 0: return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except: return None

def sonify_logic(image_url, prompt_context, progress_bar):
    progress_bar.progress(70, text="SONIFY: Analyserar bild...")
    descr = safe_replicate_run("lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                              {"image": image_url, "prompt": "Music mood in 5 words."}, "SONIFY_ANALYSIS")
    if descr:
        progress_bar.progress(85, text=f"SONIFY: Skapar ljud ({descr})...")
        snd = safe_replicate_run("meta/musicgen:671ac645", {"prompt": f"{descr}, {prompt_context}", "duration": 8}, "SONIFY_GEN")
        url = clean_url(snd)
        if url:
            st.session_state.library.append({"type": "audio", "url": url, "prompt": f"Auto-Mood: {descr}"})
            return url
    return None

def get_random_prompt(genre=None):
    if not genre: genre = random.choice(["CYBERPUNK", "SPACE", "NATURE", "RETRO", "EUPHORIC", "DARK TECHNO"])
    db = {
        "CYBERPUNK": ["Neon DJ in rainy Tokyo", "Android playing synth", "Cybernetic skyscraper"],
        "SPACE": ["Nebula glass sphere", "Astronaut on crystal planet", "Black hole horizon"],
        "NATURE": ["Bioluminescent forest", "Mossy stone golem", "Liquid gold waterfall"],
        "RETRO": ["80s grid sunset Ferrari", "Pixel arcade 1984", "Vaporwave statue"],
        "EUPHORIC": ["Sunlight through clouds", "Light wing angel", "Dream festival"],
        "DARK TECHNO": ["Bunker red lasers", "Industrial shadows", "Mechanical heart"]
    }
    return random.choice(db.get(genre, db["CYBERPUNK"]))

# --- 4. SYSTEM STATES ---
states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "brightness": 0.5,
    "library": load_history(),
    "logs": ["OS v9.4.0 FULL APPS ONLINE"],
    "system_alert": False,
    "last_synth_p": "",
    "last_image_res": None, "last_audio_res": None, "last_video_res": None
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
        [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,{overlay}), rgba(0,0,0,{overlay + 0.1})), url("{st.session_state.wallpaper}") !important; background-size: cover !important; }}
        .window-box {{ background: rgba(0, 5, 15, 0.94); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 25px; padding: 25px; min-height: 70vh; }}
        .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.6); padding: 8px; border-radius: 12px; margin-bottom: 15px; border: 1px solid {accent}22; align-items: center; }}
        .status-dot {{ height: 10px; width: 10px; background-color: {alert_c}; border-radius: 50%; box-shadow: 0 0 10px {alert_c}; animation: {"blink 1s infinite" if st.session_state.system_alert else "none"}; display: inline-block; }}
        @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
        h1, h2, h3, p {{ color: {accent} !important; font-family: 'Courier New', monospace; }}
        .stButton > button {{ background: rgba(0,0,0,0.4) !important; border: 1px solid {accent}33 !important; color: {accent} !important; width: 100%; }}
        audio, video {{ filter: sepia(1) saturate(5) hue-rotate(160deg); border-radius: 12px; margin-top: 10px; }}
        .log-box {{ background: #000; color: #0f0; font-family: 'Courier New', monospace; padding: 10px; border-radius: 5px; font-size: 0.75rem; height: 180px; overflow-y: scroll; border: 1px solid #0f03; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 6. NAVIGATION ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:20px; padding-top:20vh; font-size:4rem; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    cols = st.columns(6)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("🎬 MOVIE", "MOVIE"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        if cols[i].button(label, key=f"desktop_{target}"):
            st.session_state.page = target; st.rerun()
else:
    st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
    nc = st.columns([1,1,1,1,1,1,1,0.5]) 
    nav_items = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "LIBRARY"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
    for i, (icon, target) in enumerate(nav_items):
        if nc[i].button(icon, key=f"nav_{target}"):
            st.session_state.page = target; st.rerun()
    with nc[7]:
        st.markdown(f'<div style="text-align:center; padding-top:5px;"><span class="status-dot"></span></div>', unsafe_allow_html=True)
    st.markdown('</div><div class="window-box">', unsafe_allow_html=True)

    # --- MODULER ---
    if st.session_state.page == "SYNTH":
        st.write("### 🪄 NEURAL SYNTH")
        c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
        with c1: genre = st.selectbox("STIL:", ["CYBERPUNK", "SPACE", "NATURE", "RETRO", "EUPHORIC", "DARK TECHNO"])
        with c2: 
            if st.button("🎲 SLUMPA"):
                st.session_state.last_synth_p = get_random_prompt(genre); st.rerun()
        with c3:
            if st.button("✨ CHAOS"):
                st.session_state.last_synth_p = get_random_prompt(); st.rerun()
        
        p = st.text_area("BILD PROMPT:", value=st.session_state.last_synth_p, height=80)
        if st.button("🔥 GENERERA ALLT"):
            prog = st.progress(0, text="Initierar...")
            img_raw = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": p}, "SYNTH_RENDER")
            url = clean_url(img_raw)
            if url:
                st.session_state.last_image_res = url
                st.session_state.library.append({"type": "image", "url": url, "prompt": p})
                st.session_state.last_audio_res = sonify_logic(url, p, prog)
                prog.progress(100, text="FÄRDIG.")
                save_history(); st.rerun()
        if st.session_state.last_image_res: st.image(st.session_state.last_image_res, width=400)

    elif st.session_state.page == "AUDIO":
        st.write("### 🎧 MANUAL AUDIO SYNTH")
        ap = st.text_input("VAD VILL DU HÖRA?", placeholder="Ex: Heavy industrial techno 120bpm")
        if st.button("🔊 SKAPA LJUD"):
            prog = st.progress(30, text="Genererar vågformer...")
            res = safe_replicate_run("meta/musicgen:671ac645", {"prompt": ap, "duration": 10}, "AUDIO_GEN")
            url = clean_url(res)
            if url:
                st.session_state.last_audio_res = url
                st.session_state.library.append({"type": "audio", "url": url, "prompt": ap})
                save_history(); st.rerun()
        if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

    elif st.session_state.page == "MOVIE":
        st.write("### 🎬 MOVIE DIFFUSION")
        if st.session_state.last_image_res:
            st.image(st.session_state.last_image_res, width=200, caption="Källa")
            if st.button("🎞 ANIMERA BILD"):
                prog = st.progress(20, text="Beräknar rörelsevektorer...")
                res = safe_replicate_run("stability-ai/video-diffusion:3f0457148a1aa577d638be204a4002c1d58ce1bd57b7f7c4d328b3d24883990c", {"input_image": st.session_state.last_image_res}, "VIDEO_GEN")
                url = clean_url(res)
                if url:
                    st.session_state.last_video_res = url
                    st.session_state.library.append({"type": "video", "url": url, "prompt": "AI Motion"})
                    save_history(); st.rerun()
        else: st.warning("Skapa en bild i SYNTH först!")
        if st.session_state.last_video_res: st.video(st.session_state.last_video_res)

    elif st.session_state.page == "ENGINE":
        st.write("### 🖼 WALLPAPER ENGINE")
        wp = st.text_input("PROMPT FÖR NY BAKGRUND:")
        if st.button("🖼 GENERERA"):
            img = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": wp}, "WALLPAPER_GEN")
            url = clean_url(img)
            if url:
                st.session_state.wallpaper = url; st.rerun()

    elif st.session_state.page == "LIBRARY":
        st.write("### 📚 ARKIV")
        for i, item in enumerate(reversed(st.session_state.library)):
            with st.expander(f"{item['type'].upper()} - {item['prompt'][:30]}..."):
                if item['type'] == "image": st.image(item['url'])
                elif item['type'] == "audio": st.audio(item['url'])
                elif item['type'] == "video": st.video(item['url'])
                st.download_button(f"Ladda ner", requests.get(item['url']).content, key=f"dl_{i}")

    elif st.session_state.page == "SYSTEM":
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.accent_color = st.color_picker("FÄRG", st.session_state.accent_color)
            st.session_state.brightness = st.slider("LJUS", 0.1, 1.0, st.session_state.brightness)
            if st.button("🟢 RESET ALERT"): st.session_state.system_alert = False; st.rerun()
        with c2:
            st.markdown(f'<div class="log-box">{"<br>".join(st.session_state.logs[::-1])}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)




















































