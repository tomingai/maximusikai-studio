import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION & FIL-SYSTEM ---
VERSION = "11.5.0-SHIELD"
DB_FILE = "maximusik_history.json" # Din permanenta databas

st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. PERSISTENCE ENGINE (Regel 8) ---
def save_data():
    """Sparar sessionens data till JSON-fil"""
    data = {
        "library": st.session_state.library,
        "wallpaper": st.session_state.wallpaper,
        "brightness": st.session_state.brightness,
        "accent": st.session_state.accent,
        "last_img": st.session_state.last_img
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    """Laddar data från JSON-fil om den finns"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return None
    return None

# --- 3. MOTORER ---
def deep_clean_prompt(text):
    if not text: return ""
    return str(text).replace('"', '').replace("'", "").replace('\n', ' ').strip()

def sanitize_url(output):
    if isinstance(output, list) and len(output) > 0: return str(output[0])
    return str(output)

# --- 4. INITIALISERING (Laddar sparad data) ---
if "page" not in st.session_state:
    saved = load_data()
    st.session_state.update({
        "page": "SYNTH",
        "library": saved["library"] if saved else [],
        "accent": saved["accent"] if saved else "#00f2ff",
        "last_img": saved["last_img"] if saved else None,
        "wallpaper": saved["wallpaper"] if saved else "https://images.unsplash.com",
        "brightness": saved["brightness"] if saved else 5,
        "style": "Photorealistic"
    })

# --- 5. UI ENGINE (HD Gloss & Contrast) ---
accent = st.session_state.accent
bright_val = (11 - st.session_state.brightness) / 10
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"]::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, {bright_val}); z-index: -1; transition: 0.3s;
    }}
    [data-testid="stAppViewContainer"] {{ background: url("{st.session_state.wallpaper}"); background-size: cover; background-attachment: fixed; }}
    h1, h2, h3, label, p {{ color: #FFFFFF !important; text-shadow: 0px 0px 15px rgba(0,0,0,1), 2px 2px 5px rgba(0,0,0,1) !important; font-weight: 800 !important; }}
    .glass {{ background: rgba(0, 8, 20, 0.9); backdrop-filter: blur(60px); border: 1.5px solid {accent}66; border-radius: 20px; padding: 25px; }}
    .stTextInput>div>div>input, .stSelectbox>div>div {{ background-color: rgba(0, 0, 0, 0.7) !important; color: white !important; border: 1px solid {accent}88 !important; }}
    .stButton>button {{ border: 2px solid {accent}aa !important; background: {accent}22 !important; color: white !important; font-weight: 900 !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 6. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 15px; margin-bottom: 25px;">', unsafe_allow_html=True)
c_nav, c_bright = st.columns([0.7, 0.3])
with c_nav:
    nc = st.columns(7)
    nav_icons = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
    for i, (icon, target, locked) in enumerate(nav_icons):
        if not locked:
            if nc[i].button(icon, key=f"nav_{target}"): st.session_state.page = target; st.rerun()
        else: nc[i].markdown(f'<p style="text-align:center; opacity:0.2; font-size:1.5rem; margin:0;">{icon}</p>', unsafe_allow_html=True)
with c_bright:
    new_bright = st.slider("🔅 LUMINA", 1, 10, st.session_state.brightness)
    if new_bright != st.session_state.brightness:
        st.session_state.brightness = new_bright
        save_data() # Spara ljusstyrka direkt
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 7. SYNTH-MODUL ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 SYNTH STATION</h2>", unsafe_allow_html=True)
    user_p = st.text_input("VISION PROMPT:", placeholder="Beskriv din vision...")
    c1, c2 = st.columns([0.7, 0.3])
    style = c1.selectbox("STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Digital Art"])
    aspect = c2.selectbox("FORMAT:", ["1:1", "16:9", "9:16"])

    if st.button("🚀 EXEKVERA NEURAL KEDJA"):
        if user_p:
            with st.status("Genererar...") as status:
                raw_llm = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": f"Expand to 8k {style} prompt: {user_p}"})
                clean_p = deep_clean_prompt("".join(list(raw_llm)))
                flux_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": clean_p, "aspect_ratio": aspect.replace(":", "x")})
                url = sanitize_url(flux_res)
                if url:
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                    save_data() # Spara allt efter ny bild
                    st.rerun()
    
    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, use_column_width=True)
        if st.button("🖼 SÄTT SOM BAKGRUND"): 
            st.session_state.wallpaper = st.session_state.last_img
            save_data() # Spara bakgrundsval
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 8. ARKIV-MODUL ---
elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 SYSTEM ARCHIVE")
    if not st.session_state.library: st.info("Arkivet är tomt.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.image(item['url'], use_column_width=True)
                if st.button("VÄLJ", key=f"ark_{i}"):
                    st.session_state.last_img = item['url']
                    st.session_state.wallpaper = item['url']
                    save_data()
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)




















































































































































