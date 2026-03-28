import streamlit as st
import replicate
import os
import random
import requests

# --- 1. SYSTEM-KONFIGURATION (Regel 8, 9) ---
st.set_page_config(page_title="MAXIMUSIK AI OS v8.5 MERGE", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# LÅSTA SYSTEM-STATES (Regel 8)
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
    "last_video_res": None
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 2. HJÄLPFUNKTIONER (Regel 4, 10) ---
def get_url(res):
    try:
        if isinstance(res, list) and len(res) > 0: return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except: return str(res)

def get_random_prompt(mode="IMAGE"):
    img_prompts = ["Cyberpunk city neon rain", "Deep space nebula", "Ancient forest bioluminescent", "Retro robot DJ"]
    audio_prompts = ["Dark techno 128bpm heavy bass", "Space ambient pads", "Cyberpunk industrial", "Lofi hip hop chill"]
    env_prompts = ["Neon Tokyo skyline 2099", "Abandoned space station interior", "Digital rainforest with floating data", "Futuristic server room glow"]
    if mode == "AUDIO": return random.choice(audio_prompts)
    if mode == "ENV": return random.choice(env_prompts)
    return random.choice(img_prompts)

def sonify_image(image_input):
    with st.spinner("AI analyzing visuals..."):
        try:
            descr = replicate.run("lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                                 input={"image": image_input, "prompt": "Musical mood in 8 words."})
            res = replicate.run("meta/musicgen", input={"prompt": str(descr), "duration": 15})
            url = get_url(res)
            st.session_state.library.append({"type": "audio", "url": url, "prompt": f"Sonify: {str(descr)[:15]}"})
            return url
        except Exception as e: st.error(f"Error: {e}"); return None

# --- 3. UI ENGINE (Regel 9) ---
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
        .window-box {{ background: rgba(0, 5, 15, 0.94); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 30px; padding: 30px; margin-top: 10px; }}
        .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {accent}22; }}
        h1, h2, h3, p, label, .stCaption {{ color: {accent} !important; font-family: 'Courier New', monospace !important; text-shadow: 0 0 10px {accent}44; }}
        .stButton > button {{ background: rgba(0,0,0,0.4) !important; border: 1px solid {accent}33 !important; color: {accent} !important; border-radius: 10px !important; }}
        audio, video {{ filter: sepia(1) saturate(5) hue-rotate(160deg); width: 100%; border-radius: 15px; }}
        </style>
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
    _, win_col, _ = st.columns([0.02, 0.96, 0.02])
    with win_col:
        # SNABBMENY (Regel: FLOW)
        st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
        nc = st.columns(7)
        nav_items = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "LIBRARY"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
        for i, (icon, target) in enumerate(nav_items):
            if nc[i].button(icon, key=f"nav_{target}", use_container_width=True):
                st.session_state.page = target; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="window-box">', unsafe_allow_html=True)
        st.markdown(f"### // {st.session_state.page}")

        # SYNTH (Regel 1)
        if st.session_state.page == "SYNTH":
            t1, t2 = st.tabs(["GENERATE", "UPLOAD"])
            with t1:
                if st.button("🎲 RANDOM PROMPT"): st.session_state.last_synth_p = get_random_prompt("IMAGE"); st.rerun()
                p = st.text_area("PROMPT:", value=st.session_state.last_synth_p)
                if st.button("CREATE IMAGE", use_container_width=True):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_image_res = get_url(res)
                    st.session_state.library.append({"type": "image", "url": st.session_state.last_image_res, "prompt": p}); st.rerun()
            with t2:
                up = st.file_uploader("UPLOAD IMAGE:", type=["jpg", "png"])
                if up: st.session_state.last_image_res = up
            if st.session_state.last_image_res:
                st.image(st.session_state.last_image_res, width=300)
                c1, c2 = st.columns(2)
                if c1.button("🎬 ANIMATE"): st.session_state.page = "MOVIE"; st.rerun()
                if c2.button("🎵 SONIFY"): st.session_state.last_audio_res = sonify_image(st.session_state.last_image_res); st.rerun()

        # AUDIO (Regel 2)
        elif st.session_state.page == "AUDIO":
            t_a1, t_a2 = st.tabs(["MUSIC", "VOICE"])
            with t_a1:
                if st.button("🎲 RANDOM BEAT"): st.session_state.last_synth_p = get_random_prompt("AUDIO"); st.rerun()
                ap = st.text_input("SONIC PROMPT:", value=st.session_state.last_synth_p)
                if st.button("GENERATE MUSIC", use_container_width=True):
                    res = replicate.run("meta/musicgen", input={"prompt": ap, "duration": 15})
                    st.session_state.last_audio_res = get_url(res)
                    st.session_state.library.append({"type": "audio", "url": st.session_state.last_audio_res, "prompt": ap}); st.rerun()
            with t_a2:
                v_text = st.text_area("VOICEOVER SCRIPT:")
                if st.button("GENERATE VOICE", use_container_width=True):
                    res = replicate.run("elevenlabs/elevenlabs-tts", input={"text": v_text, "voice_id": "antoni"})
                    st.session_state.last_audio_res = get_url(res)
                    st.session_state.library.append({"type": "audio", "url": st.session_state.last_audio_res, "prompt": f"Voice: {v_text[:10]}"}); st.rerun()
            if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

        # MOVIE (Regel 3 & NY MERGE)
        elif st.session_state.page == "MOVIE":
            if st.session_state.last_image_res and not st.session_state.last_video_res:
                if st.button("ANIMERA SENASTE BILDEN"):
                    res = replicate.run("stability-ai/video-diffusion:3f0457148a1aa577d638be204a4002c1d58ce1bd57b7f7c4d328b3d24883990c", input={"input_image": st.session_state.last_image_res})
                    st.session_state.last_video_res = get_url(res)
                    st.session_state.library.append({"type": "video", "url": st.session_state.last_video_res, "prompt": "Render"}); st.rerun()
            
            if st.session_state.last_video_res:
                st.video(st.session_state.last_video_res)
                tab_v1, tab_v2 = st.tabs(["TEXT OVERLAY", "MERGE AUDIO"])
                with tab_v1:
                    txt = st.text_input("SUBTITLES:")
                    if st.button("BURN TEXT"):
                        res = replicate.run("chenxwh/video-subtitle:c7457788", input={"video": st.session_state.last_video_res, "text": txt})
                        st.session_state.last_video_res = get_url(res)
                        st.session_state.library.append({"type": "video", "url": st.session_state.last_video_res, "prompt": f"Sub: {txt}"}); st.rerun()
                with tab_v2:
                    st.write("Merge current video with latest audio (Music/Voice)")
                    if st.session_state.last_audio_res:
                        if st.button("MERGE VIDEO + AUDIO", use_container_width=True):
                            with st.spinner("Mixing..."):
                                res = replicate.run("nateraw/ffmpeg-video-audio-mix:676f44d", 
                                                   input={"video": st.session_state.last_video_res, "audio": st.session_state.last_audio_res})
                                st.session_state.last_video_res = get_url(res)
                                st.session_state.library.append({"type": "video", "url": st.session_state.last_video_res, "prompt": "Final Mix"}); st.rerun()
                    else: st.warning("Du behöver generera ljud i AUDIO först.")
            else: st.info("Skapa en bild i SYNTH först.")

        # ARKIV (Regel 5)
        elif st.session_state.page == "LIBRARY":
            st.session_state.lib_filter = st.radio("FILTER:", ["BILDER", "LJUD", "FILM"], horizontal=True)
            f_lib = [i for i in st.session_state.library if (st.session_state.lib_filter == "BILDER" and i['type'] == "image") or (st.session_state.lib_filter == "LJUD" and i['type'] == "audio") or (st.session_state.lib_filter == "FILM" and i['type'] == "video")]
            l_cols = st.columns(3)
            for idx, item in enumerate(reversed(f_lib)):
                with l_cols[idx % 3]:
                    if item['type'] == "image": st.image(item['url'])
                    elif item['type'] == "video": st.video(item['url'])
                    else: st.audio(item['url'])
                    c1, c2, c3 = st.columns(3)
                    if c1.button("🗑", key=f"d_{idx}"): st.session_state.library.remove(item); st.rerun()
                    if item['type'] == "image" and c2.button("🖼", key=f"b_{idx}"): st.session_state.wallpaper = item['url']; st.rerun()
                    try:
                        resp = requests.get(item['url'])
                        st.download_button("💾", resp.content, f"file_{idx}.png", key=f"dl_{idx}")
                    except: pass
                    st.markdown("---")

        # ENGINE (Regel 6 + NY Slump)
        elif st.session_state.page == "ENGINE":
            st.session_state.brightness = st.slider("BRIGHTNESS", 0.0, 1.0, st.session_state.brightness)
            if st.button("🎲 RANDOM ENVIRONMENT"): st.session_state.last_synth_p = get_random_prompt("ENV"); st.rerun()
            ep = st.text_area("ENV PROMPT:", value=st.session_state.last_synth_p)
            if st.button("UPDATE REALITY"):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                st.session_state.wallpaper = get_url(res); st.rerun()

        # SYSTEM (Regel 7)
        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("COLOR", st.session_state.accent_color)
            st.session_state.volume = st.slider("VOLUME", 0.0, 1.0, st.session_state.volume)
            if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)










































