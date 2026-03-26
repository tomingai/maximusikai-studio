import streamlit as st
import replicate
import os
import json

# --- 1. CONFIG & SESSION ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Session States
states = {
    "active_window": None,
    "app_bg": "https://images.unsplash.com",
    "accent_color": "#00f2ff",
    "gallery": []
}
for key, val in states.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 2. DESIGN ENGINE (SPACE OS + DYNAMISK BAKGRUND) ---
def apply_ui():
    accent = st.session_state.accent_color
    bg_url = st.session_state.app_bg
    
    st.markdown(f"""
        <style>
        /* HUVUDBAKGRUND */
        [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6)), 
                              url("{bg_url}") !important;
            background-size: cover !important; 
            background-position: center !important;
            background-attachment: fixed !important;
        }}
        
        [data-testid="stHeader"], .main, [data-testid="stAppViewBlockContainer"] {{
            background: transparent !important;
        }}

        /* TITEL */
        .os-title {{
            position: fixed; top: 40px; left: 50px;
            color: white; font-size: 2rem; font-weight: 900;
            letter-spacing: 8px; text-shadow: 0 0 20px {accent};
            font-family: monospace; z-index: 100;
        }}

        /* GIGANTISKA IKON-KNAPPAR (FRÅN GAMLA KODEN) */
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

        /* IKON-BILDER FÖR KNAPPARNA */
        div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stHorizontalBlock"] > div:nth-child(4) button {{ background-image: url('https://images.unsplash.com') !important; }}
        div[data-testid="stHorizontalBlock"] > div:nth-child(5) button {{ background-image: url('https://images.unsplash.com') !important; }}

        .label {{ 
            text-align: center; color: {accent}; font-family: monospace; 
            font-size: 0.9rem; margin-top: 15px; letter-spacing: 2px; font-weight: bold;
        }}

        /* FÖNSTER DESIGN */
        .window-content {{
            background: rgba(0, 5, 12, 0.9) !important;
            backdrop-filter: blur(40px);
            border: 1px solid {accent}33;
            border-radius: 40px;
            padding: 40px;
            color: white;
            box-shadow: 0 50px 150px rgba(0,0,0,0.9);
        }}
        
        .stTextArea textarea, .stTextInput input {{
            background-color: rgba(255,255,255,0.05) !important;
            color: white !important;
            border: 1px solid {accent}22 !important;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_ui()

# --- 3. DESKTOP VIEW (IKON-GRID) ---
if st.session_state.active_window is None:
    st.markdown("<div class='os-title'>MAXIMUSIK AI</div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 25vh;'></div>", unsafe_allow_html=True)
    
    cols = st.columns(5)
    apps = [("MAGI", "m"), ("REGI", "r"), ("MUSIK", "mu"), ("ENGINE", "e"), ("SYSTEM", "s")]
    
    for i, (name, key) in enumerate(apps):
        with cols[i]:
            if st.button(name, key=key):
                st.session_state.active_window = name
                st.rerun()
            st.markdown(f'<p class="label">{name}</p>', unsafe_allow_html=True)

# --- 4. WINDOW MODULER ---
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

        if st.session_state.active_window == "MAGI":
            prompt = st.text_area("VAD SKALL VI SKAPA?", "En futuristisk stad i neon")
            if st.button("GENERERA BILD"):
                with st.spinner("AI arbetar..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt})
                    st.session_state.gallery.append(res)
                    # Sätter bilden som bakgrund direkt för wow-effekt
                    st.session_state.app_bg = res 
                    st.rerun()
            if st.session_state.gallery:
                st.image(st.session_state.gallery[-1])

        elif st.session_state.active_window == "ENGINE":
            st.write("### 🖼 Bakgrundsinställningar")
            new_bg = st.text_input("Klistra in bild-URL:", st.session_state.app_bg)
            if st.button("UPPDATERA BAKGRUND"):
                st.session_state.app_bg = new_bg
                st.rerun()
            
            prompt_bg = st.text_area("Eller skapa en ny bakgrund med AI:")
            if st.button("GENERERA NY BAKGRUND"):
                with st.spinner("Skapar..."):
                    res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": prompt_bg, "aspect_ratio": "16:9"})
                    st.session_state.app_bg = res
                    st.rerun()

        elif st.session_state.active_window == "SYSTEM":
            st.session_state.accent_color = st.color_picker("Välj accentfärg:", st.session_state.accent_color)
            if st.button("Hard Reset"):
                st.session_state.clear()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

























