import streamlit as st
import replicate
import os
import random
import time

# --- 1. SYSTEM-KONFIGURATION ---
st.set_page_config(page_title="MAXIMUSIK AI OS v5.0", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# LÅSTA SYSTEM-STATES (Dessa försvinner inte vid sidbyte)
states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "brightness": 0.5,
    "library": [],
    "last_synth_p": "",
    "is_loading": False
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. HJÄLPFUNKTIONER (STABILITETSKONTROLL) ---
def get_url(res):
    """Säkerställer att vi alltid får en sträng-URL och undviker AttributeError"""
    if isinstance(res, list) and len(res) > 0: return str(res[0])
    return str(res)

def get_random_prompt(mode="IMAGE"):
    img_prompts = ["Cyberpunk city, neon rain", "Deep space nebula", "Ancient forest, bioluminescent", "Retro robot DJ", "Floating island"]
    audio_prompts = ["Dark techno, 128bpm", "Space ambient, pads", "Lofi hip hop, chill night", "Epic cinematic orchestral"]
    return random.choice(audio_prompts if mode == "AUDIO" else img_prompts)

# --- 3. UI ENGINE (LÅST DESIGN: GLITCH + LJUSSTYRKA) ---
def apply_ui():
    accent = st.session_state.accent_color
    bright = st.session_state.brightness
    overlay = 1.0 - bright 
    
    glitch_anim = """
    @keyframes glitch {
        0% { transform: translate(0); }
        20% { transform: translate(-2px, 2px); filter: hue-rotate(45deg); }
        40% { transform: translate(-2px, -2px); }
        100% { transform: translate(0); }
    }
    """ if st.session_state.is_loading else ""

    st.markdown(f"""
        <style>
        {glitch_anim}
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,{overlay}), rgba(0,0,0,{overlay + 0.1})), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; background-attachment: fixed !important;
            animation: {'glitch 0.2s infinite' if st.session_state.is_loading else 'none'};
            transition: 0.8s ease;
        }}
        [data-testid="stHeader"], .main {{ background: transparent !important; }}
        h1, h2, h3, p, label {{ color: {accent} !important; text-shadow: 0 0 10px {accent}77 !important; font-family: monospace !important; }}
        .window-box {{ background: rgba(0, 5, 12, 0.9); backdrop-filter: blur(50px); border: 1px solid {accent}33; border-radius: 30px; padding: 30px; }}
        .stButton > button {{ background: rgba(0,0,0,0.6) !important; border: 1px solid {accent}44 !important; color: {accent} !important; border-radius: 15px !important; height: 60px !important; font-weight: bold; }}
        .stButton > button:hover {{ border-color: {accent} !important; box-shadow: 0 0 20px {accent}44 !important; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP INTERFACE ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:10vh; font-size:3.5rem;'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    cols = st.columns(5)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        with cols[i]:
            if st.button(label, use_container_width=True):
                st.session_state.page = target; st.rerun()

# --- 5. WINDOWS & MODULER (ALLT ÄR INKLUDERAT HÄR) ---
else:
    _, win_col, _ = st.columns([0.05, 0.9, 0.05])
    with win_col:
        st.markdown('<div class="window-box">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2>// {st.session_state.page}</h2>", unsafe_allow_html=True)
        if h2.button("✕"): st.session_state.page = "DESKTOP"; st.rerun()

        # --- MODUL: SYNTH ---
        if st.session_state.page == "SYNTH":
            col_in, col_pre = st.columns([0.5, 0.5])
            with col_in:
                if st.button("🎲 SLUMPA VISION"): 
                    st.session_state.last_synth_p = get_random_prompt("IMAGE"); st.rerun()
                p = st.text_area("BILD-PROMPT:", value=st.session_state.last_synth_p, height=150)
                if st.button("EXECUTE SYNTHESIS", use_container_width=True):
                    with st.spinner("Neural Syncing..."):
                        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                        url = get_url(res)
                        st.session_state.library.append({"type": "image", "url": url, "prompt": p})
                        st.rerun()
            with col_pre:
                if st.session_state.library and st.session_state.library[-1]['type'] == "image":
                    st.image(st.session_state.library[-1]['url'], use_container_width=True)

        # --- MODUL: AUDIO ---
        elif st.session_state.page == "AUDIO":
            if st.button("🎲 SLUMPA BEAT"):
                st.session_state.last_synth_p = get_random_prompt("AUDIO"); st.rerun()
            ap = st.text_input("LJUD-PROMPT:", value=st.session_state.last_synth_p)
            if st.button("GENERATE AUDIO", use_container_width=True):
                with st.spinner("Composing..."):
                    res = replicate.run("meta/musicgen:b05b39c7", input={"prompt": ap, "duration": 10})
                    st.session_state.library.append({"type": "audio", "url": res, "prompt": ap})
                    st.rerun()
            if st.session_state.library and st.session_state.library[-1]['type'] == "audio":
                st.audio(st.session_state.library[-1]['url'])

        # --- MODUL: LIBRARY (ARKIV MED RADERING & TEXT INTILL) ---
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
                            st.session_state.library.pop(-(idx+1)); st.rerun()
                        if item['type'] == "image":
                            if b2.button("🖼 SÄTT BG", key=f"bg_{idx}"):
                                st.session_state.wallpaper = item['url']; st.rerun()

        # --- MODUL: ENGINE ---
        elif st.session_state.page == "ENGINE":
            st.session_state.brightness = st.slider("LJUSSTYRKA", 0.0, 1.0, st.session_state.brightness)
            ep = st.text_area("MILJÖ-PROMPT (16:9):")
            if st.button("UPDATE REALITY", use_container_width=True):
                with st.spinner("Syncing..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = get_url(res)
                    st.session_state.library.append({"type": "image", "url": st.session_state.wallpaper, "prompt": ep})
                    st.rerun()

        # --- MODUL: SYSTEM ---
        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("NEON FÄRG:", st.session_state.accent_color)
            if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
































