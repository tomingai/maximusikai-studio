import streamlit as st
import replicate
import os
import json
import time
from datetime import datetime

# --- 1. KÄRN-KONFIGURATION ---
VERSION = "11.4.5-CONTRAST"
st.set_page_config(page_title=f"MAXIMUSIK AI OS v{VERSION}", layout="wide", initial_sidebar_state="collapsed")

if "REPLICATE_API_TOKEN" in st.secrets:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# --- 2. MOTOR & SANITIZER ---
def clean_prompt(text):
    if not text: return ""
    return str(text).replace('"', '').replace('Prompt:', '').strip()

def sanitize_url(output):
    if isinstance(output, list) and len(output) > 0: return str(output[0])
    return str(output)

# --- 3. INITIALISERING ---
if "page" not in st.session_state:
    st.session_state.update({
        "page": "SYNTH", "library": [], "accent": "#00f2ff", "last_img": None,
        "wallpaper": "https://images.unsplash.com",
        "style": "Photorealistic", "brightness": 5 
    })

# --- 4. UI ENGINE (ADAPTIV KONTRAST) ---
accent = st.session_state.accent
bright_val = (11 - st.session_state.brightness) / 10
# Dynamisk skugga: blir tyngre ju högre ljusstyrkan (st.session_state.brightness) är
shadow_intensity = st.session_state.brightness * 0.15

st.markdown(f"""
    <style>
    /* Bakgrund & Ljusstyrka-Overlay */
    [data-testid="stAppViewContainer"]::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0, 0, 0, {bright_val});
        z-index: -1; transition: 0.3s ease;
    }}
    [data-testid="stAppViewContainer"] {{ 
        background: url("{st.session_state.wallpaper}"); 
        background-size: cover; background-attachment: fixed; background-position: center;
    }}

    /* ADAPTIV TEXT (Glow & Shadow) */
    h1, h2, h3, label, p, .stMarkdown {{ 
        color: #FFFFFF !important; 
        text-shadow: 0px 0px {10 + (shadow_intensity*5)}px rgba(0,0,0,0.9), 
                     2px 2px {2 + shadow_intensity}px rgba(0,0,0,1) !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px;
    }}

    /* Glas-paneler */
    .glass {{ 
        background: rgba(0, 5, 15, 0.88); 
        backdrop-filter: blur(60px); 
        border: 1.5px solid {accent}55; 
        border-radius: 20px; padding: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}

    /* Inputs & Selectbox med hög kontrast */
    .stTextInput>div>div>input, .stSelectbox>div>div {{
        background-color: rgba(0, 0, 0, 0.6) !important;
        color: white !important;
        border: 1px solid {accent}88 !important;
        font-weight: bold !important;
    }}

    /* Knappar */
    .stButton>button {{ 
        border: 2px solid {accent}aa !important; 
        background: {accent}22 !important; 
        color: white !important; 
        font-weight: 900 !important; 
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. NAVIGATION & LUMINA CONTROL ---
st.markdown('<div class="glass" style="padding: 15px; margin-bottom: 25px;">', unsafe_allow_html=True)
c_nav, c_bright = st.columns([0.7, 0.3])

with c_nav:
    nc = st.columns(7)
    nav_icons = [("🏠","HOME",True), ("🪄","SYNTH",False), ("🎧","AUDIO",True), ("🎬","MOVIE",True), ("📚","ARKIV",False), ("🖼","ENGINE",False), ("⚙️","SYSTEM",True)]
    for i, (icon, target, locked) in enumerate(nav_icons):
        if not locked:
            if nc[i].button(icon, key=f"nav_{target}"): 
                st.session_state.page = target; st.rerun()
        else: nc[i].markdown(f'<p style="text-align:center; opacity:0.2; font-size:1.5rem; margin:0;">{icon}</p>', unsafe_allow_html=True)

with c_bright:
    st.session_state.brightness = st.slider("🔅 LUMINA (1-10)", 1, 10, st.session_state.brightness)

st.markdown('</div>', unsafe_allow_html=True)

# --- 6. MODULER ---
if st.session_state.page == "SYNTH":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown(f"<h2 style='color:{accent}; letter-spacing:5px;'>🪄 SYNTH PRECISION</h2>", unsafe_allow_html=True)
    
    user_p = st.text_input("VAD SKALL VI SKAPA?", placeholder="Skriv din vision...")
    
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.session_state.style = st.selectbox("STIL:", ["Photorealistic", "Cinematic", "Cyberpunk", "Digital Art"])
    with col2:
        aspect = st.selectbox("FORMAT:", ["1:1", "16:9", "9:16"], index=1)

    if st.button("🚀 STARTA NEURAL KEDJA"):
        if user_p:
            prog = st.progress(0)
            with st.status("Neural Pipeline...") as status:
                res_llm = replicate.run("meta/meta-llama-3-8b-instruct", input={"prompt": f"Expand to 8k {st.session_state.style} prompt: {user_p}"})
                expanded = clean_prompt("".join(list(res_llm)))
                
                flux_res = replicate.run("black-forest-labs/flux-schnell", {"prompt": expanded, "aspect_ratio": aspect.replace(":", "x")})
                url = sanitize_url(flux_res)
                
                if url:
                    st.session_state.last_img = url
                    st.session_state.library.append({"url": url, "prompt": user_p, "ts": datetime.now().strftime("%H:%M")})
                    st.rerun()
    
    if st.session_state.last_img:
        st.divider()
        st.image(st.session_state.last_img, use_column_width=True)
        if st.button("🖼 SÄTT SOM BAKGRUND"): 
            st.session_state.wallpaper = st.session_state.last_img
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "ARKIV":
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.subheader("📚 SYSTEM ARCHIVE")
    grid = st.columns(3)
    for i, item in enumerate(reversed(st.session_state.library)):
        with grid[i % 3]:
            st.image(item['url'], use_column_width=True)
            if st.button("VÄLJ", key=f"ark_{i}"):
                st.session_state.last_img = item['url']
                st.session_state.wallpaper = item['url']; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)























































































































































