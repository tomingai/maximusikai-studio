import streamlit as st
import replicate
import os
import json
import time
import traceback
import random
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v10.3.5", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"

# --- 2. SJÄLVTEST & DIAGNOSTIK (Regel 19) ---
def run_diagnostics():
    add_log("RUNNING SYSTEM SELF-TEST...")
    status = {"API": False, "DB": False}
    if os.environ.get("REPLICATE_API_TOKEN"): status["API"] = True
    if os.path.exists(DB_FILE): status["DB"] = True
    add_log(f"DIAGNOSTICS: API={'OK' if status['API'] else 'FAIL'}, DB={'OK' if status['DB'] else 'FAIL'}")
    return status

# --- 3. SYSTEMFUNKTIONER (Regel 8, 10, 21) ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    icon = "⚠️" if is_error else "🤖"
    new_entry = f"[{timestamp}] {icon} {message}"
    if not st.session_state.logs or st.session_state.logs[-1][11:] != new_entry[11:]:
        st.session_state.logs.append(new_entry)
    if is_error: st.session_state.alarm = True
    if len(st.session_state.logs) > 12: st.session_state.logs.pop(0)

def auto_save():
    try:
        with open(DB_FILE, "w") as f:
            json.dump(st.session_state.library, f)
        add_log("AUTO-SAVE: PERSISTENCE SECURED")
    except: add_log("AUTO-SAVE FAILED", is_error=True)

def safe_replicate_run(model_alias, input_data, context="GEN"):
    models = {
        "FLUX": "black-forest-labs/flux-schnell",
        "MUSIC": "facebookresearch/musicgen:7a76a825701904677340e68d71563f69dba84f3353a16134a413d70f0322d7ad",
        "VISION": "lucataco/moondream2",
        "VIDEO": "stability-ai/video-diffusion:3f0bd67d0246b0336ca149257e3df179c3f3f5022137090b8f6c561ec9d77583"
    }
    target = models.get(model_alias, model_alias)
    bar = st.progress(0, text=f"NEURAL LINK: {model_alias}...")
    try:
        for i in range(1, 11):
            time.sleep(0.05)
            bar.progress(i * 10)
        output = replicate.run(target, input=input_data)
        bar.empty()
        return output
    except Exception as e:
        bar.empty()
        if "Invalid v" in str(e):
            add_log(f"REPAIR: STRIPPING HASH FOR {model_alias}", is_error=True)
            return replicate.run(target.split(":")[0], input=input_data)
        add_log(f"CRASH IN {context}: {str(e)[:30]}", is_error=True)
        return None

# --- 4. INITIALISERING & UI ---
if "page" not in st.session_state:
    if os.path.exists(DB_FILE):
        try: 
            with open(DB_FILE, "r") as f: lib = json.load(f)
        except: lib = []
    else: lib = []
    
    st.session_state.update({
        "page": "DESKTOP", "library": lib, "logs": ["KERNEL v10.3.5 ONLINE"],
        "accent": "#00ffcc", "wallpaper": "https://images.unsplash.com",
        "last_img": None, "alarm": False
    })
    run_diagnostics()

accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("{st.session_state.wallpaper}"); background-size: cover; background-attachment: fixed; }}
    .glass-card {{ background: rgba(0, 5, 15, 0.85); backdrop-filter: blur(25px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px; }}
    .stButton>button {{ border: 1px solid {accent}44 !important; color: {accent} !important; background: transparent !important; border-radius: 12px; transition: 0.3s; }}
    .stButton>button:hover {{ background: {accent}22 !important; box-shadow: 0 0 15px {accent}44; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass-card" style="padding: 10px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "ARKIV"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
for i, (icon, target) in enumerate(nav):
    if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:10vh; color:{accent}; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    if st.session_state.alarm: st.error("🚨 WARNING: SYSTEM ANOMALIES DETECTED")
    
    cmd = st.text_input("TERMINAL >", placeholder="Type /test, /rules, /clear or /sonify...")
    if cmd == "/test": run_diagnostics(); st.rerun()
    elif cmd == "/rules": st.json({"v": "10.3.5", "rules": "1-22 active"})
    elif cmd == "/clear": st.session_state.logs = []; st.rerun()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📜 SYSTEM LOG")
    for log in reversed(st.session_state.logs): st.code(log)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "SYNTH":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    p = st.text_input("IMAGE PROMPT:")
    if st.button("RENDER"):
        res = safe_replicate_run("FLUX", {"prompt": p}, "SYNTH")
        if res:
            st.session_state.last_img = res
            st.image(res)
            st.session_state.library.append({"type": "IMG", "url": res, "prompt": p, "ts": str(datetime.now())})
            auto_save(); add_log(f"IMAGE GENERATED: {p[:15]}...")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "AUDIO":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    ap = st.text_input("AUDIO PROMPT:")
    if st.button("COMPOSE"):
        res = safe_replicate_run("MUSIC", {"prompt": ap, "duration": 8}, "AUDIO")
        if res:
            st.audio(res)
            st.session_state.library.append({"type": "AUDIO", "url": res, "prompt": ap, "ts": str(datetime.now())})
            auto_save(); add_log(f"AUDIO COMPOSED: {ap[:15]}...")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📚 MULTIMEDIA ARCHIVE")
    if not st.session_state.library: st.info("ARCHIVE EMPTY.")
    for i, item in enumerate(reversed(st.session_state.library)):
        with st.expander(f"{item['type']} | {item['prompt'][:30]}..."):
            if item['type'] == "IMG": 
                st.image(item['url'])
                if st.button("SET WALLPAPER", key=f"w_{i}"): st.session_state.wallpaper = item['url']; st.rerun()
            elif item['type'] == "AUDIO": st.audio(item['url'])
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "SYSTEM":
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.session_state.accent = st.color_picker("ACCENT COLOR", st.session_state.accent)
    if st.button("FORCE DIAGNOSTICS"): run_diagnostics(); st.rerun()
    if st.button("RESET ALARM"): st.session_state.alarm = False; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

































































