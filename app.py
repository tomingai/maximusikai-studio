import streamlit as st
import replicate
import os
import random

# --- 1. SYSTEM-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v6.2 PRO", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# LÅSTA SYSTEM-STATES (Här bor ryggraden i ditt OS)
states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "brightness": 0.5,
    "library": [],
    "last_synth_p": "",
    "last_audio_res": None,
    "last_image_res": None
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. HJÄLPFUNKTIONER (BUGG-STOPPARE) ---
def get_url(res):
    """Extraherar URL och förhindrar AttributeError"""
    try:
        if isinstance(res, list) and len(res) > 0: return str(res[0])
        if hasattr(res, 'url'): return str(res.url)
        return str(res)
    except:
        return str(res)

def get_random_prompt(mode="IMAGE"):
    img_prompts = ["Cyberpunk city neon rain", "Deep space nebula", "Ancient forest bioluminescent", "Retro robot DJ", "Futuristic spaceship cockpit"]
    audio_prompts = ["Dark techno beat 128bpm", "Space ambient pads", "Cyberpunk industrial", "Lofi hip hop chill", "Laser fire sound effects"]
    return random.choice(audio_prompts if mode == "AUDIO" else img_prompts)

# --- 3. UI ENGINE (LÅST DESIGN) ---
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
            transition: 0.8s ease-in-out;
        }}
        [data-testid="stHeader"], .main {{ background: transparent !important; }}
        h1, h2, h3, p, label {{ color: {accent} !important; text-shadow: 0 0 10px {accent}77 !important; font-family: monospace !important; }}
        .window-box {{ background: rgba(0, 5, 12, 0.92); backdrop-filter: blur(50px); border: 2px solid {accent}33; border-radius: 30px; padding: 40px; }}
        .stButton > button {{ background: rgba(0,0,0,0.6) !important; border: 1px solid {accent}44 !important; color: {accent} !important; border-radius: 15px !important; height: 60px !important; font-weight: bold; }}
        .stButton > button:hover {{ border-color: {accent} !important; box-shadow: 0 0 20px {accent}55 !important; color: white !important; }}
        audio {{ filter: sepia(1) saturate(5) hue-rotate(160deg); width: 100%; border-radius: 12px; margin-top: 10px; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:10vh; font-size:3.5rem;'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.write("<br><br>", unsafe_allow_html=True)
    cols = st.columns(5)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"btn_{target}"):
                st.session_state.page = target; st.rerun()

# --- 5. WINDOWS & MODULER ---
else:
    _, win_col, _ = st.columns([0.05, 0.9, 0.05])
    with win_col:
        st.markdown('<div class="window-box">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2>// {st.session_state.page}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="exit_os"): st.session_state.page = "DESKTOP"; st.rerun()

        # --- AUDIO (BUGG-FRI LJUDMOTOR) ---
        if st.session_state.page == "AUDIO":
            st.write("### SONIC GENERATOR PRO")
            audio_type = st.radio("LJUD-MODALITET:", ["MUSIK (MusicGen)", "EFFEKT (AudioGen)"], horizontal=True)
            if st.button("🎲 SLUMPA"):
                st.session_state.last_synth_p = get_random_prompt("AUDIO"); st.rerun()
            ap = st.text_input("BESKRIV LJUD:", value=st.session_state.last_synth_p)
            dur = st.slider("LÄNGD (SEKUNDER):", 2, 15, 8)
            
            if st.button("EXECUTE SONIC SYNTH", use_container_width=True):
                with st.spinner("Rendering Neural Audio..."):
                    try:
                        # MusicGen-Small är bugg-fri och snabb
                        model = "facebookresearch/musicgen-small" if "MUSIK" in audio_type else "facebookresearch/audiogen"
                        res = replicate.run(model, input={"prompt": ap, "duration": dur})
                        st.session_state.last_audio_res = res
                        st.session_state.library.append({"type": "audio", "url": res, "prompt": f"[{audio_type}] {ap}"})
                    except Exception as e:
                        st.error(f"Anslutningsfel: {e}")
                st.rerun()
            if st.session_state.last_audio_res:
                st.audio(st.session_state.last_audio_res)

        # --- SYNTH (LÅST BILDMOTOR) ---
        elif st.session_state.page == "SYNTH":
            col_in, col_pre = st.columns([0.5, 0.5])
            with col_in:
                if st.button("🎲 SLUMPA VISION"):
                    st.session_state.last_synth_p = get_random_prompt("IMAGE"); st.rerun()
                p = st.text_area("BILD-PROMPT:", value=st.session_state.last_synth_p, height=150)
                if st.button("SYNTHESIZE", use_container_width=True):
                    with st.spinner("Syncing Vision..."):
                        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                        url = get_url(res)
                        st.session_state.last_image_res = url
                        st.session_state.library.append({"type": "image", "url": url, "prompt": p})
                    st.rerun()
            with col_pre:
                if st.session_state.last_image_res:
                    st.image(st.session_state.last_image_res, use_container_width=True)

        # --- LIBRARY (STABILT ARKIV) ---
        elif st.session_state.page == "LIBRARY":
            if not st.session_state.library: st.write("ARKIVET ÄR TOMT")
            else:
                for idx, item in enumerate(reversed(st.session_state.library)):
                    col_m, col_t = st.columns([0.6, 0.4])
                    with col_m:
                        if item['type'] == "image": st.image(item['url'], use_container_width=True)
                        else: st.audio(item['url'])
                    with col_t:
                        st.write(f"**PROMPT:**\n{item['prompt']}")
                        b1, b2 = st.columns(2)
                        if b1.button("🗑 RADERA", key=f"del_{idx}"):
                            # Hittar rätt index i den ursprungliga listan
                            st.session_state.library.pop(-(idx+1)); st.rerun()
                        if item['type'] == "image" and b2.button("🖼 BG", key=f"bg_{idx}"):
                            st.session_state.wallpaper = item['url']; st.rerun()

        # --- ENGINE & SYSTEM ---
        elif st.session_state.page == "ENGINE":
            st.session_state.brightness = st.slider("LJUSSTYRKA", 0.0, 1.0, st.session_state.brightness)
            ep = st.text_area("MILJÖ-PROMPT (16:9):")
            if st.button("UPDATE REALITY", use_container_width=True):
                with st.spinner("Syncing Reality..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = get_url(res)
                    st.session_state.library.append({"type": "image", "url": st.session_state.wallpaper, "prompt": ep})
                st.rerun()

        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("NEON FÄRG:", st.session_state.accent_color)
            if st.button("HARD RESET (RENSA ALLT)"):
                st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

































