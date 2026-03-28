import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v10.4.5", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"

# --- 2. SYSTEMFUNKTIONER (Regel 19, 21) ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    icon = "⚠️" if is_error else "🤖"
    new_entry = f"[{timestamp}] {icon} {message}"
    if not st.session_state.logs or st.session_state.logs[-1][11:] != new_entry[11:]:
        st.session_state.logs.append(new_entry)
    if is_error: st.session_state.alarm = True
    if len(st.session_state.logs) > 20: st.session_state.logs.pop(0)

def safe_replicate_run(model_alias, input_data):
    models = {
        "FLUX": "black-forest-labs/flux-schnell",
        "MUSIC": "facebookresearch/musicgen:7a76a825701904677340e68d71563f69dba84f3353a16134a413d70f0322d7ad",
        "VIDEO": "stability-ai/video-diffusion:3f0bd67d0246b0336ca149257e3df179c3f3f5022137090b8f6c561ec9d77583"
    }
    target = models.get(model_alias, model_alias)
    bar = st.progress(0, text=f"Neural länk: {model_alias}...")
    try:
        output = replicate.run(target, input=input_data)
        bar.empty()
        return output
    except Exception as e:
        bar.empty()
        if "Invalid v" in str(e):
            add_log(f"REPAIR: Stripping hash för {model_alias}", is_error=True)
            return replicate.run(target.split(":"), input=input_data)
        add_log(f"Krasch: {str(e)[:30]}", is_error=True)
        return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "DESKTOP", "library": [], "logs": ["OS v10.4.5 KERNEL ONLINE"],
        "accent": "#00f2ff", "wallpaper": "https://images.unsplash.com",
        "last_img": None, "alarm": False
    })

# --- 4. UI ENGINE (Glasmorphism) ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed;
    }}
    .glass {{ background: rgba(0, 5, 15, 0.8); backdrop-filter: blur(30px); border: 1px solid {accent}22; border-radius: 20px; padding: 30px; }}
    .stButton>button {{ border: 1px solid {accent}44 !important; color: {accent} !important; background: transparent !important; border-radius: 12px; height: 3.5rem; }}
    .stButton>button:hover {{ background: {accent}11 !important; box-shadow: 0 0 15px {accent}33; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px; margin-bottom: 25px; border-radius: 15px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "ARKIV"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
for i, (icon, target) in enumerate(nav):
    if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:35px; padding-top:20vh; color:{accent}; font-weight:900; opacity:0.8;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    if st.session_state.alarm: st.error("🚨 SYSTEM ALARM ACTIVE - CHECK SYSTEM LOGS")
    
    cmd = st.text_input("CMD >", placeholder="Enter command...")
    if cmd == "/rules": st.info("Rules 1-22 Active. Check SYSTEM for details.")
    elif cmd == "/clear": st.session_state.logs = []; add_log("Logs cleared."); st.rerun()

elif st.session_state.page == "SYSTEM":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("⚙️ SYSTEM CONTROL & LOGS")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.accent = st.color_picker("UI ACCENT", st.session_state.accent)
        if st.button("RESET ALARM"): st.session_state.alarm = False; st.rerun()
        if st.button("FORCE DIAGNOSTICS"): add_log("Manual Check: API/DB Online")
    
    with col2:
        st.write("### 📜 LIVE KERNEL LOG")
        for log in reversed(st.session_state.logs):
            st.code(log)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    p = st.text_input("IMAGE PROMPT:")
    if st.button("RENDER"):
        res = safe_replicate_run("FLUX", {"prompt": p})
        if res:
            st.session_state.last_img = res
            st.image(res)
            st.session_state.library.append({"type": "IMG", "url": res, "prompt": p})
            add_log(f"Synth: {p[:15]}")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "AUDIO":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    ap = st.text_input("MUSIC PROMPT:")
    if st.button("COMPOSE"):
        res = safe_replicate_run("MUSIC", {"prompt": ap, "duration": 8})
        if res:
            st.audio(res)
            st.session_state.library.append({"type": "AUDIO", "url": res, "prompt": ap})
            add_log(f"Audio: {ap[:15]}")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "MOVIE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.session_state.last_img:
        st.image(st.session_state.last_img, width=300)
        if st.button("ANIMATE"):
            res = safe_replicate_run("VIDEO", {"input_image": st.session_state.last_img})
            if res: st.video(res); add_log("Movie rendered.")
    else: st.warning("No source image. Use SYNTH first.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 LIBRARY")
    for i, item in enumerate(reversed(st.session_state.library)):
        with st.expander(f"{item['type']} | {item['prompt'][:30]}"):
            if item['type'] == "IMG": 
                st.image(item['url'])
                if st.button("SET WALLPAPER", key=f"w_{i}"): st.session_state.wallpaper = item['url']; st.rerun()
            elif item['type'] == "AUDIO": st.audio(item['url'])
    st.markdown('</div>', unsafe_allow_html=True)


































































