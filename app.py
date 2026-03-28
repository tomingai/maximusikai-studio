import streamlit as st
import replicate
import os
import random
import requests

# --- 1. SYSTEM-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v9.0 AUTO-SONIFY", layout="wide", initial_sidebar_state="collapsed")

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
    "slump_genre": "CYBERPUNK"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 2. HJÄLPFUNKTIONER (Inkl. Auto-Sonify Logik) ---
def get_url(res):
    try:
        if isinstance(res, list) and len(res) > 0: return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except: return str(res)

def get_random_prompt(mode="IMAGE", genre=None):
    if genre is None:
        genre = random.choice(["CYBERPUNK", "SPACE", "NATURE", "RETRO"])
        st.session_state.slump_genre = genre
    prompts = {
        "CYBERPUNK": {
            "IMAGE": ["Neon Tokyo skyline 2099 rain", "Cybernetic DJ glowing wires", "Futuristic hover-car"],
            "AUDIO": ["Dark industrial techno 128bpm", "Glitchy synthwave", "Cyberpunk drone"],
            "ENV": ["Cyberpunk apartment interior", "Night city harbor neon"]
        },
        "SPACE": {
            "IMAGE": ["Purple nebula stars", "Astronaut black hole", "Alien crystal planet"],
            "AUDIO": ["Ethereal space pads", "Sci-fi theme", "Deep pulsar pulses"],
            "ENV": ["Mars base observation", "Wormhole tunnel"]
        },
        "NATURE": {
            "IMAGE": ["Bioluminescent forest", "Waterfall mountains", "Magic garden flowers"],
            "AUDIO": ["Nature zen flute", "Healing water ambient", "Forest spirit drums"],
            "ENV": ["Hidden jungle temple", "Icelandic aurora lake"]
        },
        "RETRO": {
            "IMAGE": ["80s synthwave sunset", "Retro robot cassette", "Pixel art arcade"],
            "AUDIO": ["80s synth-pop beat", "Lo-fi hip hop tape", "8bit chiptune"],
            "ENV": ["Retro-futuristic room", "Neon arcade 1984"]
        }
    }
    return random.choice(prompts[genre][mode])

def sonify_logic(image_url, prompt_context):
    """Automatiserad Sonify-process"""
    try:
        # Steg 1: Analys (Moondream)
        descr = replicate.run("lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                             input={"image": image_url, "prompt": "Describe the musical mood in 5 words."})
        # Steg 2: Musik (MusicGen)
        res = replicate.run("meta/musicgen", input={"prompt": f"{descr}, inspired by {prompt_context}", "duration": 10})
        url = get_url(res)
        st.session_state.library.append({"type": "audio", "url": url, "prompt": f"Auto-Sonify: {str(descr)[:15]}"})
        return url
    except: return None

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
        .window-box {{ background: rgba(0, 5, 15, 0.94); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 30px; padding: 30px; margin-top: 10px; }}
        .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {accent}22; }}
        h1, h2, h3, p, label {{ color: {accent} !important; font-family: 'Courier New', monospace !important; }}
        .stButton > button {{ background: rgba(0,0,0,0.4) !important; border: 1px solid {accent}33 !important; color: {accent} !important; border-radius: 10px !important; }}
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
    _, win_col, _ = st.columns([0.02, 0.96, 0.02])
    with win_col:
        st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
        nc = st.columns(7)
        nav_items = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "LIBRARY"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
        for i, (icon, target) in enumerate(nav_items):
            if nc[i].button(icon, key=f"nav_{target}", use_container_width=True):
                st.session_state.page = target; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="window-box">', unsafe_allow_html=True)

        # SYNTH (Med AUTO-SONIFY)
        if st.session_state.page == "SYNTH":
            col_g, col_i = st.columns([0.7, 0.3])
            genre = col_g.selectbox("GENRE:", ["CYBERPUNK", "SPACE", "NATURE", "RETRO"], index=["CYBERPUNK", "SPACE", "NATURE", "RETRO"].index(st.session_state.slump_genre))
            if col_i.button("🚀 NEURAL IGNITION", use_container_width=True):
                st.session_state.last_synth_p = get_random_prompt("IMAGE", None); st.rerun()
            
            p = st.text_area("PROMPT:", value=st.session_state.last_synth_p)
            if st.button("CREATE IMAGE & AUTO-SONIFY", use_container_width=True):
                with st.spinner("Visualizing..."):
                    img_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_image_res = get_url(img_res)
                    st.session_state.library.append({"type": "image", "url": st.session_state.last_image_res, "prompt": p})
                with st.spinner("Auto-Sonifying..."):
                    st.session_state.last_audio_res = sonify_logic(st.session_state.last_image_res, p)
                st.rerun()

            if st.session_state.last_image_res:
                st.image(st.session_state.last_image_res, width=300)
                if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)
                if st.button("🎬 ANIMATE"): st.session_state.page = "MOVIE"; st.rerun()

        # AUDIO
        elif st.session_state.page == "AUDIO":
            st.session_state.slump_genre = st.selectbox("GENRE:", ["CYBERPUNK", "SPACE", "NATURE", "RETRO"], key="aud_genre")
            if st.button("🎲 RANDOM BEAT"): 
                st.session_state.last_synth_p = get_random_prompt("AUDIO", st.session_state.slump_genre); st.rerun()
            ap = st.text_input("SONIC PROMPT:", value=st.session_state.last_synth_p)
            if st.button("GENERATE MUSIC", use_container_width=True):
                res = replicate.run("meta/musicgen", input={"prompt": ap, "duration": 15})
                st.session_state.last_audio_res = get_url(res)
                st.session_state.library.append({"type": "audio", "url": st.session_state.last_audio_res, "prompt": ap}); st.rerun()
            if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

        # MOVIE (MERGE VIDEO + AUDIO)
        elif st.session_state.page == "MOVIE":
            if st.session_state.last_image_res:
                if st.button("ANIMATE IMAGE"):
                    res = replicate.run("stability-ai/video-diffusion:3f0457148a1aa577d638be204a4002c1d58ce1bd57b7f7c4d328b3d24883990c", input={"input_image": st.session_state.last_image_res})
                    st.session_state.last_video_res = get_url(res)
                    st.session_state.library.append({"type": "video", "url": st.session_state.last_video_res, "prompt": "Render"}); st.rerun()
            if st.session_state.last_video_res:
                st.video(st.session_state.last_video_res)
                if st.session_state.last_audio_res:
                    if st.button("MERGE VIDEO + AUDIO"):
                        res = replicate.run("nateraw/ffmpeg-video-audio-mix:676f44d", input={"video": st.session_state.last_video_res, "audio": st.session_state.last_audio_res})
                        st.session_state.last_video_res = get_url(res)
                        st.session_state.library.append({"type": "video", "url": st.session_state.last_video_res, "prompt": "Final Mix"}); st.rerun()

        # LIBRARY
        elif st.session_state.page == "LIBRARY":
            f_lib = st.session_state.library
            l_cols = st.columns(3)
            for idx, item in enumerate(reversed(f_lib)):
                with l_cols[idx % 3]:
                    if item['type'] == "image": 
                        st.image(item['url'])
                        if st.button("🖼", key=f"b_{idx}"): st.session_state.wallpaper = item['url']; st.rerun()
                    elif item['type'] == "video": st.video(item['url'])
                    else: st.audio(item['url'])
                    if st.button("🗑", key=f"d_{idx}"): st.session_state.library.remove(item); st.rerun()
                    try:
                        resp = requests.get(item['url'])
                        st.download_button("💾", resp.content, f"file_{idx}.png", key=f"dl_{idx}")
                    except: pass
                    st.markdown("---")

        # ENGINE & SYSTEM
        elif st.session_state.page == "ENGINE":
            st.session_state.brightness = st.slider("LIGHT", 0.0, 1.0, st.session_state.brightness)
            if st.button("🚀 NEURAL IGNITION"): st.session_state.last_synth_p = get_random_prompt("ENV", None); st.rerun()
            ep = st.text_area("ENV PROMPT:", value=st.session_state.last_synth_p)
            if st.button("UPDATE"):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                st.session_state.wallpaper = get_url(res); st.rerun()

        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("COLOR", st.session_state.accent_color)
            st.session_state.brightness = st.slider("BRIGHTNESS", 0.0, 1.0, st.session_state.brightness)
            st.session_state.volume = st.slider("VOLUME", 0.0, 1.0, st.session_state.volume)
            if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)












































