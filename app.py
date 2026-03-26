import streamlit as st
import replicate
import os

# --- 1. CONFIG & INITIALIZATION ---
st.set_page_config(page_title="MAXIMUSIK AI", layout="wide", initial_sidebar_state="collapsed")

# API-nyckel hantering
if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session State för att hålla reda på fönster och media
if "active_window" not in st.session_state: st.session_state.active_window = None
if "wallpaper" not in st.session_state: 
    st.session_state.wallpaper = "https://images.unsplash.com"
if "accent_color" not in st.session_state: st.session_state.accent_color = "#00f2ff"
if "synth_res" not in st.session_state: st.session_state.synth_res = None
if "audio_res" not in st.session_state: st.session_state.audio_res = None
if "video_res" not in st.session_state: st.session_state.video_res = None

# --- 2. THE SPACE OS ENGINE (CSS) ---
def apply_ui():
    accent = st.session_state.accent_color
    st.markdown(f"""
        <style>
        /* Bakgrund för hela OS:et */
        .stAppViewContainer {{
            background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6)), 
                              url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; 
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        
        .main, .stAppHeader, .stAppViewBlockContainer {{ background: transparent !important; }}

        /* Titel */
        .os-title {{
            position: fixed; top: 40px; left: 50px;
            color: white; font-size: 1.8rem; font-weight: 900;
            letter-spacing: 10px; text-shadow: 0 0 20px {accent};
            font-family: monospace; z-index: 100;
        }}

        /* GIGANTISKA GLASS-IKONER */
        div[data-testid="stButton"] > button {{
            width: 180px !important; height: 180px !important;
            border-radius: 40px !important; 
            border: 1px solid {accent}44 !important;
            background-color: rgba(0, 0, 0, 0.5) !important;
            background-size: cover !important;
            background-position: center !important;
            color: transparent !important;
            backdrop-filter: blur(10px) !important;
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
        }}

        div[data-testid="stButton"] > button:hover {{
            transform: scale(1.1) translateY(-10px) !important;
            border-color: {accent} !important;
            box-shadow: 0 0 50px {accent}66 !important;
        }}

        /* IKON-BILDER (Träffar rätt kolumn) */
        div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stHorizontalBlock"] > div:nth-child(5) button {{ background-image: url('https://images.unsplash.com') !important; }}

        .label {{ 
            text-align: center; color: {accent}; font-family: monospace; 
            font-size: 0.9rem; margin-top: 15px; letter-spacing: 3px; 
            text-transform: uppercase; font-weight: bold;
        }}

        /* Fönster-design */
        .window-content {{
            background: rgba(0, 5, 12, 0.92) !important;
            backdrop-filter: blur(40px);
            border: 1px solid {accent}33;
            border-radius: 40px;
            padding: 40px;
            color: white;
            box-shadow: 0 50px 150px rgba(0,0,0,0.9);
        }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP VIEW ---
if st.session_state.active_window is None:
    st.markdown("<div class='os-title'>MAXIMUSIK AI</div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 25vh;'></div>", unsafe_allow_html=True)
    
    cols = st.columns(5)
    apps = [("SYNTH", "s"), ("AUDIO", "a"), ("VIDEO", "v"), ("ENGINE", "wp"), ("SYSTEM", "sys")]
    
    for i, (name, key) in enumerate(apps):
        with cols[i]:
            if st.button(name, key=key):
                st.session_state.active_window = name
                st.rerun()
            st.markdown(f'<p class="label">{name}</p>', unsafe_allow_html=True)

# --- 4. WINDOW INTERFACE ---
else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, win_col, _ = st.columns([0.1, 0.8, 0.1])
    
    with win_col:
        st.markdown('<div class="window-content">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2 style='margin:0; font-family:monospace; color:{st.session_state.accent_color};'>// {st.session_state.active_window}</h2>", unsafe_allow_html=True)
        if h2.button("✕", key="close"):
            st.session_state.active_window = None
            st.rerun()
        
        st.markdown(f"<hr style='border:1px solid {st.session_state.accent_color}22; margin:20px 0;'>", unsafe_allow_html=True)

        # -- SYNTH (Bilder) --
        if st.session_state.active_window == "SYNTH":
            p = st.text_area("PROMPT:", "Cyberpunk explorer standing on a moon, cinematic lighting, 8k")
            if st.button("EXECUTE SYNTHESIS", use_container_width=True):
                with st.status("GENERATING..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.synth_res = res
                st.rerun()
            if st.session_state.synth_res:
                st.image(st.session_state.synth_res)

        # -- AUDIO (Musik) --
        elif st.session_state.active_window == "AUDIO":
            ap = st.text_input("SONIC COMMAND:", "Space ambient with deep bass pulses")
            dur = st.slider("SECONDS", 5, 20, 10)
            if st.button("RENDER AUDIO", use_container_width=True):
                with st.status("COMPOSING..."):
                    res = replicate.run("facebookresearch/musicgen:7b539958", 
                                       input={"prompt": ap, "duration": dur})
                    st.session_state.audio_res = res
                st.rerun()
            if st.session_state.audio_res:
                st.audio(st.session_state.audio_res)

        # -- VIDEO (Animering) --
        elif st.session_state.active_window == "VIDEO":
            st.info("Klistra in en bild-URL (eller använd en från SYNTH) för att animera.")
            v_url = st.text_input("SOURCE IMAGE URL:", st.session_state.synth_res if st.session_state.synth_res else "")
            if st.button("START ANIMATION", use_container_width=True):
                if v_url:
                    with st.status("RENDERING..."):
                        res = replicate.run("stability-ai/stable-video-diffusion:3f04571e", 
                                           input={"input_image": v_url})
                        st.session_state.video_res = res
                    st.rerun()
            if st.session_state.video_res:
                st.video(st.session_state.video_res)

        # -- ENGINE (Wallpaper) --
        elif st.session_state.active_window == "ENGINE":
            wp_p = st.text_area("NEW ENVIRONMENT COMMAND:", "Abstract hyperspace tunnel, neon blue and violet")
            if st.button("SYNC WALLPAPER", use_container_width=True):
                with st.status("UPDATING REALITY..."):
                    res = replicate.run("black-forest-labs/flux-schnell", 
                                       input={"prompt": wp_p, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = res
                st.rerun()

        # -- SYSTEM --
        elif st.session_state.active_window == "SYSTEM":
            st.session_state.accent_color = st.color_picker("UI ACCENT COLOR", st.session_state.accent_color)
            if st.button("HARD RESET"):
                for key in st.session_state.keys(): del st.session_state[key]
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)























