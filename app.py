import streamlit as st
import replicate
import os
import random

# --- 1. SPRÅK-DATA & PROMPT ENGINE ---
TEXTS = {
    "Svenska": {
        "title": "MAXIMUSIK AI",
        "synth": "🪄 SYNTH",
        "audio": "🎧 AUDIO",
        "library": "📚 ARKIV",
        "engine": "🖼 ENGINE",
        "system": "⚙️ SYSTEM",
        "prompt_label": "BESKRIV DIN VISION:",
        "execute": "EXEKVERA",
        "random": "🎲 SLUMPA",
        "bg_set": "SÄTT SOM BAKGRUND",
        "empty_lib": "Arkivet är tomt.",
        "lang_label": "VÄLJ SPRÅK:",
        "accent_label": "UI ACCENT FÄRG:",
        "reset": "HARD RESET (RENSA ALLT)",
        "engine_sub": "MILJÖ-MOTOR (ENVIRONMENT ENGINE)",
        "format": "SKÄRMFORMAT:",
        "style": "VISUELL STIL:",
        "sync_ui": "AUTO-SYNC UI FÄRG"
    },
    "English": {
        "title": "MAXIMUSIK AI",
        "synth": "🪄 SYNTH",
        "audio": "🎧 AUDIO",
        "library": "📚 LIBRARY",
        "engine": "🖼 ENGINE",
        "system": "⚙️ SYSTEM",
        "prompt_label": "DESCRIBE YOUR VISION:",
        "execute": "EXECUTE",
        "random": "🎲 RANDOM",
        "bg_set": "SET AS BACKGROUND",
        "empty_lib": "The library is empty.",
        "lang_label": "SELECT LANGUAGE:",
        "accent_label": "UI ACCENT COLOR:",
        "reset": "HARD RESET (CLEAR ALL)",
        "engine_sub": "SYSTEM ENVIRONMENT ENGINE",
        "format": "SCREEN FORMAT:",
        "style": "VISUAL STYLE:",
        "sync_ui": "AUTO-SYNC UI COLOR"
    }
}

def get_url(res):
    """Extraherar URL från Replicate-listor"""
    if isinstance(res, list) and len(res) > 0:
        return str(res[0])
    return str(res)

def enhance_prompt(user_input):
    """Gör korta prompts till avancerade 8k-prompts"""
    styles = ["8k cinematic", "hyper-detailed", "neon lighting", "volumetric fog", "masterpiece", "synthwave"]
    if not user_input:
        subjects = ["Cyberpunk city", "Deep space nebula", "Interstellar portal", "Android DJ", "Neon rain forest"]
        user_input = random.choice(subjects)
    return f"{user_input}, {', '.join(random.sample(styles, 3))}"

# --- 2. CONFIG & SESSION ---
st.set_page_config(page_title="MAXIMUSIK AI OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

states = {
    "page": "DESKTOP",
    "lang": "Svenska",
    "wallpaper": "https://images.unsplash.com",
    "library": [],
    "res_img": None,
    "res_audio": None,
    "input_text": "",
    "accent_color": "#00f2ff"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

T = TEXTS[st.session_state.lang]

# --- 3. CSS UI ENGINE ---
def apply_ui():
    accent = st.session_state.accent_color
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
        }}
        [data-testid="stHeader"], .main {{ background: transparent !important; }}
        .window-box {{
            background: rgba(0, 5, 12, 0.93); backdrop-filter: blur(40px);
            border: 1px solid {accent}44; border-radius: 40px; padding: 40px; color: white;
            box-shadow: 0 40px 100px rgba(0,0,0,0.8);
        }}
        .stButton > button {{
            background: rgba(255, 255, 255, 0.05) !important; border: 1px solid {accent}33 !important;
            color: white !important; border-radius: 20px !important; height: 100px !important; transition: 0.4s !important;
            font-weight: bold; letter-spacing: 2px;
        }}
        .stButton > button:hover {{ border-color: {accent} !important; box-shadow: 0 0 30px {accent}44 !important; transform: scale(1.05); }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; color:white; letter-spacing:15px; padding-top:10vh; text-shadow: 0 0 20px {st.session_state.accent_color};'>{T['title']}</h1>", unsafe_allow_html=True)
    st.write("<br><br>", unsafe_allow_html=True)
    cols = st.columns(5)
    apps = [(T['synth'], "SYNTH"), (T['audio'], "AUDIO"), (T['library'], "LIBRARY"), (T['engine'], "ENGINE"), (T['system'], "SYSTEM")]
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
        h1.title(f"// {st.session_state.page}")
        if h2.button("✕"): st.session_state.page = "DESKTOP"; st.rerun()

        # --- MODUL: SYNTH ---
        if st.session_state.page == "SYNTH":
            col1, col2 = st.columns([0.8, 0.2])
            with col2:
                if st.button(T['random']): st.session_state.input_text = enhance_prompt(""); st.rerun()
            u_input = col1.text_area(T['prompt_label'], value=st.session_state.input_text)
            if st.button(T['execute'], use_container_width=True):
                enhanced = enhance_prompt(u_input)
                with st.spinner("Neural Syncing..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": enhanced})
                    url = get_url(res)
                    st.session_state.res_img = url
                    st.session_state.library.append({"type": "image", "url": url, "prompt": enhanced})
                    st.rerun()
            if st.session_state.res_img: st.image(st.session_state.res_img)

        # --- MODUL: AUDIO ---
        elif st.session_state.page == "AUDIO":
            ap = st.text_input(T['prompt_label'], value=st.session_state.input_text)
            if st.button(T['execute'], use_container_width=True):
                with st.spinner("Composing..."):
                    res = replicate.run("meta/musicgen:b05b39c7", input={"prompt": ap or "Cyberpunk ambient", "duration": 10})
                    st.session_state.res_audio = res
                    st.session_state.library.append({"type": "audio", "url": res, "prompt": ap})
                    st.rerun()
            if st.session_state.res_audio: st.audio(st.session_state.res_audio)

        # --- MODUL: LIBRARY ---
        elif st.session_state.page == "LIBRARY":
            if not st.session_state.library: st.info(T['empty_lib'])
            else:
                for idx, item in enumerate(reversed(st.session_state.library)):
                    with st.expander(f"{item['type'].upper()}: {item['prompt'][:30]}..."):
                        if item['type'] == "image":
                            st.image(item['url'], use_container_width=True)
                            if st.button(T['bg_set'], key=f"bg_{idx}"):
                                st.session_state.wallpaper = item['url']; st.rerun()
                        else: st.audio(item['url'])

        # --- MODUL: ENGINE (UTBYGGD) ---
        elif st.session_state.page == "ENGINE":
            st.subheader(T['engine_sub'])
            col_cfg, col_gen = st.columns([0.4, 0.6])
            with col_cfg:
                ratio = st.radio(T['format'], ["16:9", "9:16", "1:1"], horizontal=True)
                style_preset = st.selectbox(T['style'], ["None", "Cyberpunk Neon", "Deep Space", "Dark Tech", "Ethereal Dream"])
                sync_ui = st.checkbox(T['sync_ui'], value=True)
            with col_gen:
                ep = st.text_area(T['prompt_label'], value=st.session_state.input_text)
                if st.button(T['execute'], use_container_width=True):
                    final_p = f"{style_preset} style, {ep}" if style_preset != "None" else ep
                    enhanced = enhance_prompt(final_p)
                    with st.spinner("Rewriting Reality..."):
                        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": enhanced, "aspect_ratio": ratio})
                        url = get_url(res)
                        st.session_state.wallpaper = url
                        st.session_state.library.append({"type": "image", "url": url, "prompt": enhanced})
                        if sync_ui:
                            st.session_state.accent_color = "#ff00ff" if "Cyberpunk" in style_preset else "#00d2ff"
                        st.rerun()

        # --- MODUL: SYSTEM ---
        elif st.session_state.page == "SYSTEM":
            st.session_state.lang = st.radio(T['lang_label'], ["Svenska", "English"], index=0 if st.session_state.lang == "Svenska" else 1)
            st.session_state.accent_color = st.color_picker(T['accent_label'], st.session_state.accent_color)
            if st.button(T['reset']): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)



























