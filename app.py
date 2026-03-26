import streamlit as st
import replicate
import os
import random

# --- 1. PROMPT MOTOR (SLUMP FÖR ALLA KNAPPAR) ---
def get_random_prompt(mode="IMAGE"):
    img_prompts = ["Cyberpunk city, neon rain", "Deep space nebula, gold dust", "Ancient forest, bioluminescent plants", "Retro robot DJ, synthwave", "Floating island, waterfalls, 8k"]
    audio_prompts = ["Dark techno, 128bpm, heavy bass", "Space ambient, ethereal pads", "Cyberpunk industrial beat", "Lofi hip hop, chill rainy night", "Epic cinematic orchestral hybrid"]
    if mode == "AUDIO": return random.choice(audio_prompts)
    return random.choice(img_prompts)

# --- 2. CONFIG & SESSION ---
st.set_page_config(page_title="MAXIMUSIK AI OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "brightness": 0.5,
    "library": [],
    "last_synth": ""
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

def get_url(res):
    """Fixar AttributeError genom att alltid extrahera sträng-URL"""
    if isinstance(res, list) and len(res) > 0: return str(res[0])
    return str(res)

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
        h1, h2, h3, p, label {{ color: {accent} !important; text-shadow: 0 0 15px {accent}77 !important; font-family: monospace !important; }}
        .window-box {{ background: rgba(0, 5, 12, 0.9); backdrop-filter: blur(50px); border: 2px solid {accent}33; border-radius: 40px; padding: 40px; }}
        .stButton > button {{ background: rgba(0,0,0,0.6) !important; border: 1px solid {accent}44 !important; color: {accent} !important; border-radius: 20px !important; height: 70px !important; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:20px; padding-top:10vh; font-size:4rem;'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    cols = st.columns(5)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
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

        # --- SYNTH ---
        if st.session_state.page == "SYNTH":
            col_a, col_b = st.columns([0.8, 0.2])
            with col_b: 
                if st.button("🎲 SLUMPA"): st.session_state.last_synth = get_random_prompt("IMAGE"); st.rerun()
            p = col_a.text_area("BILD-PROMPT:", value=st.session_state.last_synth)
            if st.button("SYNTHESIZE", use_container_width=True):
                with st.spinner("Neural Sync..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    url = get_url(res)
                    st.session_state.library.append({"type": "image", "url": url, "prompt": p})
                    st.image(url)

        # --- AUDIO ---
        elif st.session_state.page == "AUDIO":
            if st.button("🎲 SLUMPA BEAT"): st.session_state.last_synth = get_random_prompt("AUDIO"); st.rerun()
            ap = st.text_input("BESKRIV LJUD:", value=st.session_state.last_synth)
            if st.button("GENERATE AUDIO", use_container_width=True):
                with st.spinner("Composing..."):
                    res = replicate.run("meta/musicgen:b05b39c7", input={"prompt": ap, "duration": 10})
                    st.session_state.library.append({"type": "audio", "url": res, "prompt": ap})
                    st.audio(res)

        # --- ARKIV (MED RADERA-FUNKTION) ---
        elif st.session_state.page == "LIBRARY":
            if not st.session_state.library: st.write("ARKIVET ÄR TOMT")
            else:
                for idx, item in enumerate(st.session_state.library):
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        if item['type'] == "image": st.image(item['url'], width=300)
                        else: st.audio(item['url'])
                    with col2:
                        if st.button("🗑 RADERA", key=f"del_{idx}"):
                            st.session_state.library.pop(idx)
                            st.rerun()
                        if item['type'] == "image":
                            if st.button("🖼 BG", key=f"bg_{idx}"):
                                st.session_state.wallpaper = item['url']; st.rerun()

        # --- ENGINE ---
        elif st.session_state.page == "ENGINE":
            if st.button("🎲 SLUMPA MILJÖ"): st.session_state.last_synth = get_random_prompt("IMAGE"); st.rerun()
            ep = st.text_area("MILJÖ-PROMPT:", value=st.session_state.last_synth)
            if st.button("UPDATE REALITY"):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                st.session_state.wallpaper = get_url(res)
                st.session_state.library.append({"type": "image", "url": st.session_state.wallpaper, "prompt": ep})
                st.rerun()

        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("NEON:", st.session_state.accent_color)
            if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)





























