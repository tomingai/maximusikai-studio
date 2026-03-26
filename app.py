import streamlit as st
import replicate
import os
import random

# --- 1. EXPANDERAT GENRE-BIBLIOTEK & FÄRG-LOGIK ---
GENRE_MASTER = {
    "Cyberpunk Neon": {"prompt": "neon lights, rainy streets, high tech, cyan and magenta", "color": "#ff00ff"},
    "Space Noir": {"prompt": "monolithic structures, deep shadows, cinematic lighting, 1940s detective space aesthetic", "color": "#555555"},
    "Synthwave 80s": {"prompt": "retro-futurism, digital grid, sunset horizon, vibrant purple", "color": "#f0ff00"},
    "Solarpunk": {"prompt": "lush greenery, futuristic white architecture, sunlight, sustainable tech, bright blue sky", "color": "#00ff88"},
    "Dark Fantasy": {"prompt": "gothic castle, floating crystals, magical mist, moonlight", "color": "#aa00ff"},
    "Steampunk": {"prompt": "brass gears, steam engines, Victorian futuristic, copper and rust colors", "color": "#ff7700"},
    "Alien Ocean": {"prompt": "underwater bioluminescent flora, deep sea creatures, ethereal turquoise glow", "color": "#00ffd2"},
    "Post-Apocalyptic": {"prompt": "overgrown ruins, rusted steel, cinematic dust, gritty realism", "color": "#7a5533"},
    "Interstellar Void": {"prompt": "black hole, event horizon, swirling stars, cosmic horror aesthetic", "color": "#ffffff"}
}

def generate_custom_prompt(genre_name):
    env_list = ["A sprawling megacity", "A lonely research outpost", "A floating palace", "A hidden laboratory", "A cosmic portal"]
    env = random.choice(env_list)
    style_info = GENRE_MASTER[genre_name]["prompt"]
    return f"{env}, {style_info}, 8k resolution, masterpiece cinematic"

# --- 2. SETUP & SESSION ---
st.set_page_config(page_title="MAXIMUSIK AI OS", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

states = {
    "page": "DESKTOP",
    "wallpaper": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "brightness": 0.5,
    "library": [],
    "current_genre": "Cyberpunk Neon"
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

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
        h1, h2, h3, p, label, .stMarkdown {{
            color: {accent} !important; text-shadow: 0 0 15px {accent}77 !important;
            font-family: 'Courier New', monospace !important;
        }}
        .window-box {{
            background: rgba(0, 5, 12, 0.93); backdrop-filter: blur(50px);
            border: 2px solid {accent}33; border-radius: 40px; padding: 40px;
        }}
        .stButton > button {{
            background: rgba(0,0,0,0.6) !important; border: 1px solid {accent}44 !important;
            color: {accent} !important; border-radius: 20px !important; height: 80px !important;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 4. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:25px; padding-top:15vh; font-size:4rem;'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
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

        # --- UTBYGGD ENGINE-MODUL ---
        if st.session_state.page == "ENGINE":
            st.subheader("MULTIVERSE ENVIRONMENT SELECTOR")
            
            c1, c2 = st.columns([0.4, 0.6])
            with c1:
                st.session_state.brightness = st.slider("SYSTEM BRIGHTNESS", 0.0, 1.0, st.session_state.brightness)
                
                # GENRE-VÄLJARE
                selected_genre = st.selectbox("VÄLJ GENRE:", list(GENRE_MASTER.keys()))
                st.session_state.current_genre = selected_genre
                
                # AUTO-FÄRG SYNC
                if st.button("SYNC GENRE COLORS", use_container_width=True):
                    st.session_state.accent_color = GENRE_MASTER[selected_genre]["color"]
                    st.rerun()
                
                if st.button("🎲 SLUMPA ALLT", use_container_width=True):
                    st.session_state.current_genre = random.choice(list(GENRE_MASTER.keys()))
                    st.session_state.accent_color = GENRE_MASTER[st.session_state.current_genre]["color"]
                    st.rerun()

            with c2:
                # Generera prompt baserat på genre
                suggested_p = generate_custom_prompt(st.session_state.current_genre)
                final_p = st.text_area("PROMPT ENGINE:", value=suggested_p, height=150)
                
                if st.button("EXECUTE REALITY SHIFT", use_container_width=True):
                    with st.spinner("Neural Syncing Universe..."):
                        res = replicate.run("black-forest-labs/flux-schnell", 
                                           input={"prompt": final_p, "aspect_ratio": "16:9"})
                        url = res if isinstance(res, list) else res
                        st.session_state.wallpaper = url
                        st.session_state.library.append({"type": "image", "url": url, "prompt": final_p})
                        st.rerun()

        elif st.session_state.page == "SYNTH":
            p = st.text_area("BILD-PROMPT:")
            if st.button("GENERATE"):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p})
                st.image(res if isinstance(res, list) else res)

        elif st.session_state.page == "LIBRARY":
            for idx, item in enumerate(reversed(st.session_state.library)):
                st.image(item['url'], width=500)
                if st.button("SÄTT SOM BAKGRUND", key=f"lib_{idx}"):
                    st.session_state.wallpaper = item['url']; st.rerun()
        
        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("NEON OVERRIDE", st.session_state.accent_color)
            if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)




























