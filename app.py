import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v10.4.8", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"

# --- 2. SYSTEMFUNKTIONER (Regel 8, 19, 21) ---
def add_log(message, is_error=False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state: st.session_state.logs = []
    icon = "⚠️" if is_error else "🤖"
    new_entry = f"[{timestamp}] {icon} {message}"
    
    # Regel 18: Loop Protector
    if not st.session_state.logs or st.session_state.logs[-1][11:] != new_entry[11:]:
        st.session_state.logs.append(new_entry)
        # Regel 8: Auto-save loggen vid varje ny post
        save_system_state()
        
    if is_error: st.session_state.alarm = True
    if len(st.session_state.logs) > 35: st.session_state.logs.pop(0)

def save_system_state():
    """Regel 8: Bakgrunds-save av Bibliotek och Loggar."""
    state_data = {
        "library": st.session_state.get("library", []),
        "logs": st.session_state.get("logs", []),
        "accent": st.session_state.get("accent", "#00f2ff"),
        "wallpaper": st.session_state.get("wallpaper", "")
    }
    try:
        with open(DB_FILE, "w") as f:
            json.dump(state_data, f)
    except: pass

def load_system_state():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return None
    return None

def run_self_test():
    add_log("RUNNING SYSTEM SELF-TEST...")
    api_ok = os.environ.get("REPLICATE_API_TOKEN") is not None
    add_log(f"DIAGNOSTICS: API={'ONLINE' if api_ok else 'OFFLINE'}")
    return api_ok

def safe_replicate_run(model_alias, input_data):
    models = {
        "FLUX": "black-forest-labs/flux-schnell",
        "MUSIC": "facebookresearch/musicgen:7a76a825701904677340e68d71563f69dba84f3353a16134a413d70f0322d7ad",
        "VIDEO": "stability-ai/video-diffusion:3f0bd67d0246b0336ca149257e3df179c3f3f5022137090b8f6c561ec9d77583"
    }
    target = models.get(model_alias, model_alias)
    bar = st.progress(0, text=f"Neural Link: {model_alias}")
    try:
        output = replicate.run(target, input=input_data)
        bar.empty()
        save_system_state()
        return output
    except Exception as e:
        bar.empty()
        if "Invalid v" in str(e):
            add_log(f"AUTO-FIX: Version stripped for {model_alias}", is_error=True)
            return replicate.run(target.split(":"), input=input_data)
        add_log(f"ERROR: {str(e)[:40]}", is_error=True)
        return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    saved = load_system_state()
    if saved:
        st.session_state.update({
            "page": "DESKTOP", "library": saved.get("library", []), 
            "logs": saved.get("logs", []), "accent": saved.get("accent", "#00f2ff"),
            "wallpaper": saved.get("wallpaper", "https://images.unsplash.com"),
            "last_img": None, "alarm": False, "diagnostics_run": False
        })
    else:
        st.session_state.update({
            "page": "DESKTOP", "library": [], "logs": ["OS KERNEL v10.4.8 BOOT"],
            "accent": "#00f2ff", "wallpaper": "https://images.unsplash.com",
            "last_img": None, "alarm": False, "diagnostics_run": False
        })

# --- 4. UI ENGINE ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ 
        background: linear-gradient(rgba(0,0,0,0.88), rgba(0,0,0,0.96)), url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed;
    }}
    .glass {{ background: rgba(0, 5, 15, 0.88); backdrop-filter: blur(40px); border: 1px solid {accent}22; border-radius: 20px; padding: 30px; }}
    .stButton>button {{ border: 1px solid {accent}55 !important; color: {accent} !important; background: transparent !important; border-radius: 12px; height: 3.5rem; }}
    .stButton>button:hover {{ background: {accent}15 !important; box-shadow: 0 0 20px {accent}44; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px; margin-bottom: 25px; border-radius: 18px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "ARKIV"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
for i, (icon, target) in enumerate(nav):
    if nc[i].button(icon, key=f"nav_{target}"): 
        st.session_state.page = target
        if target == "SYSTEM": st.session_state.diagnostics_run = False 
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:35px; padding-top:20vh; color:{accent}; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    if st.session_state.alarm: st.error("🚨 SYSTEM ALARM ACTIVE")
    st.text_input("CMD >", placeholder="Ready for commands...")

elif st.session_state.page == "SYSTEM":
    if not st.session_state.diagnostics_run:
        run_self_test()
        st.session_state.diagnostics_run = True
    
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("⚙️ SYSTEM CONTROL")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.accent = st.color_picker("UI ACCENT", st.session_state.accent)
        if st.button("RESET ALARM"): st.session_state.alarm = False; st.rerun()
        
        log_data = "\n".join(st.session_state.logs)
        st.download_button("📥 DOWNLOAD KERNEL LOG", data=log_data, file_name="maximusik_kernel.txt", mime="text/plain")
        if st.button("CLEAR LOG HISTORY"): st.session_state.logs = []; save_system_state(); st.rerun()
    
    with c2:
        st.write("### 📜 KERNEL LOG")
        for log in reversed(st.session_state.logs): st.code(log)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    p = st.text_input("IMAGE PROMPT:")
    if st.button("RENDER IMAGE"):
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
    if st.button("COMPOSE AUDIO"):
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
        if st.button("RENDER MOTION"):
            res = safe_replicate_run("VIDEO", {"input_image": st.session_state.last_img})
            if res: st.video(res); add_log("Movie Processed")
    else: st.warning("Need SYNTH image first.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 MEDIA ARCHIVE")
    for i, item in enumerate(reversed(st.session_state.library)):
        with st.expander(f"{item['type']} | {item['prompt'][:30]}"):
            if item['type'] == "IMG": 
                st.image(item['url'])
                if st.button("INJECT WALLPAPER", key=f"wall_{i}"): st.session_state.wallpaper = item['url']; st.rerun()
            elif item['type'] == "AUDIO": st.audio(item['url'])
    st.markdown('</div>', unsafe_allow_html=True)



































































