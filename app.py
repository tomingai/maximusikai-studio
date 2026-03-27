import streamlit as st
import replicate
import os
import random
import requests
from io import BytesIO

# --- 1. SYSTEM-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v6.7 VISION", layout="wide", initial_sidebar_state="collapsed")

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

def get_random_prompt(mode="IMAGE"):
    img_prompts = ["Cyberpunk city neon rain", "Deep space nebula", "Ancient forest bioluminescent", "Retro robot DJ"]
    audio_prompts = ["Dark techno 128bpm heavy bass", "Space ambient ethereal pads", "Cyberpunk industrial beat", "Lofi hip hop chill"]
    return random.choice(audio_prompts if mode == "AUDIO" else img_prompts)

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
        h1, h2, h3, p, label, .stCaption {{ color: {accent} !important; text-shadow: 0 0 10px {accent}77 !important; font-family: 'Courier New', monospace !important; }}
        .window-box {{ 
            background: rgba(0, 5, 12, 0.92); 
            backdrop-filter: blur(25px); 
            border: 1px solid {accent}44; 
            border-radius: 30px; 
            padding: 35px;
            margin-top: 20px;
        }}
        .stButton > button {{ 
            background: rgba(0,0,0,0.6) !important; 
            border: 1px solid {accent}44 !important; 
            color: {accent} !important; 
            border-radius: 12px !important; 
            transition: all 0.3s ease;
        }}
        .stButton > button:hover {{ border-color: {accent} !important; box-shadow: 0 0 20px {accent}55; }}
        audio {{ filter: sepia(1) saturate(5) hue-rotate(160deg); width: 100%; border-radius: 12px; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:20px; padding-top:15vh; font-size:4.5rem; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:{st.session_state.accent_color}; opacity:0.7;'>SYSTEM OS v6.7 // VISION UPDATE</p>", unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    cols = st.columns(6)
    apps = [
        ("🪄 SYNTH", "SYNTH"), 
        ("🎧 AUDIO", "AUDIO"), 
        ("📸 VISION", "VISION"), 
        ("📚 ARKIV", "LIBRARY"), 
        ("🖼 ENGINE", "ENGINE"), 
        ("⚙️ SYSTEM", "SYSTEM")
    ]
    for i, (label, target) in enumerate(apps):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"btn_{target}"):
                st.session_state.page = target; st.rerun()

# --- 5. WINDOWS ---
else:
    _, win_col, _ = st.columns([0.05, 0.9, 0.05])
    with win_col:
        st.markdown('<div class="window-box">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2>// {st.session_state.page}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="exit_os"): st.session_state.page = "DESKTOP"; st.rerun()

        # --- VISION (IMAGE TO MUSIC) ---
        if st.session_state.page == "VISION":
            st.write("### ANALYSE IMAGE & GENERATE SOUNDTRACK")
            up = st.file_uploader("UPLOAD SOURCE:", type=["jpg", "png", "jpeg"])
            if up:
                st.image(up, width=300)
                if st.button("EXECUTE VISION-TO-AUDIO", use_container_width=True):
                    with st.spinner("Analyzing Visual DNA..."):
                        try:
                            # Steg 1: Bildanalys
                            descr = replicate.run("lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                                                 input={"image": up, "prompt": "Describe the mood and musical style of this image."})
                            st.info(f"ANALYSIS: {descr}")
                            # Steg 2: Musikgen
                            res = replicate.run("meta/musicgen:7a76a8258502edb298485a3666d92021614f94bb2ed02901399677334466d3a8", 
                                               input={"prompt": f"Music inspired by: {descr}", "duration": 8})
                            st.session_state.last_audio_res = res
                            st.session_state.library.append({"type": "audio", "url": res, "prompt": f"Vision: {descr[:20]}"})
                            st.rerun()
                        except Exception as e: st.error(e)
            if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

        # --- AUDIO ---
        elif st.session_state.page == "AUDIO":
            if st.button("🎲 RANDOM"): st.session_state.last_synth_p = get_random_prompt("AUDIO"); st.rerun()
            ap = st.text_input("PROMPT:", value=st.session_state.last_synth_p)
            if st.button("GENERATE", use_container_width=True):
                with st.spinner("Processing..."):
                    res = replicate.run("meta/musicgen", input={"prompt": ap, "duration": 8})
                    st.session_state.last_audio_res = res
                    st.session_state.library.append({"type": "audio", "url": res, "prompt": ap})
                st.rerun()
            if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

        # --- SYNTH ---
        elif st.session_state.page == "SYNTH":
            if st.button("🎲 RANDOM"): st.session_state.last_synth_p = get_random_prompt("IMAGE"); st.rerun()
            p = st.text_area("PROMPT:", value=st.session_state.last_synth_p)
            if st.button("SYNTHESIZE", use_container_width=True):
                with st.spinner("Visualizing..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    url = get_url(res)
                    st.session_state.last_image_res = url
                    st.session_state.library.append({"type": "image", "url": url, "prompt": p})
                st.rerun()
            if st.session_state.last_image_res: st.image(st.session_state.last_image_res, width=500)

        # --- LIBRARY ---
        elif st.session_state.page == "LIBRARY":
            f_lib = st.session_state.library
            if not f_lib: st.write("EMPTY")
            else:
                l_cols = st.columns(3)
                for idx, item in enumerate(reversed(f_lib)):
                    with l_cols[idx % 3]:
                        if item['type'] == "image": st.image(item['url'])
                        else: st.audio(item['url'])
                        if st.button("🗑", key=f"del_{idx}"): 
                            st.session_state.library.remove(item); st.rerun()
                        st.markdown("---")

        # --- ENGINE & SYSTEM ---
        elif st.session_state.page == "ENGINE":
            st.session_state.brightness = st.slider("LIGHT", 0.0, 1.0, st.session_state.brightness)
            ep = st.text_area("ENV PROMPT:")
            if st.button("UPDATE"):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                st.session_state.wallpaper = get_url(res); st.rerun()

        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("COLOR", st.session_state.accent_color)
            if st.button("RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)



































