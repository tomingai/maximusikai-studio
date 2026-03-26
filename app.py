import streamlit as st
import replicate
import os
import random

# --- 1. DATA & SPRÅK ---
TEXTS = {
    "Svenska": {
        "title": "MAXIMUSIK AI", "synth": "🪄 SYNTH", "audio": "🎧 AUDIO", 
        "library": "📚 ARKIV", "engine": "🖼 ENGINE", "system": "⚙️ SYSTEM",
        "prompt": "VISION:", "execute": "EXEKVERA", "sync": "AUTO-TEXT AKTIVERAD"
    },
    "English": {
        "title": "MAXIMUSIK AI", "synth": "🪄 SYNTH", "audio": "🎧 AUDIO", 
        "library": "📚 LIBRARY", "engine": "🖼 ENGINE", "system": "⚙️ SYSTEM",
        "prompt": "VISION:", "execute": "EXECUTE", "sync": "AUTO-TEXT ACTIVATED"
    }
}

def get_url(res):
    if isinstance(res, list) and len(res) > 0: return str(res[0])
    return str(res)

def get_auto_color(style):
    colors = {
        "Cyberpunk Neon": "#ff00ff", "Deep Space": "#00d2ff", 
        "Retro Synthwave": "#f0ff00", "Dark Tech": "#00ff41", 
        "Ethereal Dream": "#ff7700", "None": "#00f2ff"
    }
    return colors.get(style, "#00f2ff")

# --- 2. CONFIG & SESSION ---
st.set_page_config(page_title="MAXIMUSIK AI", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

states = {
    "page": "DESKTOP", "lang": "Svenska", "accent_color": "#00f2ff",
    "wallpaper": "https://images.unsplash.com",
    "library": [], "res_img": None, "input_text": ""
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

T = TEXTS[st.session_state.lang]

# --- 3. DYNAMISK TEXT-ENGINE (CSS) ---
def apply_ui():
    accent = st.session_state.accent_color
    st.markdown(f"""
        <style>
        /* Bakgrundsmotor */
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.8)), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; background-attachment: fixed !important;
        }}
        [data-testid="stHeader"], .main {{ background: transparent !important; }}
        
        /* ALL TEXT AUTO-FÄRG & GLÖD */
        h1, h2, h3, p, label, .stMarkdown, .stSelectbox label, .stTextArea label, .stTextInput label {{
            color: {accent} !important;
            text-shadow: 0 0 15px {accent}44 !important;
            font-family: 'Courier New', monospace !important;
        }}
        
        /* Fönster-design */
        .window-box {{
            background: rgba(0, 5, 12, 0.95); backdrop-filter: blur(50px);
            border: 2px solid {accent}22; border-radius: 40px; padding: 40px;
            box-shadow: 0 0 60px {accent}11;
        }}

        /* Knappar med synkad textfärg */
        .stButton > button {{
            background: rgba(0,0,0,0.6) !important; border: 1px solid {accent}44 !important;
            color: {accent} !important; border-radius: 20px !important; height: 100px !important;
            font-weight: 900; text-transform: uppercase; letter-spacing: 4px;
            box-shadow: inset 0 0 10px {accent}22 !important;
        }}
        .stButton > button:hover {{ 
            border-color: {accent} !important; box-shadow: 0 0 40px {accent}44 !important; 
            color: white !important; background: {accent}22 !important;
        }}
        
        /* Inputs & Textareas */
        .stTextArea textarea, .stTextInput input {{
            background-color: rgba(0,0,0,0.5) !important;
            color: white !important; border: 1px solid {accent}33 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:20px; padding-top:15vh; font-size:4rem;'>{T['title']}</h1>", unsafe_allow_html=True)
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
        h1.markdown(f"<h2>// {st.session_state.page}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close_os"): st.session_state.page = "DESKTOP"; st.rerun()

        if st.session_state.page == "ENGINE":
            st.write(T['sync'])
            style = st.selectbox("STYLE PRESET:", ["None", "Cyberpunk Neon", "Deep Space", "Retro Synthwave", "Dark Tech", "Ethereal Dream"])
            ep = st.text_area(T['prompt'])
            if st.button(T['execute'], use_container_width=True):
                with st.spinner("Rewriting Reality..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"{style}, {ep}", "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = get_url(res)
                    st.session_state.accent_color = get_auto_color(style)
                    st.session_state.library.append({"type": "image", "url": st.session_state.wallpaper, "prompt": ep})
                    st.rerun()

        elif st.session_state.page == "SYNTH":
            p = st.text_area(T['prompt'])
            if st.button(T['execute'], use_container_width=True):
                with st.spinner("Neural Sync..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.res_img = get_url(res)
                    st.session_state.library.append({"type": "image", "url": st.session_state.res_img, "prompt": p})
                    st.rerun()
            if st.session_state.res_img: st.image(st.session_state.res_img)

        elif st.session_state.page == "LIBRARY":
            if not st.session_state.library: st.write("EMPTY_ARCHIVE")
            else:
                for idx, item in enumerate(reversed(st.session_state.library)):
                    with st.container():
                        st.write(f"PROMPT: {item['prompt']}")
                        if item['type'] == "image":
                            st.image(item['url'], width=600)
                            if st.button("SET BACKGROUND", key=f"bg_{idx}"):
                                st.session_state.wallpaper = item['url']; st.rerun()
                        st.markdown("---")

        elif st.session_state.page == "SYSTEM":
            st.session_state.lang = st.radio("LANG:", ["Svenska", "English"])
            st.session_state.accent_color = st.color_picker("MANUAL ACCENT:", st.session_state.accent_color)
            if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)



























