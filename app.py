import streamlit as st
import replicate
import os

# --- 1. CONFIG & API ---
st.set_page_config(page_title="MAXIMUSIK AI OS", layout="wide", initial_sidebar_state="collapsed")

# Hämtar token
replicate_api_token = st.secrets.get("REPLICATE_API_TOKEN") or os.environ.get("REPLICATE_API_TOKEN")
if not replicate_api_token:
    st.error("API-nyckel saknas! Lägg till REPLICATE_API_TOKEN i Streamlit Secrets.")
    st.stop()
os.environ["REPLICATE_API_TOKEN"] = replicate_api_token

# Session States
if "page" not in st.session_state: st.session_state.page = "DESKTOP"
if "wallpaper" not in st.session_state: st.session_state.wallpaper = "https://images.unsplash.com"
if "res_img" not in st.session_state: st.session_state.res_img = None
if "res_audio" not in st.session_state: st.session_state.res_audio = None

# --- 2. CSS ENGINE ---
def apply_ui():
    accent = "#00f2ff"
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        [data-testid="stHeader"], .main {{ background: transparent !important; }}
        .window-box {{
            background: rgba(0, 5, 10, 0.9);
            backdrop-filter: blur(30px);
            border: 1px solid {accent}44;
            border-radius: 35px;
            padding: 40px;
            color: white;
            box-shadow: 0 40px 80px rgba(0,0,0,0.8);
        }}
        .stButton > button {{
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid {accent}33 !important;
            color: white !important;
            border-radius: 20px !important;
            height: 80px !important;
            font-weight: bold !important;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown("<h1 style='text-align:center; color:white; letter-spacing:15px; padding-top:10vh;'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.write("<br><br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🪄\nSYNTH", use_container_width=True): st.session_state.page = "SYNTH"; st.rerun()
    with c2:
        if st.button("🎧\nAUDIO", use_container_width=True): st.session_state.page = "AUDIO"; st.rerun()
    with c3:
        if st.button("🎬\nVIDEO", use_container_width=True): st.session_state.page = "VIDEO"; st.rerun()
    with c4:
        if st.button("🖼\nENGINE", use_container_width=True): st.session_state.page = "ENGINE"; st.rerun()

# --- 4. WINDOWS ---
else:
    _, win_col, _ = st.columns([0.1, 0.8, 0.1])
    with win_col:
        st.markdown('<div class="window-box">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.title(f"// {st.session_state.page}")
        if h2.button("✕"):
            st.session_state.page = "DESKTOP"; st.rerun()

        # --- SYNTH (IMAGE) ---
        if st.session_state.page == "SYNTH":
            p = st.text_area("PROMPT:", "Cyberpunk city, neon lights, 8k")
            if st.button("GENERATE IMAGE"):
                with st.spinner("Processing..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.res_img = res; st.rerun()
            if st.session_state.res_img:
                st.image(st.session_state.res_img)

        # --- AUDIO (MUSIC) - FIXAD FÖR 422 ERROR ---
        elif st.session_state.page == "AUDIO":
            ap = st.text_input("SONIC PROMPT:", "Dark techno beat with heavy bass")
            dur = st.slider("DURATION", 5, 15, 8)
            if st.button("GENERATE AUDIO"):
                try:
                    with st.spinner("Composing..."):
                        # Vi använder den mest stabila MusicGen-modellen på Replicate just nu
                        res = replicate.run(
                            "facebookresearch/musicgen:7a76a6d6", 
                            input={"prompt": ap, "duration": dur}
                        )
                        st.session_state.res_audio = res; st.rerun()
                except Exception as e:
                    st.warning("Första försöket misslyckades. Testar reserv-server...")
                    try:
                        # Fallback till den universella pathen om hashen ovan dött
                        res = replicate.run(
                            "meta/musicgen", 
                            input={"prompt": ap, "duration": dur}
                        )
                        st.session_state.res_audio = res; st.rerun()
                    except Exception as e2:
                        st.error(f"Kunde inte generera ljud: {e2}")

            if st.session_state.res_audio:
                st.audio(st.session_state.res_audio)

        # --- VIDEO ---
        elif st.session_state.page == "VIDEO":
            if st.session_state.res_img:
                st.image(st.session_state.res_img, width=300)
                if st.button("ANIMATE"):
                    with st.spinner("Rendering..."):
                        res = replicate.run("stability-ai/stable-video-diffusion:3f04571e", input={"input_image": st.session_state.res_img})
                        st.video(res)
            else:
                st.warning("Skapa en bild i SYNTH först!")

        # --- ENGINE ---
        elif st.session_state.page == "ENGINE":
            wp_p = st.text_input("PROMPT FOR WALLPAPER:", "Cosmic nebula, deep purple")
            if st.button("GENERATE WALLPAPER"):
                with st.spinner("Updating..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": wp_p, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = res; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

























