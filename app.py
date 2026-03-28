import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION & DATA-SHIELD ---
VERSION = "11.3.6-ULTIMATE"
DB_FILE = "maximusik_history.json"

st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. PERSISTENCE ENGINE ---
def save_data():
    try:
        data = {
            "library": st.session_state.get("library", []),
            "wallpaper": st.session_state.get("wallpaper", ""),
            "brightness": st.session_state.get("brightness", 5),
            "last_img": st.session_state.get("last_img", None)
        }
        with open(DB_FILE, "w") as f: json.dump(data, f)
    except: pass

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return None
    return None

# --- 3. MOTOR & URL-SANITIZER ---
def clean_prompt(text):
    if not text: return ""
    return str(text).replace('"', '').replace('Prompt:', '').strip()

def sanitize_url(output):
    """Fixar list-kraschen genom att extrahera första strängen"""
    if isinstance(output, list) and len(output) > 0:
        return str(output[0])
    return str(output)

def safe_replicate_run(model, input_data):
    try:
        res = replicate.run(model, input=input_data)
        if "moondream" in model or "llama" in model: return res
        return sanitize_url(res)
    except Exception as e:
        st.error(f"Neural Error: {str(e)[:100]}")
        return None

# --- 4. INITIALISERING ---
if "page" not in st.session_state:
    saved = load_data()
    st.session_state.update({
        "page": "SYNTH",
        "library": saved["library"] if saved else [],
        "accent": "#00f2ff",
        "last_img": saved["last_img"] if saved else None,
        "wallpaper": saved["wallpaper"] if saved else "https://images.unsplash.com",
        "brightness": saved["brightness"] if saved else 5,
        "style": "Photorealistic"
    })

# --- 5. UI ENGINE (GLOW & LUMINA) ---
accent = st.session_state.accent
bright_val = (11 - st.session_state.brightness) / 10

st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"]::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, {bright_val}); z-index: -1; transition: 0.3s;
    }}
    [data-testid="stAppViewContainer"] {{ 
        background: url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed;
    }}
    .glass {{ 
        background: rgba(0, 10, 30, 0.85); backdrop-filter: blur(50px); 
        border: 1px solid {accent}66; border-radius: 20px; padding: 25px; 
    }}
    h1, h2, h3, label, p {{ color: white !important; text-shadow: 2px 2px 12px rgba(0,0,0,1) !important; font-weight: 800 !important; }}
    .stTextInput>div>div>input, .stSelectbox>div>div {{ background-color: rgba(0, 0, 0, 0.6) !important; color: white !important; border: 1px solid {accent}44 !important; }}
    .stButton>button {{ border: 1px solid {accent}88 !important; color: white !important; background: {accent}22 !important; border-radius: 12px; height: 3.5rem; font-weight: bold; width: 100%; }}
    .neural-console {{ background: rgba(0,0,0,0.8); border: 1px solid {accent}44; padding: 12px; border-radius: 8px; font-family: monospace; color: {accent}; font-size: 0.8rem; }}
    </style>
""", unsafe_allow_html=True)

# --- 6. NAVIGATION & LUMINA ---
st.markdown('<div class="glass" style="padding: 15px; margin-bottom: 20px;">', unsafe_allow_html=True)
c_nav, c_bright = st.columns([0.7, 0.3])
with c_nav:
    nc = st.columns(7)
    nav_icons = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
    for i, (icon, target, locked) in enumerate(nav_icons):
        if not locked:
            if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
        else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)
with c_bright:
    new_bright = st.slider("🔅 LUMINA", 1, 10, st.session_state.brightness)
    if new_bright != st.session_state.brightness:
        st.session_state.brightness = new_bright
        save_data(); st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 SYNTH STATION</h2>", unsafe_allow_html=True)
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Banan-lejon...")
    c1, c2 = st.columns([0.7, 0.3])
    with c1:
        st.session_state.style = st.selectbox("STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Digital Art"])
    with c2:
        aspect = st.selectbox("FORMAT:", ["1x1", "16x9", "9x16"], index=1)

    if st.button("🚀 STARTA NEURAL KEDJA"):
        if user_p:
            prog = st.progress(0)
            console = st.empty()
            log = ["› INITIALIZING NEURAL ENGINE..."]
            prog.progress(20, text="EXPANDING VISION...")
            raw_expanded = "".join(list(replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": f"Expand to a {st.session_state.style} 8k image prompt: {user_p}"})))
            expanded = clean_prompt(raw_expanded)
            log.append("› PROMPT OPTIMIZED.")
            console.markdown(f'<div class="neural-console">{"<br>".join(log)}</div>', unsafe_allow_html=True)
            prog.progress(50, text="RENDERING PIXELS...")
            # FIXED: aspect_ratio använder nu korrekt x-format
            url = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": expanded, "aspect_ratio": aspect})
            if url:
                st.session_state.last_img = url
                st.session_state.library.append({"url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                save_data()
                st.rerun()
    if st.session_state.last_img:
        st.divider(); st.image(st.session_state.last_img, use_column_width=True)
        if st.button("🖼 SÄTT SOM BAKGRUND"): st.session_state.wallpaper = st.session_state.last_img; save_data(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if not st.session_state.library: st.info("Arkivet är tomt.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.image(item['url'], use_column_width=True)
                if st.button("VÄLJ", key=f"ark_{i}"):
                    st.session_state.last_img = item['url']; st.session_state.wallpaper = item['url']; save_data(); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)























































































































































