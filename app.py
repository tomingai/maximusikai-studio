import streamlit as st
import replicate
import os
import random
import requests
from io import BytesIO

# --- 1. SYSTEM-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v7.4 ENGINE", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# LÅSTA SYSTEM-STATES
states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "brightness": 0.5,
    "library": [],
    "last_synth_p": "",
    "last_audio_res": None,
    "last_image_res": None,
    "lib_filter": "ALLA"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 2. HJÄLPFUNKTIONER ---
def get_url(res):
    try:
        if isinstance(res, list) and len(res) > 0: return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except: return str(res)

def sonify_image(image_url):
    with st.spinner("AI tolkar visuella data..."):
        try:
            analysis = replicate.run(
                "lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                input={"image": image_url, "prompt": "Describe the musical style and mood of this image in 8 words."}
            )
            st.info(f"AUDIO-DNA: {analysis}")
            music_res = replicate.run("meta/musicgen", input={"prompt": f"Genre: {analysis}", "duration": 8})
            st.session_state.library.append({"type": "audio", "url": music_res, "prompt": f"Vision: {analysis[:15]}"})
            return music_res
        except Exception as e:
            st.error(f"Sonify Error: {e}"); return None

# --- 3. UI ENGINE ---
def apply_ui():
    accent = st.session_state.accent_color
    bright = st.session_state.brightness
    overlay = 1.0 - bright 
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,{overlay}), rgba(0,0,0,{overlay + 0.1})), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; background-attachment: fixed !important;
            background-position: center !important;
        }}
        [data-testid="stHeader"], .main {{ background: transparent !important; }}
        h1, h2, h3, p, label, .stCaption {{ color: {accent} !important; text-shadow: 0 0 12px {accent}88 !important; font-family: 'Courier New', monospace !important; }}
        .window-box {{ background: rgba(0, 5, 15, 0.93); backdrop-filter: blur(30px); border: 1px solid {accent}33; border-radius: 30px; padding: 40px; margin-top: 20px; }}
        .stButton > button {{ background: rgba(0,0,0,0.6) !important; border: 1px solid {accent}44 !important; color: {accent} !important; border-radius: 12px !important; transition: 0.3s; }}
        .stButton > button:hover {{ border-color: {accent} !important; box-shadow: 0 0 20px {accent}44; }}
        audio {{ filter: sepia(1) saturate(5) hue-rotate(160deg); width: 100%; border-radius: 15px; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:15vh; font-size:4.5rem; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:{st.session_state.accent_color}; opacity:0.6;'>OS v7.4 // ENGINE MODULE ACTIVE</p>", unsafe_allow_html=True)
    cols = st.columns(5)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        with cols[i]:
            if st.button(label, use_container_width=True):
                st.session_state.page = target; st.rerun()

# --- 5. WINDOWS ---
else:
    _, win_col, _ = st.columns([0.05, 0.9, 0.05])
    with win_col:
        st.markdown('<div class="window-box">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2>// {st.session_state.page}</h2>", unsafe_allow_html=True)
        if h2.button("✕"): st.session_state.page = "DESKTOP"; st.rerun()

        # --- SYNTH ---
        if st.session_state.page == "SYNTH":
            p = st.text_area("PROMPT (VISUAL):", value=st.session_state.last_synth_p)
            if st.button("GENERATE VISION", use_container_width=True):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                st.session_state.last_image_res = get_url(res)
                st.session_state.library.append({"type": "image", "url": st.session_state.last_image_res, "prompt": p}); st.rerun()
            if st.session_state.last_image_res:
                st.image(st.session_state.last_image_res, width=400)
                if st.button("🎵 SKAPA MUSIK AV BILDEN"):
                    st.session_state.last_audio_res = sonify_image(st.session_state.last_image_res); st.rerun()

        # --- AUDIO ---
        elif st.session_state.page == "AUDIO":
            ap = st.text_input("PROMPT (SONIC):")
            if st.button("GENERATE AUDIO", use_container_width=True):
                res = replicate.run("meta/musicgen", input={"prompt": ap, "duration": 8})
                st.session_state.last_audio_res = res
                st.session_state.library.append({"type": "audio", "url": res, "prompt": ap}); st.rerun()
            if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

        # --- LIBRARY (ARKIVET) ---
        elif st.session_state.page == "LIBRARY":
            st.session_state.lib_filter = st.radio("FILTER:", ["BILDER", "LJUD"], horizontal=True)
            f_lib = [i for i in st.session_state.library if (st.session_state.lib_filter == "BILDER" and i['type'] == "image") or (st.session_state.lib_filter == "LJUD" and i['type'] == "audio")]
            if not f_lib: st.write("ARKIVET ÄR TOMT")
            else:
                l_cols = st.columns(3)
                for idx, item in enumerate(reversed(f_lib)):
                    with l_cols[idx % 3]:
                        if item['type'] == "image": 
                            st.image(item['url'])
                            c1, c2, c3 = st.columns(3)
                            if c1.button("🗑", key=f"d_{idx}"): st.session_state.library.remove(item); st.rerun()
                            if c2.button("🖼", key=f"b_{idx}"): st.session_state.wallpaper = item['url']; st.rerun()
                            if c3.button("🎵", key=f"s_{idx}"): st.session_state.last_audio_res = sonify_image(item['url']); st.rerun()
                        else: 
                            st.audio(item['url'])
                            if st.button("🗑", key=f"da_{idx}"): st.session_state.library.remove(item); st.rerun()
                        st.markdown("---")

        # --- ENGINE (BAKGRUNDSSKAPAREN) ---
        elif st.session_state.page == "ENGINE":
            st.write("### ENVIRONMENT RE-DRAFT")
            st.session_state.brightness = st.slider("AMBIENT BRIGHTNESS", 0.0, 1.0, st.session_state.brightness)
            ep = st.text_area("ENVIRONMENT PROMPT (16:9 Optimerad):", placeholder="Cyberpunk skyline, neon rain, hyper-realistic...")
            if st.button("UPDATE REALITY", use_container_width=True):
                with st.spinner("Rendering Environment..."):
                    res = replicate.run("black-forest-labs/flux-schnell", 
                                       input={"prompt": ep, "aspect_ratio": "16:9"})
                    url = get_url(res)
                    st.session_state.wallpaper = url
                    st.session_state.library.append({"type": "image", "url": url, "prompt": f"Engine: {ep[:15]}"})
                    st.rerun()
            st.info("Tips: Du kan också gå till ARKIVET och trycka på 🖼 på valfri bild för att sätta den som bakgrund.")

        # --- SYSTEM ---
        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("ACCENT COLOR", st.session_state.accent_color)
            if st.button("FACTORY RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)







































