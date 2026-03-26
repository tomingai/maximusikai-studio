import streamlit as st
import replicate
import os
import random
import requests
from io import BytesIO

# --- 1. SYSTEM-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v6.6 FINAL", layout="wide", initial_sidebar_state="collapsed")

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
        }}
        [data-testid="stHeader"], .main {{ background: transparent !important; }}
        h1, h2, h3, p, label, .stCaption {{ color: {accent} !important; text-shadow: 0 0 10px {accent}77 !important; font-family: monospace !important; }}
        .window-box {{ background: rgba(0, 5, 12, 0.94); backdrop-filter: blur(50px); border: 2px solid {accent}33; border-radius: 40px; padding: 40px; }}
        .stButton > button {{ background: rgba(0,0,0,0.6) !important; border: 1px solid {accent}44 !important; color: {accent} !important; border-radius: 15px !important; height: 50px !important; font-weight: bold; }}
        audio {{ filter: sepia(1) saturate(5) hue-rotate(160deg); width: 100%; border-radius: 12px; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:10vh; font-size:3.5rem;'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    cols = st.columns(5)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
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

        # --- AUDIO (FIXAD MODELL-PATH) ---
        if st.session_state.page == "AUDIO":
            st.write("### SONIC GENERATOR")
            if st.button("🎲 SLUMPA BEAT"):
                st.session_state.last_synth_p = get_random_prompt("AUDIO"); st.rerun()
            ap = st.text_input("PROMPT:", value=st.session_state.last_synth_p)
            if st.button("GENERATE AUDIO", use_container_width=True):
                with st.spinner("Neural Composing..."):
                    try:
                        # FIX: Använder den mest stabila officiella pathen
                        res = replicate.run("meta/musicgen", input={"prompt": ap, "duration": 8})
                        st.session_state.last_audio_res = res
                        st.session_state.library.append({"type": "audio", "url": res, "prompt": ap})
                    except Exception as e:
                        st.error(f"Replicate Error: {e}")
                st.rerun()
            if st.session_state.last_audio_res:
                st.audio(st.session_state.last_audio_res)

        # --- SYNTH ---
        elif st.session_state.page == "SYNTH":
            if st.button("🎲 SLUMPA"):
                st.session_state.last_synth_p = get_random_prompt("IMAGE"); st.rerun()
            p = st.text_area("PROMPT:", value=st.session_state.last_synth_p)
            if st.button("SYNTHESIZE", use_container_width=True):
                with st.spinner("Syncing Vision..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    url = get_url(res)
                    st.session_state.last_image_res = url
                    st.session_state.library.append({"type": "image", "url": url, "prompt": p})
                st.rerun()
            if st.session_state.last_image_res:
                st.image(st.session_state.last_image_res, width=400)

        # --- ARKIV (KOMPAKT + DOWNLOAD) ---
        elif st.session_state.page == "LIBRARY":
            st.session_state.lib_filter = st.radio("FILTER:", ["ALLA", "BILDER", "LJUD"], horizontal=True)
            f_lib = st.session_state.library
            if st.session_state.lib_filter == "BILDER": f_lib = [i for i in f_lib if i['type'] == "image"]
            if st.session_state.lib_filter == "LJUD": f_lib = [i for i in f_lib if i['type'] == "audio"]

            if not f_lib: st.write("ARKIVET ÄR TOMT")
            else:
                lib_cols = st.columns(3)
                for idx, item in enumerate(reversed(f_lib)):
                    with lib_cols[idx % 3]:
                        if item['type'] == "image": st.image(item['url'], use_container_width=True)
                        else: st.audio(item['url'])
                        st.caption(f"{item['prompt'][:20]}...")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            if st.button("🗑", key=f"del_{idx}"):
                                st.session_state.library.remove(item); st.rerun()
                        with c2:
                            if item['type'] == "image" and st.button("🖼", key=f"bg_{idx}"):
                                st.session_state.wallpaper = item['url']; st.rerun()
                        with c3:
                            try:
                                response = requests.get(item['url'])
                                ext = "png" if item['type'] == "image" else "wav"
                                st.download_button(label="💾", data=response.content, file_name=f"maximusik_{idx}.{ext}", mime=f"{item['type']}/{ext}", key=f"dl_{idx}")
                            except: st.write("err")
                        st.markdown("---")

        # --- ENGINE & SYSTEM ---
        elif st.session_state.page == "ENGINE":
            st.session_state.brightness = st.slider("LJUSSTYRKA", 0.0, 1.0, st.session_state.brightness)
            ep = st.text_area("MILJÖ-PROMPT (16:9):")
            if st.button("UPDATE REALITY"):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                url = get_url(res)
                st.session_state.wallpaper = url
                st.session_state.library.append({"type": "image", "url": url, "prompt": ep})
                st.rerun()

        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("NEON FÄRG:", st.session_state.accent_color)
            if st.button("HARD RESET"):
                st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


































