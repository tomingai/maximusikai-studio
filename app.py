import streamlit as st
import replicate
import os
import random
import requests

# --- 1. SYSTEM-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v8.9 IGNITION", layout="wide", initial_sidebar_state="collapsed")

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

# --- 2. UTÖKAD SLUMP-MOTOR (Regel 2 & Inspirations-knapp) ---
def get_random_prompt(mode="IMAGE", genre=None):
    if genre is None:
        genre = random.choice(["CYBERPUNK", "SPACE", "NATURE", "RETRO"])
        st.session_state.slump_genre = genre
    
    prompts = {
        "CYBERPUNK": {
            "IMAGE": ["Neon Tokyo skyline 2099 rain", "Cybernetic DJ with glowing wires", "Futuristic hover-car in dark alley"],
            "AUDIO": ["Dark industrial techno 128bpm", "Glitchy synthwave with heavy bass", "Cyberpunk ambient drone"],
            "ENV": ["Cyberpunk apartment interior", "Night city harbor with neon signs"]
        },
        "SPACE": {
            "IMAGE": ["Deep space nebula with purple stars", "Astronaut looking at a black hole", "Alien crystal planet landscape"],
            "AUDIO": ["Ethereal space ambient pads", "Orchestral sci-fi theme", "Deep pulsar rhythmic pulses"],
            "ENV": ["Mars base observation deck", "Inside a wormhole tunnel"]
        },
        "NATURE": {
            "IMAGE": ["Bioluminescent ancient forest", "Golden hour waterfall in mountains", "Magic garden with floating flowers"],
            "AUDIO": ["Nature zen flute with birds", "Healing water ambient", "Forest spirit rhythmic drums"],
            "ENV": ["Hidden jungle temple", "Icelandic aurora over lake"]
        },
        "RETRO": {
            "IMAGE": ["80s synthwave sunset grid", "Retro robot holding a cassette", "Vintage pixel art arcade"],
            "AUDIO": ["80s retro synth-pop beat", "Lo-fi hip hop cassette tape", "Classic 8bit chiptune"],
            "ENV": ["Retro-futuristic living room", "Neon arcade hall 1984"]
        }
    }
    return random.choice(prompts[genre][mode])

def get_url(res):
    try:
        if isinstance(res, list) and len(res) > 0: return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except: return str(res)

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
            background-position: center !important;
        }}
        .window-box {{ background: rgba(0, 5, 15, 0.94); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 30px; padding: 30px; margin-top: 10px; }}
        .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 15px; margin-bottom: 20px; border: 1px solid {accent}22; }}
        h1, h2, h3, p, label, .stCaption {{ color: {accent} !important; font-family: 'Courier New', monospace !important; text-shadow: 0 0 10px {accent}44; }}
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

        # SYNTH
        if st.session_state.page == "SYNTH":
            col_g, col_i = st.columns([0.7, 0.3])
            genre = col_g.selectbox("GENRE:", ["CYBERPUNK", "SPACE", "NATURE", "RETRO"], index=["CYBERPUNK", "SPACE", "NATURE", "RETRO"].index(st.session_state.slump_genre))
            if col_i.button("🚀 NEURAL IGNITION", use_container_width=True):
                st.session_state.last_synth_p = get_random_prompt("IMAGE", None); st.rerun()
            
            t1, t2 = st.tabs(["GENERATE", "UPLOAD"])
            with t1:
                if st.button("🎲 RANDOM PROMPT"): 
                    st.session_state.last_synth_p = get_random_prompt("IMAGE", genre); st.rerun()
                p = st.text_area("PROMPT:", value=st.session_state.last_synth_p)
                if st.button("CREATE IMAGE", use_container_width=True):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_image_res = get_url(res)
                    st.session_state.library.append({"type": "image", "url": st.session_state.last_image_res, "prompt": p}); st.rerun()
            with t2:
                up = st.file_uploader("UPLOAD:", type=["jpg", "png"])
                if up: st.session_state.last_image_res = up
            if st.session_state.last_image_res:
                st.image(st.session_state.last_image_res, width=300)
                c1, c2 = st.columns(2)
                if c1.button("🎬 ANIMATE"): st.session_state.page = "MOVIE"; st.rerun()
                if c2.button("🎵 SONIFY"): 
                    res = replicate.run("meta/musicgen", input={"prompt": f"Soundtrack for {st.session_state.last_synth_p}", "duration": 15})
                    st.session_state.library.append({"type": "audio", "url": get_url(res), "prompt": "Sonify"}); st.rerun()

        # AUDIO
        elif st.session_state.page == "AUDIO":
            col_ga, col_ia = st.columns([0.7, 0.3])
            genre_a = col_ga.selectbox("GENRE:", ["CYBERPUNK", "SPACE", "NATURE", "RETRO"], key="aud_genre")
            if col_ia.button("🚀 NEURAL IGNITION", use_container_width=True, key="ign_aud"):
                st.session_state.last_synth_p = get_random_prompt("AUDIO", None); st.rerun()
            
            t_a1, t_a2 = st.tabs(["MUSIC", "VOICE"])
            with t_a1:
                if st.button("🎲 RANDOM BEAT"): 
                    st.session_state.last_synth_p = get_random_prompt("AUDIO", genre_a); st.rerun()
                ap = st.text_input("SONIC PROMPT:", value=st.session_state.last_synth_p)
                if st.button("GENERATE MUSIC", use_container_width=True):
                    res = replicate.run("meta/musicgen", input={"prompt": ap, "duration": 15})
                    st.session_state.last_audio_res = get_url(res)
                    st.session_state.library.append({"type": "audio", "url": st.session_state.last_audio_res, "prompt": ap}); st.rerun()
            with t_a2:
                v_text = st.text_area("SCRIPT:")
                if st.button("GENERATE VOICE", use_container_width=True):
                    res = replicate.run("elevenlabs/elevenlabs-tts", input={"text": v_text, "voice_id": "antoni"})
                    st.session_state.last_audio_res = get_url(res)
                    st.session_state.library.append({"type": "audio", "url": st.session_state.last_audio_res, "prompt": f"Voice: {v_text[:10]}"}); st.rerun()
            if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

        # MOVIE
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
            st.session_state.lib_filter = st.radio("FILTER:", ["BILDER", "LJUD", "FILM"], horizontal=True)
            f_lib = [i for i in st.session_state.library if (st.session_state.lib_filter == "BILDER" and i['type'] == "image") or (st.session_state.lib_filter == "LJUD" and i['type'] == "audio") or (st.session_state.lib_filter == "FILM" and i['type'] == "video")]
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

        # ENGINE
        elif st.session_state.page == "ENGINE":
            st.session_state.brightness = st.slider("LIGHT", 0.0, 1.0, st.session_state.brightness)
            if st.button("🚀 NEURAL IGNITION"): st.session_state.last_synth_p = get_random_prompt("ENV", None); st.rerun()
            ep = st.text_area("ENV PROMPT:", value=st.session_state.last_synth_p)
            if st.button("UPDATE"):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                st.session_state.wallpaper = get_url(res); st.rerun()

        # SYSTEM
        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("COLOR", st.session_state.accent_color)
            st.session_state.brightness = st.slider("BRIGHTNESS", 0.0, 1.0, st.session_state.brightness)
            st.session_state.volume = st.slider("VOLUME", 0.0, 1.0, st.session_state.volume)
            if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)











































