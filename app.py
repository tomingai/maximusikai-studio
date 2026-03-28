import streamlit as st
import replicate
import os
import random
import requests

# --- 1. SYSTEM-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v9.1.1", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# LÅSTA SYSTEM-STATES (Regel 10)
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

# --- 2. HJÄLPFUNKTIONER (Regel 4) ---
def get_url(res):
    try:
        if isinstance(res, list) and len(res) > 0: return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except: return str(res)

def get_random_prompt(mode="IMAGE", genre=None):
    if genre is None: genre = random.choice(["CYBERPUNK", "SPACE", "NATURE", "RETRO"])
    prompts = {
        "CYBERPUNK": {"IMAGE": ["Neon Tokyo DJ", "Android rain"], "AUDIO": ["Dark techno"], "ENV": ["Neon harbor"]},
        "SPACE": {"IMAGE": ["Nebula stars", "Black hole"], "AUDIO": ["Space pads"], "ENV": ["Mars base"]},
        "NATURE": {"IMAGE": ["Magic forest", "Waterfall"], "AUDIO": ["Zen flute"], "ENV": ["Jungle temple"]},
        "RETRO": {"IMAGE": ["80s sunset", "Pixel arcade"], "AUDIO": ["Synth-pop"], "ENV": ["1984 arcade"]}
    }
    return random.choice(prompts[genre][mode])

def sonify_logic(image_url, prompt_context):
    try:
        descr = replicate.run("lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                             input={"image": image_url, "prompt": "Music mood in 5 words."})
        res = replicate.run("meta/musicgen", input={"prompt": f"{descr}, {prompt_context}", "duration": 10})
        url = get_url(res)
        st.session_state.library.append({"type": "audio", "url": url, "prompt": f"Auto: {str(descr)[:10]}"})
        return url
    except: return None

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
        .window-box {{ background: rgba(0, 5, 15, 0.94); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 25px; padding: 25px; margin-top: 5px; }}
        .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.6); padding: 8px; border-radius: 12px; margin-bottom: 15px; border: 1px solid {accent}22; }}
        h1, h2, h3, p, label {{ color: {accent} !important; font-family: 'Courier New', monospace !important; text-shadow: 0 0 8px {accent}44; }}
        .stButton > button {{ background: rgba(0,0,0,0.4) !important; border: 1px solid {accent}33 !important; color: {accent} !important; border-radius: 8px !important; }}
        audio, video {{ filter: sepia(1) saturate(5) hue-rotate(160deg); width: 100%; border-radius: 12px; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:20px; padding-top:20vh; font-size:4rem; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
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
        # NAVIGATION SNABBMENY
        st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
        nc = st.columns(7)
        nav_items = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "LIBRARY"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
        for i, (icon, target) in enumerate(nav_items):
            if nc[i].button(icon, key=f"n_{target}", use_container_width=True):
                st.session_state.page = target; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="window-box">', unsafe_allow_html=True)

        # SYNTH (Regel 1 & 4)
        if st.session_state.page == "SYNTH":
            col_g, col_i = st.columns([0.7, 0.3])
            genre = col_g.selectbox("GENRE:", ["CYBERPUNK", "SPACE", "NATURE", "RETRO"], index=0)
            if col_i.button("🚀 IGNITION"):
                st.session_state.last_synth_p = get_random_prompt("IMAGE", genre); st.rerun()
            
            t1, t2 = st.tabs(["GENERATE", "UPLOAD"])
            with t1:
                p = st.text_area("IMAGE PROMPT:", value=st.session_state.last_synth_p)
                if st.button("CREATE IMAGE + AUDIO", use_container_width=True):
                    with st.spinner("Rendering..."):
                        img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                        st.session_state.last_image_res = get_url(img)
                        st.session_state.library.append({"type": "image", "url": st.session_state.last_image_res, "prompt": p})
                        st.session_state.last_audio_res = sonify_logic(st.session_state.last_image_res, p)
                        st.rerun()
            with t2:
                up = st.file_uploader("UPLOAD:", type=["jpg", "png"])
                if up: st.session_state.last_image_res = up
            
            if st.session_state.last_image_res:
                st.image(st.session_state.last_image_res, width=300)
                if st.button("🎬 ANIMERA DENNA BILD"): st.session_state.page = "MOVIE"; st.rerun()

        # AUDIO (Regel 2)
        elif st.session_state.page == "AUDIO":
            st.write("### MANUAL AUDIO")
            ap = st.text_input("PROMPT:")
            if st.button("GENERATE 15S", use_container_width=True):
                res = replicate.run("meta/musicgen", input={"prompt": ap, "duration": 15})
                st.session_state.last_audio_res = get_url(res)
                st.session_state.library.append({"type": "audio", "url": st.session_state.last_audio_res, "prompt": ap}); st.rerun()
            if st.session_state.last_audio_res: st.audio(st.session_state.last_audio_res)

        # MOVIE (Regel 3 & MERGE)
        elif st.session_state.page == "MOVIE":
            if st.session_state.last_image_res:
                if st.button("RENDER MOVIE FROM IMAGE"):
                    with st.spinner("Animating..."):
                        res = replicate.run("stability-ai/video-diffusion:3f0457148a1aa577d638be204a4002c1d58ce1bd57b7f7c4d328b3d24883990c", input={"input_image": st.session_state.last_image_res})
                        st.session_state.last_video_res = get_url(res)
                        st.session_state.library.append({"type": "video", "url": st.session_state.last_video_res, "prompt": "Movie"}); st.rerun()
            
            if st.session_state.last_video_res:
                st.video(st.session_state.last_video_res)
                mv1, mv2 = st.tabs(["SUBTITLES", "MERGE AUDIO"])
                with mv1:
                    txt = st.text_input("SUBTITLE TEXT:")
                    if st.button("BURN TEXT"):
                        res = replicate.run("chenxwh/video-subtitle:c7457788", input={"video": st.session_state.last_video_res, "text": txt})
                        st.session_state.last_video_res = get_url(res); st.rerun()
                with mv2:
                    if st.session_state.last_audio_res:
                        if st.button("🔊 MERGE VIDEO + MUSIC"):
                            res = replicate.run("nateraw/ffmpeg-video-audio-mix:676f44d", input={"video": st.session_state.last_video_res, "audio": st.session_state.last_audio_res})
                            st.session_state.last_video_res = get_url(res); st.rerun()
            else: st.info("Create image in SYNTH first.")

        # ARKIV (Regel 5 & 6)
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
                    c1, c2 = st.columns(2)
                    if c1.button("🗑", key=f"d_{idx}"): st.session_state.library.remove(item); st.rerun()
                    try:
                        resp = requests.get(item['url'])
                        c2.download_button("💾", resp.content, f"f_{idx}.png", key=f"dl_{idx}")
                    except: pass
                    st.markdown("---")

        # ENGINE & SYSTEM (Regel 7)
        elif st.session_state.page == "ENGINE":
            st.session_state.brightness = st.slider("LIGHT", 0.0, 1.0, st.session_state.brightness)
            ep = st.text_area("ENV PROMPT (16:9):")
            if st.button("UPDATE ENGINE"):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                st.session_state.wallpaper = get_url(res); st.rerun()

        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("COLOR", st.session_state.accent_color)
            st.session_state.volume = st.slider("VOLUME", 0.0, 1.0, st.session_state.volume)
            if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)













































