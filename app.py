import streamlit as st
import replicate
import os
import random

# --- 1. PROMPT MOTOR ---
def get_random_prompt(mode="IMAGE"):
    img_prompts = ["Cyberpunk city, neon rain", "Deep space nebula, gold dust", "Ancient forest, bioluminescent plants", "Retro robot DJ, synthwave", "Floating island, waterfalls, 8k"]
    audio_prompts = ["Dark techno, 128bpm, heavy bass", "Space ambient, ethereal pads", "Cyberpunk industrial beat", "Lofi hip hop, chill rainy night", "Epic cinematic orchestral hybrid"]
    return random.choice(audio_prompts) if mode == "AUDIO" else random.choice(img_prompts)

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
        h1, h2, h3, p, label {{ color: {accent} !important; text-shadow: 0 0 10px {accent}55 !important; font-family: monospace !important; }}
        .window-box {{ background: rgba(0, 5, 12, 0.9); backdrop-filter: blur(50px); border: 1px solid {accent}33; border-radius: 30px; padding: 30px; }}
        
        /* Arkiv-kort styling */
        .archive-card {{
            border: 1px solid {accent}22;
            background: rgba(255,255,255,0.03);
            border-radius: 15px;
            padding: 15px;
            margin-bottom: 20px;
        }}
        
        .stButton > button {{ background: rgba(0,0,0,0.5) !important; border: 1px solid {accent}33 !important; color: {accent} !important; border-radius: 12px !important; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:20px; padding-top:10vh; font-size:3.5rem;'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
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
        if h2.button("✕", key="close_win"): st.session_state.page = "DESKTOP"; st.rerun()

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
                    st.rerun()
            if st.session_state.library and st.session_state.library[-1]['type'] == "image":
                st.image(st.session_state.library[-1]['url'], width=500)

        # --- AUDIO ---
        elif st.session_state.page == "AUDIO":
            if st.button("🎲 SLUMPA BEAT"): st.session_state.last_synth = get_random_prompt("AUDIO"); st.rerun()
            ap = st.text_input("BESKRIV LJUD:", value=st.session_state.last_synth)
            if st.button("GENERATE AUDIO", use_container_width=True):
                with st.spinner("Composing..."):
                    res = replicate.run("meta/musicgen:b05b39c7", input={"prompt": ap, "duration": 8})
                    st.session_state.library.append({"type": "audio", "url": res, "prompt": ap})
                    st.rerun()
            if st.session_state.library and st.session_state.library[-1]['type'] == "audio":
                st.audio(st.session_state.library[-1]['url'])

        # --- ARKIV (TEXT BREDVID MEDIA) ---
        elif st.session_state.page == "LIBRARY":
            if not st.session_state.library: st.write("ARKIVET ÄR TOMT")
            else:
                for idx, item in enumerate(reversed(st.session_state.library)):
                    # Skapar en container per objekt för snyggare layout
                    st.markdown('<div class="archive-card">', unsafe_allow_html=True)
                    col_media, col_info = st.columns([0.6, 0.4])
                    
                    with col_media:
                        if item['type'] == "image": st.image(item['url'], use_container_width=True)
                        else: st.audio(item['url'])
                    
                    with col_info:
                        st.markdown(f"**PROMPT:**\n*{item['prompt']}*")
                        st.write(f"TYPE: {item['type'].upper()}")
                        
                        # Kontrollknappar på rad
                        btn_c1, btn_c2, btn_c3 = st.columns(3)
                        with btn_c1:
                            if st.button("🗑", key=f"del_{idx}"):
                                st.session_state.library.pop(-(idx+1))
                                st.rerun()
                        with btn_c2:
                            if item['type'] == "image":
                                if st.button("🖼", key=f"bg_{idx}", help="Sätt som bakgrund"):
                                    st.session_state.wallpaper = item['url']; st.rerun()
                        with btn_c3:
                            st.markdown(f'<a href="{item["url"]}" download target="_blank" style="text-decoration:none;">💾</a>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

        # --- ENGINE & SYSTEM ---
        elif st.session_state.page == "ENGINE":
            st.session_state.brightness = st.slider("LJUSSTYRKA", 0.0, 1.0, st.session_state.brightness)
            if st.button("🎲 SLUMPA MILJÖ"): st.session_state.last_synth = get_random_prompt("IMAGE"); st.rerun()
            ep = st.text_area("MILJÖ-PROMPT:", value=st.session_state.last_synth)
            if st.button("UPDATE REALITY", use_container_width=True):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                st.session_state.wallpaper = get_url(res)
                st.session_state.library.append({"type": "image", "url": st.session_state.wallpaper, "prompt": ep})
                st.rerun()

        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("NEON:", st.session_state.accent_color)
            if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)






























