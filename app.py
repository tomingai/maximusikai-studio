import streamlit as st
import replicate
import os
import random
import requests

# --- 1. SYSTEM-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v7.8 FIXED", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# LÅSTA SYSTEM-STATES
states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "brightness": 0.5,
    "volume": 0.8,
    "library": [],
    "last_synth_p": "",
    "last_audio_res": None,
    "last_image_res": None,
    "last_video_res": None,
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

def sonify_image(image_input):
    with st.spinner("Analyzing visuals for audio..."):
        try:
            descr = replicate.run(
                "lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                input={"image": image_input, "prompt": "Describe the musical style and mood in 8 words."}
            )
            # Låst stabil version av MusicGen
            res = replicate.run(
                "facebookresearch/musicgen:7a76a8258502edb298485a3666d92021614f94bb2ed02901399677334466d3a8", 
                input={"prompt": f"Music: {descr}", "duration": 15}
            )
            st.session_state.library.append({"type": "audio", "url": res, "prompt": f"Sonify: {descr[:15]}"})
            return res
        except Exception as e: st.error(f"Audio Error: {e}"); return None

def animate_image(image_url):
    with st.spinner("Rendering Cinematic Motion..."):
        try:
            res = replicate.run(
                "stability-ai/video-diffusion:3f0457148a1aa577d638be204a4002c1d58ce1bd57b7f7c4d328b3d24883990c", 
                input={"input_image": image_url}
            )
            video_url = get_url(res)
            st.session_state.library.append({"type": "video", "url": video_url, "prompt": "Motion Render"})
            return video_url
        except Exception as e: st.error(f"Video Error: {e}"); return None

# --- 3. UI ENGINE ---
def apply_ui():
    accent = st.session_state.accent_color
    bright = st.session_state.brightness
    vol = st.session_state.volume
    overlay = 1.0 - bright 
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,{overlay}), rgba(0,0,0,{overlay + 0.1})), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; background-attachment: fixed !important;
        }}
        .window-box {{ background: rgba(0, 5, 15, 0.93); backdrop-filter: blur(30px); border: 1px solid {accent}33; border-radius: 30px; padding: 40px; }}
        h1, h2, h3, p, label {{ color: {accent} !important; font-family: 'Courier New', monospace !important; }}
        .stButton > button {{ background: rgba(0,0,0,0.6) !important; border: 1px solid {accent}44 !important; color: {accent} !important; border-radius: 12px !important; }}
        audio, video {{ filter: sepia(1) saturate(5) hue-rotate(160deg); width: 100%; border-radius: 15px; }}
        </style>
        <script>
        var audios = document.getElementsByTagName('audio');
        for(var i = 0; i < audios.length; i++){{ audios[i].volume = {vol}; }}
        </script>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:15vh; font-size:4.5rem; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    cols = st.columns(6)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("🎬 MOVIE", "MOVIE"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
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

        if st.session_state.page == "SYNTH":
            tab1, tab2 = st.tabs(["GENERATE", "UPLOAD"])
            with tab1:
                p = st.text_area("VISUAL PROMPT:")
                if st.button("CREATE IMAGE"):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_image_res = get_url(res)
                    st.session_state.library.append({"type": "image", "url": st.session_state.last_image_res, "prompt": p}); st.rerun()
            with tab2:
                up = st.file_uploader("CHOOSE IMAGE:", type=["jpg", "png", "jpeg"])
                if up: st.session_state.last_image_res = up
            if st.session_state.last_image_res:
                st.image(st.session_state.last_image_res, width=300)
                if st.button("🎬 ANIMATE (MAKE MOVIE)"): 
                    st.session_state.last_video_res = animate_image(st.session_state.last_image_res); st.rerun()

        elif st.session_state.page == "AUDIO":
            ap = st.text_input("SONIC PROMPT:")
            dur = st.slider("DURATION (SEC):", 5, 30, 15)
            if st.button("GENERATE"):
                with st.spinner("Generating stable audio..."):
                    res = replicate.run(
                        "facebookresearch/musicgen:7a76a8258502edb298485a3666d92021614f94bb2ed02901399677334466d3a8", 
                        input={"prompt": ap, "duration": dur}
                    )
                    st.session_state.last_audio_res = res
                    st.session_state.library.append({"type": "audio", "url": res, "prompt": ap}); st.rerun()
            if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

        elif st.session_state.page == "MOVIE":
            if st.session_state.last_video_res:
                st.video(st.session_state.last_video_res)
                if st.button("🎵 SONIFY VIDEO"):
                    st.session_state.last_audio_res = sonify_image(st.session_state.last_video_res); st.rerun()
            else:
                st.info("Skapa en bild i SYNTH först och välj ANIMATE.")

        elif st.session_state.page == "LIBRARY":
            st.session_state.lib_filter = st.radio("FILTER:", ["BILDER", "LJUD", "FILM"], horizontal=True)
            f_lib = [i for i in st.session_state.library if (st.session_state.lib_filter == "BILDER" and i['type'] == "image") or (st.session_state.lib_filter == "LJUD" and i['type'] == "audio") or (st.session_state.lib_filter == "FILM" and i['type'] == "video")]
            l_cols = st.columns(3)
            for idx, item in enumerate(reversed(f_lib)):
                with l_cols[idx % 3]:
                    if item['type'] == "image": st.image(item['url'])
                    elif item['type'] == "video": st.video(item['url'])
                    else: st.audio(item['url'])
                    if st.button("🗑", key=f"d_{idx}"): st.session_state.library.remove(item); st.rerun()
                    st.markdown("---")

        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("COLOR", st.session_state.accent_color)
            st.session_state.volume = st.slider("VOLUME", 0.0, 1.0, st.session_state.volume)
            if st.button("RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)









































