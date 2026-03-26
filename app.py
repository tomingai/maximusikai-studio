import streamlit as st
import replicate
import os

# --- 1. CONFIG & SESSION ---
st.set_page_config(page_title="MAXIMUSIK AI OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Initiera alla systemvariabler
states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "library": [],
    "res_img": None,
    "res_audio": None,
    "accent_color": "#00f2ff"
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 2. CSS ENGINE ---
def apply_ui():
    accent = st.session_state.accent_color
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
        
        /* Fönster-effekt */
        .window-box {{
            background: rgba(0, 5, 10, 0.9);
            backdrop-filter: blur(40px);
            border: 1px solid {accent}44;
            border-radius: 35px; padding: 40px; color: white;
            box-shadow: 0 40px 100px rgba(0,0,0,0.8);
        }}

        /* Knappar på Desktop */
        .stButton > button {{
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid {accent}33 !important;
            color: white !important;
            border-radius: 20px !important;
            height: 120px !important;
            font-size: 1.2rem !important;
            transition: 0.4s !important;
        }}
        .stButton > button:hover {{
            border-color: {accent} !important;
            box-shadow: 0 0 30px {accent}44 !important;
            transform: scale(1.05);
        }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP VIEW ---
if st.session_state.page == "DESKTOP":
    st.markdown("<h1 style='text-align:center; color:white; letter-spacing:15px; padding-top:10vh; text-shadow: 0 0 20px #00f2ff;'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    st.write("<br><br>", unsafe_allow_html=True)
    
    cols = st.columns(5)
    apps = [
        ("🪄 SYNTH", "SYNTH"), 
        ("🎧 AUDIO", "AUDIO"), 
        ("📚 ARKIV", "LIBRARY"), 
        ("🖼 ENGINE", "ENGINE"), 
        ("⚙️ SYSTEM", "SYSTEM")
    ]
    
    for i, (label, target) in enumerate(apps):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"nav_{target}"):
                st.session_state.page = target
                st.rerun()

# --- 4. WINDOWS (MODUL-INNEHÅLL) ---
else:
    _, win_col, _ = st.columns([0.05, 0.9, 0.05])
    with win_col:
        st.markdown('<div class="window-box">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.title(f"// {st.session_state.page}")
        if h2.button("✕", key="close_win"): 
            st.session_state.page = "DESKTOP"; st.rerun()
        
        st.markdown("<hr style='border-color:rgba(255,255,255,0.1)'>", unsafe_allow_html=True)

        # --- SYNTH: Bildgenerator ---
        if st.session_state.page == "SYNTH":
            p = st.text_area("PROMPT (Visualisera något):", "A cybernetic dragon in a neon rain forest, 8k")
            if st.button("EXECUTE NEURAL SYNTH"):
                with st.spinner("Genererar bild..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                    url = res[0] if isinstance(res, list) else res
                    st.session_state.res_img = url
                    st.session_state.library.append({"type": "image", "url": url, "prompt": p})
                    st.rerun()
            if st.session_state.res_img:
                st.image(st.session_state.res_img, use_container_width=True)

        # --- AUDIO: Musikgenerator ---
        elif st.session_state.page == "AUDIO":
            ap = st.text_input("BESKRIV MUSIKEN:", "Epic cinematic synthwave with heavy drums")
            dur = st.slider("LÄNGD (SEKUNDER):", 5, 20, 10)
            if st.button("COMPOSE SOUND"):
                with st.spinner("Komponerar..."):
                    res = replicate.run("meta/musicgen:b05b39c7", input={"prompt": ap, "duration": dur})
                    st.session_state.res_audio = res
                    st.session_state.library.append({"type": "audio", "url": res, "prompt": ap})
                    st.rerun()
            if st.session_state.res_audio:
                st.audio(st.session_state.res_audio)

        # --- LIBRARY: Arkivet ---
        elif st.session_state.page == "LIBRARY":
            if not st.session_state.library:
                st.info("Arkivet är tomt. Skapa bilder eller musik först.")
            else:
                for item in reversed(st.session_state.library):
                    with st.container():
                        st.write(f"**Prompt:** {item['prompt']}")
                        if item['type'] == "image":
                            st.image(item['url'], width=400)
                            if st.button("SÄTT SOM BAKGRUND", key=item['url']):
                                st.session_state.wallpaper = item['url']; st.rerun()
                        else:
                            st.audio(item['url'])
                        st.markdown("---")

        # --- ENGINE: Miljö-generator ---
        elif st.session_state.page == "ENGINE":
            st.subheader("Skapa en ny systemmiljö (16:9)")
            ep = st.text_area("MILJÖ-PROMPT:", "Abstract hyperspace tunnel, deep blue neon")
            if st.button("GENERATE ENVIRONMENT"):
                with st.spinner("Neural Sync..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": ep, "aspect_ratio": "16:9"})
                    url = res[0] if isinstance(res, list) else res
                    st.session_state.wallpaper = url
                    st.session_state.library.append({"type": "image", "url": url, "prompt": ep})
                    st.rerun()

        # --- SYSTEM: Inställningar ---
        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("UI ACCENT FÄRG:", st.session_state.accent_color)
            st.write("Systemstatus: **ONLINE**")
            if st.button("HARD RESET (Rensa allt)"):
                st.session_state.clear()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

























