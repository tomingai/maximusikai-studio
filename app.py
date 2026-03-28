import streamlit as st
import replicate
import os
import random
import requests

# --- 1. SYSTEM-KONFIGURATION (Regel 8, 9) ---
st.set_page_config(page_title="MAXIMUSIK AI OS v8.3 VOICE", layout="wide", initial_sidebar_state="collapsed")

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

# --- 2. HJÄLPFUNKTIONER ---
def get_url(res):
    try:
        if isinstance(res, list) and len(res) > 0: return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except: return str(res)

def get_random_prompt(mode="IMAGE"):
    img_prompts = ["Cyberpunk city neon rain", "Deep space nebula", "Retro robot DJ"]
    audio_prompts = ["Dark techno 128bpm", "Space ambient pads", "Lofi hip hop chill"]
    return random.choice(audio_prompts if mode == "AUDIO" else img_prompts)

def sonify_image(image_input):
    with st.spinner("AI analyzing visuals..."):
        try:
            descr = replicate.run("lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                                 input={"image": image_input, "prompt": "Describe the mood in 8 words."})
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
        .window-box {{ background: rgba(0, 5, 15, 0.93); backdrop-filter: blur(30px); border: 1px solid {accent}33; border-radius: 30px; padding: 40px; margin-top: 20px; }}
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

        # SYNTH (Regel 1)
        if st.session_state.page == "SYNTH":
            t1, t2 = st.tabs(["GENERATE", "UPLOAD"])
            with t1:
                if st.button("🎲 RANDOM"): st.session_state.last_synth_p = get_random_prompt("IMAGE"); st.rerun()
                p = st.text_area("PROMPT:", value=st.session_state.last_synth_p)
                if st.button("CREATE IMAGE", use_container_width=True):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_image_res = get_url(res)
                    st.session_state.library.append({"type": "image", "url": st.session_state.last_image_res, "prompt": p}); st.rerun()
            with t2:
                up = st.file_uploader("IMAGE:", type=["jpg", "png"])
                if up: st.session_state.last_image_res = up
            if st.session_state.last_image_res:
                st.image(st.session_state.last_image_res, width=300)
                c1, c2 = st.columns(2)
                if c1.button("🎬 ANIMATE"):
                    res = replicate.run("stability-ai/video-diffusion:3f0457148a1aa577d638be204a4002c1d58ce1bd57b7f7c4d328b3d24883990c", input={"input_image": st.session_state.last_image_res})
                    st.session_state.last_video_res = get_url(res)
                    st.session_state.library.append({"type": "video", "url": st.session_state.last_video_res, "prompt": "Render"}); st.rerun()
                if c2.button("🎵 SONIFY"):
                    st.session_state.last_audio_res = sonify_image(st.session_state.last_image_res); st.rerun()

        # AUDIO (Regel 2 & NY Voiceover)
        elif st.session_state.page == "AUDIO":
            t_a1, t_a2 = st.tabs(["MUSIC ENGINE", "VOICEOVER (TTS)"])
            with t_a1:
                ap = st.text_input("SONIC PROMPT:", value=get_random_prompt("AUDIO"))
                dur = st.slider("SECONDS:", 5, 30, 15)
                if st.button("GENERATE MUSIC", use_container_width=True):
                    res = replicate.run("meta/musicgen", input={"prompt": ap, "duration": dur})
                    st.session_state.last_audio_res = get_url(res)
                    st.session_state.library.append({"type": "audio", "url": st.session_state.last_audio_res, "prompt": ap}); st.rerun()
            with t_a2:
                v_text = st.text_area("SCRIPT (MANUS):", placeholder="Välkommen till framtidens reklam...")
                v_voice = st.selectbox("VOICE:", ["Bella", "Antoni", "Arnold", "Josh"])
                if st.button("GENERATE VOICE", use_container_width=True):
                    with st.spinner("Synthesizing..."):
                        # ElevenLabs via Replicate (Smidigaste versionen)
                        res = replicate.run("elevenlabs/elevenlabs-tts", input={"text": v_text, "voice_id": v_voice.lower()})
                        st.session_state.last_audio_res = get_url(res)
                        st.session_state.library.append({"type": "audio", "url": st.session_state.last_audio_res, "prompt": f"Voice: {v_text[:15]}"}); st.rerun()
            if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

        # MOVIE (Regel 3 & 10)
        elif st.session_state.page == "MOVIE":
            if st.session_state.last_video_res:
                st.video(st.session_state.last_video_res)
                txt = st.text_input("SUBTITLE TEXT:")
                if st.button("BURN SUBTITLES"):
                    res = replicate.run("chenxwh/video-subtitle:c7457788", input={"video": st.session_state.last_video_res, "text": txt})
                    st.session_state.last_video_res = get_url(res)
                    st.session_state.library.append({"type": "video", "url": st.session_state.last_video_res, "prompt": f"Sub: {txt}"}); st.rerun()
            else: st.info("Create a video in SYNTH first.")

        # ARKIV (Regel 5)
        elif st.session_state.page == "LIBRARY":
            f_lib = st.session_state.library
            l_cols = st.columns(3)
            for idx, item in enumerate(reversed(f_lib)):
                with l_cols[idx % 3]:
                    if item['type'] == "image": st.image(item['url'])
                    elif item['type'] == "video": st.video(item['url'])
                    else: st.audio(item['url'])
                    c1, c2, c3, c4 = st.columns(4)
                    if c1.button("🗑", key=f"d_{idx}"): st.session_state.library.remove(item); st.rerun()
                    if item['type'] == "image" and c2.button("🖼", key=f"b_{idx}"): st.session_state.wallpaper = item['url']; st.rerun()
                    try:
                        resp = requests.get(item['url'])
                        c4.download_button("💾", resp.content, f"file_{idx}.png", key=f"dl_{idx}")
                    except: pass
                    st.markdown("---")

        # ENGINE & SYSTEM (Regel 6, 7)
        elif st.session_state.page == "ENGINE":
            st.session_state.brightness = st.slider("LIGHT", 0.0, 1.0, st.session_state.brightness)
            ep = st.text_area("ENV PROMPT (16:9):")
            if st.button("UPDATE REALITY"):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                st.session_state.wallpaper = get_url(res); st.rerun()

        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("COLOR", st.session_state.accent_color)
            st.session_state.volume = st.slider("VOLUME", 0.0, 1.0, st.session_state.volume)
            if st.button("RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)










































