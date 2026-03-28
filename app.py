import streamlit as st
import replicate
import os
import json
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.1.0"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. URL-SANITIZER & MOTOR (Regel 21 & 12) ---
def sanitize_url(output):
    if isinstance(output, list) and len(output) > 0: return str(output[0])
    return str(output)

def safe_replicate_run(model, input_data):
    try:
        res = replicate.run(model, input=input_data)
        return sanitize_url(res) if model != "lucataco/moondream2" else res
    except: return None

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "accent": "#00f2ff", "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Macro Photography", "hd_mode": True, "analysis": ""
    })

# --- 4. UI ENGINE ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.9), rgba(0,0,0,0.95)), url("{st.session_state.wallpaper}"); background-size: cover; }}
    .glass {{ background: rgba(0, 5, 20, 0.9); backdrop-filter: blur(50px); border: 1px solid {accent}44; border-radius: 25px; padding: 25px; margin-bottom: 20px; }}
    .stButton>button {{ border: 1px solid {accent}66 !important; color: white !important; background: {accent}22 !important; border-radius: 12px; height: 3.5rem; transition: 0.3s; width: 100%; }}
    .stButton>button:hover {{ background: {accent}44 !important; box-shadow: 0 0 20px {accent}77; }}
    .locked-btn button {{ opacity: 0.1 !important; cursor: not-allowed !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION (ENGINE UNLOCKED) ---
st.markdown('<div class="glass" style="padding: 10px;">', unsafe_allow_html=True)
nav_cols = st.columns(7)
nav_config = [
    ("🏠", "HOME", True), ("🪄", "SYNTH", False), ("🎧", "AUDIO", True), 
    ("🎬", "MOVIE", True), ("📚", "ARKIV", False), ("🖼", "ENGINE", False), ("⚙️", "SYSTEM", True)
]
for i, (icon, target, is_locked) in enumerate(nav_config):
    if is_locked:
        nav_cols[i].markdown('<div class="locked-btn">', unsafe_allow_html=True)
        nav_cols[i].button(icon, key=f"l_{i}")
        nav_cols[i].markdown('</div>', unsafe_allow_html=True)
    else:
        if nav_cols[i].button(icon, key=f"a_{target}"):
            st.session_state.page = target; st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 ULTRA-HD SYNTH STATION</h2>", unsafe_allow_html=True)
    user_p = st.text_input("VISION:", placeholder="Beskriv din HD-vision...")
    if st.button("🚀 EXEKVERA NEURAL HD-SYNTES"):
        with st.status("Genererar...") as s:
            final_p = user_p
            if st.session_state.hd_mode:
                res_ll = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": f"8k macro photo prompt: {user_p}"})
                final_p = "".join(list(res_ll))
            url = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": final_p, "aspect_ratio": "16x9"})
            if url:
                st.session_state.last_img = url
                st.session_state.library.append({"url": url, "prompt": user_p})
                st.rerun()
    if st.session_state.last_img:
        st.image(st.session_state.last_img)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ENGINE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🖼️ VISION ENGINE [ANALYS]</h2>", unsafe_allow_html=True)
    if st.session_state.last_img:
        st.image(st.session_state.last_img, width=400)
        if st.button("🔍 KÖR NEURAL INSPEKTION"):
            with st.spinner("Analyserar pixlar..."):
                res = safe_replicate_run("lucataco/moondream2", {
                    "image": st.session_state.last_img, 
                    "prompt": "Describe the lighting, textures, and details in this image. Is it high quality?"
                })
                st.session_state.analysis = res
        if st.session_state.analysis:
            st.info(st.session_state.analysis)
    else: st.warning("Skapa en bild i SYNTH först.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 ARKIV")
    cols = st.columns(3)
    for i, item in enumerate(reversed(st.session_state.library)):
        with cols[i % 3]:
            st.image(item['url'])
            if st.button("SET WALLPAPER", key=f"w_{i}"):
                st.session_state.wallpaper = item['url']; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)





































































