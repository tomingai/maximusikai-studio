import streamlit as st
import replicate
import os
import json
import time
import traceback
from datetime import datetime

# --- 1. SYSTEM-KONFIGURATION (v10.1.9 FULL RESTORE) ---
st.set_page_config(page_title="MAXIMUSIK AI OS v10.1.9", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"

# --- 2. KÄRNLOGIK & AUTO-FIX ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    icon = "⚠️" if is_error else "🤖"
    new_entry = f"[{timestamp}] {icon} {message}"
    if not st.session_state.logs or st.session_state.logs[-1][11:] != new_entry[11:]:
        st.session_state.logs.append(new_entry)
    if len(st.session_state.logs) > 15: st.session_state.logs.pop(0)

def safe_replicate_run(model_alias, input_data, context="GENERAL"):
    models = {
        "FLUX": "black-forest-labs/flux-schnell",
        "MUSIC": "facebookresearch/musicgen:7a76a825701904677340e68d71563f69dba84f3353a16134a413d70f0322d7ad",
        "VISION": "lucataco/moondream2",
        "VIDEO": "stability-ai/video-diffusion:3f0bd67d0246b0336ca149257e3df179c3f3f5022137090b8f6c561ec9d77583"
    }
    target = models.get(model_alias, model_alias)
    bar = st.progress(0, text=f"Neural länk: {model_alias}...")
    try:
        for i in range(1, 5):
            time.sleep(0.1)
            bar.progress(i * 20, text=f"Processar {context}...")
        
        # Auto-Fix: Strippa version om den orsakat "Invalid v." tidigare
        output = replicate.run(target, input=input_data)
        bar.progress(100)
        time.sleep(0.2)
        bar.empty()
        return output
    except Exception as e:
        bar.empty()
        if "Invalid v" in str(e):
            add_log(f"REPAIR: Stripping version for {model_alias}", is_error=True)
            return replicate.run(target.split(":")[0], input=input_data)
        add_log(f"Krasch i {context}: {str(e)[:30]}", is_error=True)
        return None

def save_history():
    try:
        with open(DB_FILE, "w") as f:
            json.dump(st.session_state.library, f)
    except: pass

# --- 3. INITIALISERING & UI ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "DESKTOP",
        "library": [],
        "logs": ["KERNEL v10.1.9 RESTORED"],
        "accent": "#00f2ff",
        "wallpaper": "https://images.unsplash.com",
        "last_img": None
    })

accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.9)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 5, 15, 0.85); backdrop-filter: blur(25px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; margin-bottom: 20px; }}
    .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {accent}22; }}
    .stButton>button {{ border: 1px solid {accent}44 !important; background: transparent !important; color: {accent} !important; border-radius: 10px; transition: 0.3s; }}
    .stButton>button:hover {{ background: {accent}22 !important; box-shadow: 0 0 15px {accent}33; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:15vh; color:{accent}; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    c = st.columns(6)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("🎬 MOVIE", "MOVIE"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        if c[i].button(label): st.session_state.page = target; st.rerun()
    
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.write("### 📜 SYSTEM LOG")
    for log in reversed(st.session_state.logs): st.code(log)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
    nc = st.columns(7)
    nav = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "LIBRARY"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
    for i, (icon, target) in enumerate(nav):
        if nc[i].button(icon): st.session_state.page = target; st.rerun()
    st.markdown('</div><div class="glass">', unsafe_allow_html=True)

    # MODULER
    if st.session_state.page == "SYNTH":
        st.subheader("🪄 NEURAL SYNTH")
        p = st.text_input("IMAGE PROMPT:")
        if st.button("GENERATE"):
            res = safe_replicate_run("FLUX", {"prompt": p}, "IMAGE")
            if res:
                st.session_state.last_img = res
                st.image(res)
                st.session_state.library.append({"type": "IMG", "url": res, "prompt": p})
                save_history()

    elif st.session_state.page == "AUDIO":
        st.subheader("🎧 AUDIO ENGINE")
        ap = st.text_input("MUSIC PROMPT:")
        if st.button("COMPOSE"):
            res = safe_replicate_run("MUSIC", {"prompt": ap, "duration": 8}, "AUDIO")
            if res:
                st.audio(res)
                st.session_state.library.append({"type": "AUDIO", "url": res, "prompt": ap})
                save_history()

    elif st.session_state.page == "MOVIE":
        st.subheader("🎬 MOVIE RENDERER")
        if st.session_state.last_img:
            st.image(st.session_state.last_img, width=300)
            if st.button("ANIMATE"):
                res = safe_replicate_run("VIDEO", {"input_image": st.session_state.last_img}, "VIDEO")
                if res: st.video(res)
        else: st.warning("Generera en bild i SYNTH först.")

    elif st.session_state.page == "LIBRARY":
        st.subheader("📚 ARKIV")
        for item in reversed(st.session_state.library):
            with st.expander(f"{item['type']} - {item['prompt'][:20]}..."):
                if item['type'] == "IMG": st.image(item['url'])
                elif item['type'] == "AUDIO": st.audio(item['url'])
                if st.button("SET WALLPAPER", key=item['url']):
                    st.session_state.wallpaper = item['url']; st.rerun()

    elif st.session_state.page == "ENGINE":
        st.subheader("🖼 VISION ENGINE")
        url = st.text_input("URL ATT ANALYSERA:", value=st.session_state.last_img if st.session_state.last_img else "")
        if url and st.button("ANALYSE"):
            res = safe_replicate_run("VISION", {"image": url, "prompt": "Describe this image."}, "VISION")
            st.info(res)

    elif st.session_state.page == "SYSTEM":
        st.subheader("⚙️ SYSTEM CONTROL")
        st.session_state.accent = st.color_picker("ACCENT", st.session_state.accent)
        if st.button("CLEAR LOGS"): st.session_state.logs = []; st.rerun()
        if st.button("REPAIR DB"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.library = []; st.success("Database Purged")

    st.markdown('</div>', unsafe_allow_html=True)































































