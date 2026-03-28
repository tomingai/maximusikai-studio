import streamlit as st
import replicate
import os
import random
import requests
import json

# --- 1. SYSTEM-KONFIGURATION & REGLER ---
# VERSION: 9.2.1 | STATUS: STABIL | REGLER 1-12 AKTIVA
st.set_page_config(page_title="MAXIMUSIK AI OS v9.2.1", layout="wide", initial_sidebar_state="collapsed")

# API-Token hantering
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

DB_FILE = "maximusik_history.json"

# --- 2. LÅSTA SYSTEM-STATES (Persistence Logic) ---
def load_history():
    """Laddar historik från fil om den finns (Regel 11)."""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except: return []
    return []

def save_history():
    """Sparar biblioteket till disk (Regel 11)."""
    try:
        with open(DB_FILE, "w") as f:
            json.dump(st.session_state.library, f)
    except: pass

# Initialisera states om de inte finns
states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "brightness": 0.5,
    "volume": 0.8,
    "library": load_history(),
    "last_synth_p": "",
    "last_audio_res": None,
    "last_image_res": None,
    "last_video_res": None,
    "slump_genre": "CYBERPUNK"
}

for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 3. CORE LOGIC (Regel 4) ---
def get_url(res):
    """Extraherar URL oavsett Replicate-objektets typ."""
    try:
        if isinstance(res, list): return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except: return str(res)

def sonify_logic(image_url, prompt_context):
    """Analyserar bild och skapar matchande ljud (Regel 4)."""
    try:
        # 1. Bildbeskrivning
        descr = replicate.run("lucataco/moondream2:610746815820698144-8848-436e-b76e-07a829a7386d", 
                             input={"image": image_url, "prompt": "Music mood in 5 words."})
        # 2. Generera ljud
        res = replicate.run("meta/musicgen:671ac645", 
                             input={"prompt": f"{descr}, {prompt_context}", "duration": 10})
        url = get_url(res)
        # Spara till bibliotek
        st.session_state.library.append({"type": "audio", "url": url, "prompt": f"Auto-Sonify: {prompt_context[:15]}"})
        save_history()
        return url
    except Exception as e:
        st.error(f"Sonify Error: {e}")
        return None

# --- 4. UI ENGINE (Regel 2 & 9) ---
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
        .window-box {{ background: rgba(0, 5, 15, 0.94); backdrop-filter: blur(40px); border: 1px solid {accent}33; border-radius: 25px; padding: 25px; margin-top: 5px; }}
        .nav-bar {{ display: flex; justify-content: space-around; background: rgba(0,0,0,0.6); padding: 8px; border-radius: 12px; margin-bottom: 15px; border: 1px solid {accent}22; }}
        h1, h2, h3, p, label {{ color: {accent} !important; font-family: 'Courier New', monospace !important; text-shadow: 0 0 8px {accent}44; }}
        .stButton > button {{ background: rgba(0,0,0,0.4) !important; border: 1px solid {accent}33 !important; color: {accent} !important; border-radius: 8px !important; }}
        audio, video {{ filter: sepia(1) saturate(5) hue-rotate(160deg); width: 100%; border-radius: 12px; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 5. DESKTOP NAVIGATION ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:20px; padding-top:20vh; font-size:4rem; font-weight:900;'>MAXIMUSIK</h1>", unsafe_allow_html=True)
    cols = st.columns(6)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("🎬 MOVIE", "MOVIE"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"d_btn_{target}"):
                st.session_state.page = target; st.rerun()

# --- 6. WINDOWS LOGIC (Regel 12) ---
else:
    _, win_col, _ = st.columns([0.02, 0.96, 0.02])
    with win_col:
        # Global Navigations-meny
        st.markdown('<div class="nav-bar">', unsafe_allow_html=True)
        nc = st.columns(7)
        nav_items = [("🏠", "DESKTOP"), ("🪄", "SYNTH"), ("🎧", "AUDIO"), ("🎬", "MOVIE"), ("📚", "LIBRARY"), ("🖼", "ENGINE"), ("⚙️", "SYSTEM")]
        for i, (icon, target) in enumerate(nav_items):
            if nc[i].button(icon, key=f"nav_{target}", use_container_width=True):
                st.session_state.page = target; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="window-box">', unsafe_allow_html=True)

        # --- MODUL: SYNTH ---
        if st.session_state.page == "SYNTH":
            col_g, col_i = st.columns([0.7, 0.3])
            genre_list = ["CYBERPUNK", "SPACE", "NATURE", "RETRO"]
            genre = col_g.selectbox("VÄLJ STIL:", genre_list)
            
            if col_i.button("🚀 RANDOM PROMPT"):
                # Enkel slumpgenerator (Regel 4)
                prompts = ["Neon DJ in space", "Cyber forest with bioluminescence", "Retro sunset with grids"]
                st.session_state.last_synth_p = random.choice(prompts)
                st.rerun()
            
            p = st.text_area("IMAGE PROMPT:", value=st.session_state.last_synth_p)
            if st.button("RENDER UNIVERSE", use_container_width=True):
                with st.spinner("Processing..."):
                    img_res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.last_image_res = get_url(img_res)
                    st.session_state.library.append({"type": "image", "url": st.session_state.last_image_res, "prompt": p})
                    st.session_state.last_audio_res = sonify_logic(st.session_state.last_image_res, p)
                    save_history(); st.rerun()
            
            if st.session_state.last_image_res:
                st.image(st.session_state.last_image_res, width=400)
                if st.button("🎬 ANIMERA DENNA"): st.session_state.page = "MOVIE"; st.rerun()

        # --- MODUL: AUDIO ---
        elif st.session_state.page == "AUDIO":
            st.write("### 🎧 AUDIO SYNTH")
            ap = st.text_input("BESKRIV LJUDET:", placeholder="Ex: Heavy industrial techno beat")
            if st.button("SKAPA LJUD (10S)"):
                with st.spinner("Genererar vågformer..."):
                    res = replicate.run("meta/musicgen:671ac645", input={"prompt": ap, "duration": 10})
                    st.session_state.last_audio_res = get_url(res)
                    st.session_state.library.append({"type": "audio", "url": st.session_state.last_audio_res, "prompt": ap})
                    save_history(); st.rerun()
            if st.session_state.last_audio_res:
                st.audio(st.session_state.last_audio_res)

        # --- MODUL: MOVIE ---
        elif st.session_state.page == "MOVIE":
            st.write("### 🎬 MOVIE ENGINE")
            if st.session_state.last_image_res:
                st.image(st.session_state.last_image_res, width=200, caption="Input Bild")
                if st.button("SKAPA RÖRELSE (VIDEO)"):
                    with st.spinner("Animerar pixlar..."):
                        res = replicate.run("stability-ai/video-diffusion:3f0457148a1aa577d638be204a4002c1d58ce1bd57b7f7c4d328b3d24883990c", 
                                            input={"input_image": st.session_state.last_image_res})
                        st.session_state.last_video_res = get_url(res)
                        st.session_state.library.append({"type": "video", "url": st.session_state.last_video_res, "prompt": "AI Motion"})
                        save_history(); st.rerun()
            
            if st.session_state.last_video_res:
                st.video(st.session_state.last_video_res)
                if st.button("🔊 KOPPLA IHOP MED SENASTE LJUD") and st.session_state.last_audio_res:
                    with st.spinner("Merging..."):
                        res = replicate.run("cjwbw/video-extra-audio:8848-436e-b76e-07a829a7386d", 
                                            input={"video": st.session_state.last_video_res, "audio": st.session_state.last_audio_res})
                        st.session_state.last_video_res = get_url(res)
                        save_history(); st.rerun()

        # --- MODUL: LIBRARY (Download Center) ---
        elif st.session_state.page == "LIBRARY":
            st.write("### 📚 SYSTEM ARKIV")
            if not st.session_state.library:
                st.info("Arkivet är tomt.")
            for i, item in enumerate(reversed(st.session_state.library)):
                with st.expander(f"{item['type'].upper()} - {item['prompt'][:25]}..."):
                    if item['type'] == "image": st.image(item['url'])
                    elif item['type'] == "audio": st.audio(item['url'])
                    elif item['type'] == "video": st.video(item['url'])
                    
                    try:
                        file_bytes = requests.get(item['url']).content
                        ext = "png" if item['type'] == "image" else "mp3" if item['type'] == "audio" else "mp4"
                        st.download_button(f"LADDA NER .{ext}", file_bytes, file_name=f"maxi_{i}.{ext}", key=f"dl_{i}")
                    except: st.error("Kunde inte hämta filen.")

        # --- MODUL: ENGINE ---
        elif st.session_state.page == "ENGINE":
            st.write("### 🖼 WALLPAPER ENGINE")
            wp_p = st.text_input("SKAPA NY BAKGRUND:", placeholder="Ex: Abstract dark blue 4k")
            if st.button("GENERATE WALLPAPER"):
                img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": wp_p})
                st.session_state.wallpaper = get_url(img); st.rerun()

        # --- MODUL: SYSTEM ---
        elif st.session_state.page == "SYSTEM":
            st.write("### ⚙️ SYSTEM SETTINGS")
            st.session_state.accent_color = st.color_picker("FÄRGPROFIL", st.session_state.accent_color)
            st.session_state.brightness = st.slider("LJUSSTYRKA", 0.1, 1.0, st.session_state.brightness)
            if st.button("🔴 TOTAL RESET (Raderar allt)"):
                st.session_state.library = []
                if os.path.exists(DB_FILE): os.remove(DB_FILE)
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)














































