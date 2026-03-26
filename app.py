import streamlit as st
import replicate
import os
import random

# --- 1. SPRÅK-DATA ---
TEXTS = {
    "Svenska": {
        "title": "MAXIMUSIK AI",
        "synth": "🪄 SYNTH",
        "audio": "🎧 AUDIO",
        "library": "📚 ARKIV",
        "engine": "🖼 ENGINE",
        "system": "⚙️ SYSTEM",
        "prompt_label": "VAD SKALL VI SKAPA?",
        "execute": "STARTA NEURAL SYNTH",
        "random": "🎲 SLUMPA",
        "bg_set": "SÄTT SOM BAKGRUND",
        "empty_lib": "Arkivet är tomt.",
        "lang_label": "VÄLJ SPRÅK:",
        "accent_label": "UI ACCENT FÄRG:",
        "reset": "HARD RESET (RENSA ALLT)"
    },
    "English": {
        "title": "MAXIMUSIK AI",
        "synth": "🪄 SYNTH",
        "audio": "🎧 AUDIO",
        "library": "📚 LIBRARY",
        "engine": "🖼 ENGINE",
        "system": "⚙️ SYSTEM",
        "prompt_label": "WHAT SHALL WE CREATE?",
        "execute": "EXECUTE NEURAL SYNTH",
        "random": "🎲 RANDOM",
        "bg_set": "SET AS BACKGROUND",
        "empty_lib": "The library is empty.",
        "lang_label": "SELECT LANGUAGE:",
        "accent_label": "UI ACCENT COLOR:",
        "reset": "HARD RESET (CLEAR ALL)"
    }
}

# --- 2. HJÄLPFUNKTIONER ---
def get_url(res):
    if isinstance(res, list) and len(res) > 0:
        return str(res[0])
    return str(res)

def enhance_prompt(user_input):
    styles = ["8k cinematic", "hyper-detailed", "neon lighting", "volumetric fog", "masterpiece", "synthwave"]
    if not user_input:
        subjects = ["Cyberpunk city", "Deep space nebula", "Interstellar portal", "Android DJ"]
        user_input = random.choice(subjects)
    return f"{user_input}, {', '.join(random.sample(styles, 3))}"

# --- 3. CONFIG & SESSION ---
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

# --- 4. CSS ENGINE ---
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
            background: rgba(0, 5, 12, 0.95); backdrop-filter: blur(40px);
            border: 1px solid {accent}44; border-radius: 40px; padding: 40px; color: white;
        }}
        .stButton > button {{
            background: rgba(255, 255, 255, 0.05) !important; border: 1px solid {accent}33 !important;
            color: white !important; border-radius: 20px !important; height: 100px !important; transition: 0.4s !important;
        }}
        .stButton > button:hover {{ border-color: {accent} !important; box-shadow: 0 0 30px {accent}44 !important; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 5. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; color:white; letter-spacing:15px; padding-top:10vh; text-shadow: 0 0 20px {st.session_state.accent_color};'>{T['title']}</h1>", unsafe_allow_html=True)
    cols = st.columns(5)
    apps = [(T['synth'], "SYNTH"), (T['audio'], "AUDIO"), (T['library'], "LIBRARY"), (T['engine'], "ENGINE"), (T['system'], "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        with cols[i]:
            if st.button(label, use_container_width=True):
                st.session_state.page = target; st.rerun()

# --- 6. WINDOWS ---
else:
    _, win_col, _ = st.columns([0.05, 0.9, 0.05])
    with win_col:
        st.markdown('<div class="window-box">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.title(f"// {st.session_state.page}")
        if h2.button("✕"): st.session_state.page = "DESKTOP"; st.rerun()

        if st.session_state.page == "SYNTH":
            col1, col2 = st.columns([0.8, 0.2])
            with col2:
                if st.button(T['random']): st.session_state.input_text = enhance_prompt(""); st.rerun()
            u_input = col1.text_area(T['prompt_label'], value=st.session_state.input_text)
            if st.button(T['execute'], use_container_width=True):
                enhanced = enhance_prompt(u_input)
                with st.spinner("Syncing..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": enhanced})
                    url = get_url(res)
                    st.session_state.res_img = url
                    st.session_state.library.append({"type": "image", "url": url, "prompt": enhanced})
                    st.rerun()
            if st.session_state.res_img: st.image(st.session_state.res_img)

        elif st.session_state.page == "AUDIO":
            ap = st.text_input(T['prompt_label'], value=st.session_state.input_text)
            if st.button(T['execute'], use_container_width=True):
                with st.spinner("Composing..."):
                    res = replicate.run("meta/musicgen:b05b39c7", input={"prompt": ap or "Space ambient", "duration": 10})
                    st.session_state.res_audio = res
                    st.session_state.library.append({"type": "audio", "url": res, "prompt": ap})
                    st.rerun()
            if st.session_state.res_audio: st.audio(st.session_state.res_audio)

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

        elif st.session_state.page == "SYSTEM":
            st.session_state.lang = st.radio(T['lang_label'], ["Svenska", "English"], index=0 if st.session_state.lang == "Svenska" else 1)
            st.session_state.accent_color = st.color_picker(T['accent_label'], st.session_state.accent_color)
            if st.button(T['reset']): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)



























