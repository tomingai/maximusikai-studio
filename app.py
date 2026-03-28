import streamlit as st
import replicate
import os
import json
import time
import traceback
import random
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v10.2.0", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"

# --- 2. SYSTEMFUNKTIONER (Regel 19 & 21) ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    icon = "⚠️" if is_error else "🤖"
    new_entry = f"[{timestamp}] {icon} {message}"
    if not st.session_state.logs or st.session_state.logs[-1][11:] != new_entry[11:]:
        st.session_state.logs.append(new_entry)
    if is_error: st.session_state.alarm = True
    if len(st.session_state.logs) > 20: st.session_state.logs.pop(0)

def auto_save():
    """Auto-Save till JSON (Systemkrav)."""
    try:
        with open(DB_FILE, "w") as f:
            json.dump(st.session_state.library, f)
    except: add_log("Auto-save failed", is_error=True)

def safe_replicate_run(model_alias, input_data, context="GENERAL"):
    """Neural Progress Bar + Auto-Retry logik."""
    models = {
        "FLUX": "black-forest-labs/flux-schnell",
        "MUSIC": "facebookresearch/musicgen:7a76a825701904677340e68d71563f69dba84f3353a16134a413d70f0322d7ad",
        "VISION": "lucataco/moondream2",
        "VIDEO": "stability-ai/video-diffusion:3f0bd67d0246b0336ca149257e3df179c3f3f5022137090b8f6c561ec9d77583"
    }
    target = models.get(model_alias, model_alias)
    
    # Neural Progress Bar (Regel 12)
    progress_text = f"Initialiserar neural länk: {model_alias}..."
    bar = st.progress(0, text=progress_text)
    
    try:
        for i in range(1, 10):
            time.sleep(0.05)
            bar.progress(i * 10, text=f"Krypterar datastream för {context}...")
        
        output = replicate.run(target, input=input_data)
        bar.progress(100, text="Länk etablerad.")
        time.sleep(0.3)
        bar.empty()
        return output
    except Exception as e:
        bar.empty()
        if "Invalid v" in str(e):
            add_log(f"REPAIR TRIGGERED: Stripping version hash for {model_alias}", is_error=True)
            return replicate.run(target.split(":")[0], input=input_data)
        add_log(f"API ERROR i {context}: {str(e)[:40]}", is_error=True)
        return None

# --- 3. INITIALISERING ---
if "library" not in st.session_state:
    if os.path.exists(DB_FILE):
        try: 
            with open(DB_FILE, "r") as f: lib = json.load(f)
        except: lib = []
    else: lib = []
    
    st.session_state.update({
        "page": "DESKTOP",
        "library": lib,
        "logs": ["MAXIMUSIK OS v10.2.0 KERNEL ONLINE"],
        "accent": "#00ffcc",
        "wallpaper": "https://images.unsplash.com",
        "last_img": None,
        "alarm": False
    })

# --- 4. UI ENGINE (Glasmorphism) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass-card {{ background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); border: 1px solid {accent}22; border-radius: 20px; padding: 25px; margin-bottom: 20px; }}
    .stButton>button {{ border: 1px solid {accent}44 !important; background: transparent !important; color: {accent} !important; border-radius: 12px; height: 3.5rem; }}
    .stButton>button:hover {{ background: {accent}11 !important; box-shadow: 0 0 20px {accent}33; }}
    .log-text {{ font-family: 'Courier New', monospace; font-size: 0.85rem; color: {accent}; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:30px; padding-top:15vh; color:{accent}; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    if st.session_state.alarm: st.error("🚨 SYSTEMVARNING: Anomalier detekterade i loggen.")
    
    cols = st.columns(6)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("🎬 MOVIE", "MOVIE"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        if cols[i].button(label): st.session_state.page = target; st.rerun()
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📜 LIVE-LOGG")
    for log in reversed(st.session_state.logs):
        st.markdown(f'<p class="log-text">{log}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Nav-bar för undersidor
    st.markdown('<div class="glass-card" style="padding: 10px;">', unsafe_allow_html=True)
    nc = st.columns(7)
    nav = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "LIBRARY"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
    for i, (icon, target) in enumerate(nav):
        if nc[i].button(icon): st.session_state.page = target; st.rerun()
    st.markdown('</div><div class="glass-card">', unsafe_allow_html=True)

    # MODUL-LOGIK
    if st.session_state.page == "SYNTH":
        st.subheader("🪄 NEURAL IMAGE SYNTH")
        p = st.text_input("Beskriv visionen:")
        if st.button("RENDER"):
            res = safe_replicate_run("FLUX", {"prompt": p}, "SYNTH")
            if res:
                img_url = res[0] if isinstance(res, list) else res
                st.session_state.last_img = img_url
                st.image(img_url)
                st.session_state.library.append({"type": "IMG", "url": img_url, "prompt": p, "date": str(datetime.now())})
                auto_save(); add_log(f"Bild renderad: {p[:20]}")

    elif st.session_state.page == "AUDIO":
        st.subheader("🎧 NEURAL AUDIO ENGINE")
        ap = st.text_input("Prompt (Stil, BPM, Instrument):")
        if st.button("KOMPONERA"):
            res = safe_replicate_run("MUSIC", {"prompt": ap, "duration": 10}, "AUDIO")
            if res:
                st.audio(res)
                st.session_state.library.append({"type": "AUDIO", "url": res, "prompt": ap, "date": str(datetime.now())})
                auto_save(); add_log(f"Ljudfil klar: {ap[:20]}")

    elif st.session_state.page == "MOVIE":
        st.subheader("🎬 MOTION ENGINE")
        if st.session_state.last_img:
            st.image(st.session_state.last_img, width=400, caption="Källbild")
            if st.button("ANIMERA"):
                res = safe_replicate_run("VIDEO", {"input_image": st.session_state.last_img}, "VIDEO")
                if res:
                    st.video(res)
                    st.session_state.library.append({"type": "VIDEO", "url": res, "prompt": "Animerad bild", "date": str(datetime.now())})
                    auto_save()
        else: st.warning("Ingen källbild hittades. Kör SYNTH först.")

    elif st.session_state.page == "LIBRARY":
        st.subheader("📚 MULTIMEDIA-ARKIV")
        if not st.session_state.library: st.info("Arkivet är tomt.")
        for i, item in enumerate(reversed(st.session_state.library)):
            with st.expander(f"{item['type']} | {item['prompt'][:30]}..."):
                if item['type'] == "IMG": st.image(item['url'])
                elif item['type'] == "AUDIO": st.audio(item['url'])
                elif item['type'] == "VIDEO": st.video(item['url'])
                if st.button("ANVÄND SOM WALLPAPER", key=f"wall_{i}"):
                    st.session_state.wallpaper = item['url']; st.rerun()

    elif st.session_state.page == "ENGINE":
        st.subheader("👁️ VISION ENGINE (ANALYS)")
        v_url = st.text_input("Bild-URL för analys:", value=st.session_state.last_img if st.session_state.last_img else "")
        if st.button("KÖR ANALYS"):
            res = safe_replicate_run("VISION", {"image": v_url, "prompt": "Describe this image for a prompt engineer."}, "VISION")
            st.success(res); add_log("Vision-analys slutförd.")

    elif st.session_state.page == "SYSTEM":
        st.subheader("⚙️ SYSTEMINSTÄLLNINGAR")
        st.session_state.accent = st.color_picker("Välj System-Accent", st.session_state.accent)
        if st.button("RESET ALARM"): st.session_state.alarm = False; st.rerun()
        if st.button("REPARERA DATABAS"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.library = []; st.success("Databas rensad.")

    st.markdown('</div>', unsafe_allow_html=True)
































































