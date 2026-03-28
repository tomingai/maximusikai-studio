import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION (KERNEL FREEZE v11.3.7) ---
VERSION = "11.3.7-GOLDEN"
st.set_page_config(page_title=f"MAXIMUSIK AI OS {VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. FRYSTA FUNKTIONER ---
def clean_prompt(text):
    return str(text).replace('"', '').replace('Prompt:', '').strip() if text else ""

def sanitize_url(output):
    return str(output) if not isinstance(output, list) else str(output[0])

def safe_replicate_run(model, input_data):
    try:
        res = replicate.run(model, input=input_data)
        return res if "moondream" in model or "llama" in model else sanitize_url(res)
    except: return None

# --- 3. STATE LOCKDOWN ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "accent": "#00f2ff", "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Photorealistic", "analysis": ""
    })

# --- 4. UI ENGINE ---
accent = st.session_state.accent
st.markdown(f"""
    <style>
    @keyframes pulse-green {{ 0% {{ border-color: {accent}44; }} 50% {{ border-color: #00ff88; }} 100% {{ border-color: {accent}44; }} }}
    [data-testid="stAppViewContainer"] {{ background: linear-gradient(rgba(0,0,0,0.95), rgba(0,0,0,0.98)), url("{st.session_state.wallpaper}"); background-size: cover; background-attachment: fixed; }}
    .glass {{ background: rgba(0, 5, 20, 0.92); backdrop-filter: blur(50px); border: 1px solid {accent}33; border-radius: 20px; padding: 25px; }}
    .success-box {{ border: 2px solid #00ff88; animation: pulse-green 2s infinite; border-radius: 12px; padding: 15px; text-align: center; color: #00ff88; font-family: monospace; font-weight: bold; }}
    .stButton>button {{ border: 1px solid {accent}55 !important; color: white !important; background: {accent}11 !important; border-radius: 12px; height: 3.5rem; font-weight: bold; width: 100%; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION ---
st.markdown('<div class="glass" style="padding: 10px; margin-bottom: 20px;">', unsafe_allow_html=True)
nc = st.columns(7)
nav = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
for i, (icon, target, is_locked) in enumerate(nav):
    if not is_locked:
        if nc[i].button(icon, key=f"nav_{target}"):
            st.session_state.page = target; st.rerun()
    else: nc[i].markdown(f'<p style="text-align:center; opacity:0.1; font-size:1.5rem; margin:0; padding-top:10px;">{icon}</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🪄 SYNTH STATION</h2>", unsafe_allow_html=True)
    user_p = st.text_input("VISION PROMPT:", placeholder="Banan-lejon...")
    c1, c2 = st.columns([0.7, 0.3])
    st.session_state.style = c1.selectbox("STIL:", ["Photorealistic", "Cinematic", "Cyberpunk"], index=0)
    aspect = c2.selectbox("FORMAT:", ["1:1", "16:9", "9:16"], index=1)

    if st.button("🚀 EXEKVERA"):
        if user_p:
            prog = st.progress(0)
            with st.status("Neural Pipeline...") as status:
                expanded = "".join(list(replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": f"Expand to 8k {st.session_state.style} prompt: {user_p}"})))
                url = safe_replicate_run("black-forest-labs/flux-schnell", {"prompt": clean_prompt(expanded), "aspect_ratio": aspect.replace(":", "x")})
                if url:
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                    st.markdown('<div class="success-box">✅ READY</div>', unsafe_allow_html=True)
                    time.sleep(1); st.rerun()
    if st.session_state.last_img:
        st.image(st.session_state.last_img, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ENGINE":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent};'>🖼️ VISION ENGINE</h2>", unsafe_allow_html=True)
    
    # Auto-Load från Arkiv om sessionen är tom
    if not st.session_state.last_img and st.session_state.library:
        st.session_state.last_img = st.session_state.library[-1]['url']
        
    if st.session_state.last_img:
        st.image(st.session_state.last_img, width=400)
        if st.button("🔍 ANALYSERA BILD"):
            res = safe_replicate_run("lucataco/moondream2", {"image": st.session_state.last_img, "prompt": "Describe textures and quality."})
            st.session_state.analysis = res
        if st.session_state.analysis: st.info(st.session_state.analysis)
    else: st.info("Skapa en bild först för att aktivera analysen.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 ARKIV")
    if not st.session_state.library: st.info("Tomt.")
    else:
        grid = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.library)):
            with grid[i % 3]:
                st.image(item['url'], use_column_width=True)
                if st.button("VÄLJ", key=f"ark_{i}"):
                    st.session_state.last_img = item['url']
                    st.session_state.wallpaper = item['url']; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)










































































