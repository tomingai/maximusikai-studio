import streamlit as st
import replicate
import os

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="MAXIMUSIK AI OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session States
if "page" not in st.session_state: st.session_state.page = "DESKTOP"
if "wallpaper" not in st.session_state: st.session_state.wallpaper = "https://images.unsplash.com"
if "res_img" not in st.session_state: st.session_state.res_img = None

# --- 2. ADVANCED CSS ENGINE ---
def apply_custom_styles():
    accent = "#00f2ff"
    st.markdown(f"""
        <style>
        /* Bakgrundsmotorn */
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        [data-testid="stHeader"], .main {{ background: transparent !important; }}

        /* Glas-fönster för moduler */
        .window-box {{
            background: rgba(0, 8, 15, 0.85);
            backdrop-filter: blur(30px);
            border: 1px solid {accent}44;
            border-radius: 40px;
            padding: 40px;
            box-shadow: 0 50px 100px rgba(0,0,0,0.8);
            color: white;
            margin-top: 50px;
        }}

        /* Custom Buttons styling */
        .stButton > button {{
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid {accent}33 !important;
            color: white !important;
            border-radius: 15px !important;
            transition: 0.3s !important;
        }}
        .stButton > button:hover {{
            background: {accent}22 !important;
            border-color: {accent} !important;
            box-shadow: 0 0 20px {accent}44 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- 3. DESKTOP INTERFACE (HTML/CSS GRID) ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"""
        <div style='text-align:center; padding-top:10vh;'>
            <h1 style='color:white; letter-spacing:15px; font-weight:900; text-shadow:0 0 20px #00f2ff;'>MAXIMUSIK AI</h1>
            <p style='color:#00f2ff; font-family:monospace; letter-spacing:5px;'>NEURAL OPERATING SYSTEM v3.0</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("<br><br>", unsafe_allow_html=True)
    
    # Skapar navigations-grid med Streamlit-kolumner som agerar knappar
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        if st.button("🪄\n\nSYNTH", use_container_width=True, key="btn_s"):
            st.session_state.page = "SYNTH"; st.rerun()
    with c2:
        if st.button("🎧\n\nAUDIO", use_container_width=True, key="btn_a"):
            st.session_state.page = "AUDIO"; st.rerun()
    with c3:
        if st.button("🎬\n\nVIDEO", use_container_width=True, key="btn_v"):
            st.session_state.page = "VIDEO"; st.rerun()
    with c4:
        if st.button("🖼\n\nENGINE", use_container_width=True, key="btn_e"):
            st.session_state.page = "ENGINE"; st.rerun()
    with c5:
        if st.button("💀\n\nRESET", use_container_width=True, key="btn_r"):
            st.session_state.clear(); st.rerun()

# --- 4. MODULE CONTENT (INNEHÅLLET I KNAPPARNA) ---
else:
    _, center_win, _ = st.columns([0.1, 0.8, 0.1])
    
    with center_win:
        st.markdown(f'<div class="window-box">', unsafe_allow_html=True)
        
        # Header med stäng-knapp
        h1, h2 = st.columns([0.9, 0.1])
        h1.title(f"// {st.session_state.page}")
        if h2.button("✕", key="close"):
            st.session_state.page = "DESKTOP"; st.rerun()

        # --- MODUL: SYNTH (Bildgenerering) ---
        if st.session_state.page == "SYNTH":
            p = st.text_area("VAD SKALL VI SKAPA?", "A futuristic cyberpunk DJ booth, neon lighting, 8k cinematic")
            if st.button("EXECUTE GENERATION", use_container_width=True):
                with st.spinner("Neural networks processing..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    st.session_state.res_img = res
            if st.session_state.res_img:
                st.image(st.session_state.res_img, use_container_width=True)
                if st.button("SET AS SYSTEM WALLPAPER"):
                    st.session_state.wallpaper = st.session_state.res_img; st.rerun()

        # --- MODUL: AUDIO (Musik) ---
        elif st.session_state.page == "AUDIO":
            ap = st.text_input("BESKRIV LJUDET:", "Dark industrial techno beat, 130bpm")
            sec = st.slider("LÄNGD (SEKUNDER)", 5, 20, 10)
            if st.button("COMPOSE AUDIO", use_container_width=True):
                with st.spinner("Composing..."):
                    audio = replicate.run("facebookresearch/musicgen:7b539958", 
                                         input={"prompt": ap, "duration": sec})
                    st.audio(audio)

        # --- MODUL: VIDEO (Animering) ---
        elif st.session_state.page == "VIDEO":
            st.info("Animera din senaste skapelse från SYNTH.")
            if st.session_state.res_img:
                st.image(st.session_state.res_img, width=300)
                if st.button("ANIMATE IMAGE (SVD)", use_container_width=True):
                    with st.spinner("Rendering video..."):
                        video = replicate.run("stability-ai/stable-video-diffusion:3f04571e", 
                                             input={"input_image": st.session_state.res_img})
                        st.video(video)
            else:
                st.warning("Skapa en bild i SYNTH först!")

        # --- MODUL: ENGINE (System Wallpaper) ---
        elif st.session_state.page == "ENGINE":
            st.write("### SYSTEM ENVIRONMENT")
            wp_prompt = st.text_input("GENERERA NY VÄRLDS-BAKGRUND:", "Deep space nebula, violet and gold")
            if st.button("SYNC ENVIRONMENT", use_container_width=True):
                with st.spinner("Rewriting reality..."):
                    res = replicate.run("black-forest-labs/flux-schnell", 
                                       input={"prompt": wp_prompt, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = res; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

























