import streamlit as st
import replicate
import os

# --- 1. CONFIG & SESSION ---
st.set_page_config(page_title="MAXIMUSIK AI", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# State Management
states = {
    "active_window": None,
    "wallpaper": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "synth_res": None,
    "audio_res": None,
    "video_res": None
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 2. DESIGN (SPACE OS ENGINE) ---
def apply_ui():
    accent = st.session_state.accent_color
    st.markdown(f"""
        <style>
        .stAppViewContainer {{
            background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6)), 
                              url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; 
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        
        .main, .stAppHeader, .stAppViewBlockContainer {{ background: transparent !important; }}

        .os-title {{
            position: fixed; top: 30px; left: 40px;
            color: white; font-size: 1.5rem; font-weight: 900;
            letter-spacing: 8px; text-shadow: 0 0 15px {accent};
            font-family: 'Courier New', monospace; z-index: 10;
        }}

        /* IKONER */
        div[data-testid="stButton"] > button {{
            width: 180px !important; height: 180px !important;
            border-radius: 35px !important; 
            border: 1px solid {accent}44 !important;
            background: rgba(0, 0, 0, 0.4) !important;
            backdrop-filter: blur(10px) !important;
            transition: 0.4s ease-in-out !important;
        }}
        
        div[data-testid="stButton"] > button:hover {{
            transform: translateY(-10px) scale(1.05) !important;
            border-color: {accent} !important;
            box-shadow: 0 0 40px {accent}55 !important;
        }}

        /* IKON-BILDER */
        div[data-testid="stButton"] > button[key="s"] {{ background-image: url('https://images.unsplash.com') !important; background-size: cover; }}
        div[data-testid="stButton"] > button[key="a"] {{ background-image: url('https://images.unsplash.com') !important; background-size: cover; }}
        div[data-testid="stButton"] > button[key="v"] {{ background-image: url('https://images.unsplash.com') !important; background-size: cover; }}
        div[data-testid="stButton"] > button[key="wp"] {{ background-image: url('https://images.unsplash.com') !important; background-size: cover; }}
        div[data-testid="stButton"] > button[key="sys"] {{ background-image: url('https://images.unsplash.com') !important; background-size: cover; }}

        div[data-testid="stButton"] > button p {{ display: none !important; }}

        .window-content {{
            background: rgba(5, 10, 15, 0.9) !important;
            backdrop-filter: blur(30px);
            border: 1px solid {accent}33;
            border-radius: 30px;
            padding: 30px;
            color: white;
            box-shadow: 0 40px 100px rgba(0,0,0,0.9);
        }}
        
        .label {{ text-align: center; color: {accent}; font-family: monospace; font-size: 0.8rem; margin-top: 10px; letter-spacing: 2px; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP VIEW ---
if st.session_state.active_window is None:
    st.markdown("<div class='os-title'>MAXIMUSIK AI v2.0</div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 25vh;'></div>", unsafe_allow_html=True)
    
    cols = st.columns(5)
    apps = [
        ("SYNTH", "s"), ("AUDIO", "a"), ("VIDEO", "v"), 
        ("ENGINE", "wp"), ("SYSTEM", "sys")
    ]
    
    for i, (name, key) in enumerate(apps):
        with cols[i]:
            if st.button(name, key=key):
                st.session_state.active_window = name
                st.rerun()
            st.markdown(f'<p class="label">{name}</p>', unsafe_allow_html=True)

# --- 4. WINDOW INTERFACE ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.1, 1, 0.1])
    
    with win_col:
        st.markdown('<div class="window-content">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='margin:0; font-family:monospace; color:{st.session_state.accent_color};'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown(f"<hr style='border:0.5px solid {st.session_state.accent_color}33; margin:20px 0;'>", unsafe_allow_html=True)

        # -- MODUL: SYNTH (IMAGE) --
        if st.session_state.active_window == "SYNTH":
            p = st.text_area("VISUAL_PROMPT:", "Cyberpunk city in space, neon 8k")
            if st.button("GENERATE IMAGE", use_container_width=True):
                with st.spinner("SYNTHESIZING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res[0]
            if st.session_state.synth_res:
                st.image(st.session_state.synth_res, caption="Generated Output")

        # -- MODUL: AUDIO (MUSIC) --
        elif st.session_state.active_window == "AUDIO":
            ap = st.text_input("SONIC_PROMPT:", "Dark ambient techno, 128bpm")
            dur = st.slider("DURATION (SEC)", 5, 20, 8)
            if st.button("COMPOSE MUSIC", use_container_width=True):
                with st.spinner("COMPOSING..."):
                    res = replicate.run("facebookresearch/musicgen:7a76a6d6", 
                                       input={"prompt": ap, "duration": dur})
                    st.session_state.audio_res = res
            if st.session_state.audio_res:
                st.audio(st.session_state.audio_res)

        # -- MODUL: VIDEO (ANIMATION) --
        elif st.session_state.active_window == "VIDEO":
            st.info("Ladda upp en bild för att animera den till video.")
            img_url = st.text_input("IMAGE_URL:", st.session_state.synth_res if st.session_state.synth_res else "")
            if st.button("ANIMATE", use_container_width=True):
                if img_url:
                    with st.spinner("RENDERING VIDEO..."):
                        res = replicate.run("stability-ai/stable-video-diffusion:3f04571e", 
                                           input={"input_image": img_url})
                        st.session_state.video_res = res[0]
                else: st.warning("Need image source first.")
            if st.session_state.video_res:
                st.video(st.session_state.video_res)

        # -- MODUL: ENGINE (WALLPAPER) --
        elif st.session_state.active_window == "ENGINE":
            bg_p = st.text_area("NEW_ENVIRONMENT:", "Nebula explosion, deep purple and teal")
            if st.button("REWRITE REALITY", use_container_width=True):
                with st.spinner("UPDATING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", 
                                       input={"prompt": bg_p, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = res[0]
                st.rerun()

        # -- MODUL: SYSTEM --
        elif st.session_state.active_window == "SYSTEM":
            st.session_state.accent_color = st.color_picker("ACCENT_COLOR", st.session_state.accent_color)
            if st.button("RESET SYSTEM"):
                for key in st.session_state.keys(): del st.session_state[key]
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)






















