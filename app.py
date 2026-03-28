import streamlit as st
import replicate
import os
import json
import time
import traceback
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v10.3.1", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"

# --- 2. SYSTEMFUNKTIONER (Regel 19, 21 & 22) ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    icon = "⚠️" if is_error else "🤖"
    new_entry = f"[{timestamp}] {icon} {message}"
    # Regel 18: Loop Protector
    if not st.session_state.logs or st.session_state.logs[-1][11:] != new_entry[11:]:
        st.session_state.logs.append(new_entry)
    if is_error: st.session_state.alarm = True
    if len(st.session_state.logs) > 15: st.session_state.logs.pop(0)

def safe_replicate_run(model_alias, input_data, context="GENERAL"):
    # Regel 13: Dynamic Routing
    models = {
        "FLUX": "black-forest-labs/flux-schnell",
        "MUSIC": "facebookresearch/musicgen:7a76a825701904677340e68d71563f69dba84f3353a16134a413d70f0322d7ad",
        "VISION": "lucataco/moondream2",
        "VIDEO": "stability-ai/video-diffusion:3f0bd67d0246b0336ca149257e3df179c3f3f5022137090b8f6c561ec9d77583"
    }
    target = models.get(model_alias, model_alias)
    
    # Regel 9: Neural Progress Bar
    bar = st.progress(0, text=f"Länkar till {model_alias}...")
    try:
        for i in range(1, 6):
            time.sleep(0.1)
            bar.progress(i * 20)
        
        output = replicate.run(target, input=input_data)
        bar.empty()
        return output
    except Exception as e:
        bar.empty()
        # Regel 21: Auto-Fix för 'Invalid v.'
        if "Invalid v" in str(e):
            add_log(f"REPAIR: Stripping hash för {model_alias}", is_error=True)
            return replicate.run(target.split(":")[0], input=input_data)
        
        # Regel 20: Error logging
        with open("system_errors.log", "a") as f:
            f.write(f"{datetime.now()}: {traceback.format_exc()}\n")
        add_log(f"Fel i {context}: {str(e)[:30]}", is_error=True)
        return None

# --- 3. INITIALISERING & UI ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "DESKTOP", "library": [], "logs": ["KERNEL v10.3.1 SECURED"],
        "accent": "#00f2ff", "wallpaper": "https://images.unsplash.com",
        "last_img": None, "alarm": False
    })

accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed;
    }}
    .glass-card {{ 
        background: rgba(0, 5, 15, 0.8); backdrop-filter: blur(25px); 
        border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px; 
    }}
    .stButton>button {{ 
        border: 1px solid {accent}44 !important; background: transparent !important; 
        color: {accent} !important; border-radius: 12px; height: 3rem; transition: 0.3s;
    }}
    .stButton>button:hover {{ background: {accent}22 !important; box-shadow: 0 0 15px {accent}44; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. ROUTING & MODULER ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:15vh; color:{accent}; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    if st.session_state.alarm: st.error("🚨 SYSTEMVARNING: Anomalier detekterade.")
    
    c = st.columns(6)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("🎬 MOVIE", "MOVIE"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        if c[i].button(label): st.session_state.page = target; st.rerun()
    
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write("### 📜 LIVE LOG")
    for log in reversed(st.session_state.logs): st.code(log)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Nav-bar (Regel 3 & 4)
    st.markdown('<div class="glass-card" style="padding: 10px;">', unsafe_allow_html=True)
    nc = st.columns(7)
    nav = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "LIBRARY"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
    for i, (icon, target) in enumerate(nav):
        if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
    st.markdown('</div><div class="glass-card">', unsafe_allow_html=True)

    if st.session_state.page == "SYNTH":
        p = st.text_input("IMAGE PROMPT (FLUX):")
        if st.button("RENDER"):
            res = safe_replicate_run("FLUX", {"prompt": p}, "SYNTH")
            if res:
                url = res[0] if isinstance(res, list) else res
                st.session_state.last_img = url
                st.image(url)
                st.session_state.library.append({"type": "IMG", "url": url, "prompt": p})
                add_log(f"Render klar: {p[:15]}")

    elif st.session_state.page == "AUDIO":
        ap = st.text_input("MUSIC PROMPT (MusicGen):")
        if st.button("COMPOSE"):
            res = safe_replicate_run("MUSIC", {"prompt": ap, "duration": 8}, "AUDIO")
            if res:
                st.audio(res)
                st.session_state.library.append({"type": "AUDIO", "url": res, "prompt": ap})
                add_log(f"Audio klar: {ap[:15]}")

    elif st.session_state.page == "MOVIE":
        if st.session_state.last_img:
            st.image(st.session_state.last_img, width=300)
            if st.button("ANIMATE (SVD)"):
                res = safe_replicate_run("VIDEO", {"input_image": st.session_state.last_img}, "VIDEO")
                if res: st.video(res)
        else: st.warning("Generera en bild i SYNTH först.")

    elif st.session_state.page == "LIBRARY":
        # Regel 16 & 17
        for i, item in enumerate(reversed(st.session_state.library)):
            with st.expander(f"{item['type']} - {item['prompt'][:20]}"):
                if item['type'] == "IMG": st.image(item['url'])
                elif item['type'] == "AUDIO": st.audio(item['url'])
                if st.button("SET WALLPAPER", key=f"wall_{i}"): 
                    st.session_state.wallpaper = item['url']; st.rerun()

    elif st.session_state.page == "ENGINE":
        url = st.text_input("URL:", value=st.session_state.last_img if st.session_state.last_img else "")
        if st.button("ANALYSE"):
            res = safe_replicate_run("VISION", {"image": url, "prompt": "Describe this image."}, "VISION")
            st.info(res)

    elif st.session_state.page == "SYSTEM":
        st.session_state.accent = st.color_picker("ACCENT COLOR", st.session_state.accent)
        if st.button("CLEAR LOGS"): st.session_state.logs = []; st.rerun()
        if st.button("RESET ALARM"): st.session_state.alarm = False; st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

































































