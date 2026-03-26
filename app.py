import streamlit as st
import replicate
import os

# --- 1. CONFIG & SESSION ---
st.set_page_config(page_title="MAXIMUSIK AI", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

states = {
    "page": "DESKTOP",
    "lang": "Svenska",
    "accent_color": "#00f2ff",
    "bg_brightness": 0.6, # STANDARD LJUSSTYRKA (0.0 - 1.0)
    "wallpaper": "https://images.unsplash.com",
    "library": [],
    "res_img": None
}
for key, val in states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 2. DYNAMISK UI ENGINE (MED LJUSSTYRKA) ---
def apply_ui():
    accent = st.session_state.accent_color
    bright = st.session_state.bg_brightness
    # Ju högre ljusstyrka på reglaget, desto lägre opacity på det svarta lagret
    overlay_opacity = 1.0 - bright 
    
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(rgba(0,0,0,{overlay_opacity}), rgba(0,0,0,{overlay_opacity + 0.1})), 
                        url("{st.session_state.wallpaper}") !important;
            background-size: cover !important; 
            background-attachment: fixed !important;
            transition: 0.5s ease-in-out;
        }}
        [data-testid="stHeader"], .main {{ background: transparent !important; }}
        
        h1, h2, h3, p, label, .stMarkdown, .stSelectbox label, .stTextArea label {{
            color: {accent} !important;
            text-shadow: 0 0 15px {accent}55 !important;
            font-family: 'Courier New', monospace !important;
        }}
        
        .window-box {{
            background: rgba(0, 5, 12, 0.9); 
            backdrop-filter: blur(40px);
            border: 2px solid {accent}22; 
            border-radius: 40px; padding: 40px;
        }}

        .stButton > button {{
            background: rgba(0,0,0,0.6) !important; 
            border: 1px solid {accent}44 !important;
            color: {accent} !important; 
            border-radius: 20px !important; 
            height: 100px !important;
            font-weight: 900; 
            letter-spacing: 3px;
        }}
        
        /* Slider styling */
        .stSlider [data-baseweb="slider"] div {{ background-color: {accent} !important; }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP ---
if st.session_state.page == "DESKTOP":
    st.markdown(f"<h1 style='text-align:center; letter-spacing:20px; padding-top:15vh; font-size:4rem;'>MAXIMUSIK AI</h1>", unsafe_allow_html=True)
    cols = st.columns(5)
    apps = [("🪄 SYNTH", "SYNTH"), ("🎧 AUDIO", "AUDIO"), ("📚 ARKIV", "LIBRARY"), ("🖼 ENGINE", "ENGINE"), ("⚙️ SYSTEM", "SYSTEM")]
    for i, (label, target) in enumerate(apps):
        with cols[i]:
            if st.button(label, use_container_width=True):
                st.session_state.page = target; st.rerun()

# --- 4. WINDOWS ---
else:
    _, win_col, _ = st.columns([0.05, 0.9, 0.05])
    with win_col:
        st.markdown('<div class="window-box">', unsafe_allow_html=True)
        h1, h2 = st.columns([0.9, 0.1])
        h1.markdown(f"<h2>// {st.session_state.page}</h2>", unsafe_allow_html=True)
        if h2.button("✕"): st.session_state.page = "DESKTOP"; st.rerun()

        # --- ENGINE (Ljusstyrka kontroll) ---
        if st.session_state.page == "ENGINE":
            st.write("### ENVIRONMENT CONTROL")
            st.session_state.bg_brightness = st.slider("BAKGRUNDENS LJUSSTYRKA", 0.0, 1.0, st.session_state.bg_brightness)
            
            p = st.text_area("PROMPT FÖR NY MILJÖ:")
            if st.button("REWRITE REALITY", use_container_width=True):
                with st.spinner("Syncing..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": p, "aspect_ratio": "16:9"})
                    st.session_state.wallpaper = str(res)
                    st.rerun()

        # --- SYSTEM ---
        elif st.session_state.page == "SYSTEM":
            st.session_state.accent_color = st.color_picker("UI ACCENT:", st.session_state.accent_color)
            st.session_state.bg_brightness = st.slider("SYSTEM BRIGHTNESS", 0.0, 1.0, st.session_state.bg_brightness)
            if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

        # --- ÖVRIGA MODULER (Förenklade) ---
        elif st.session_state.page == "SYNTH":
            sp = st.text_area("BILD-PROMPT:")
            if st.button("SYNTHESIZE"):
                res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": sp})
                st.session_state.res_img = str(res)
                st.rerun()
            if st.session_state.res_img: st.image(st.session_state.res_img)

        st.markdown('</div>', unsafe_allow_html=True)




























