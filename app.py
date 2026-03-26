import streamlit as st
import replicate
import os
import time
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="MAXIMUSIKAI STUDIO PRO 2026", page_icon="⚡", layout="wide")

SPACE_BG = "https://images.unsplash.com"

if "gallery" not in st.session_state: st.session_state.gallery = []
if "user_db" not in st.session_state: st.session_state.user_db = {"ANONYM": 10, "TOMAS2026": 999}
if "app_bg" not in st.session_state: st.session_state.app_bg = SPACE_BG
if "agreed" not in st.session_state: st.session_state.agreed = False

# --- 2. NUCLEAR TRANSPARENCY ENGINE ---
def apply_design():
    bg_url = st.session_state.app_bg
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com');

        /* Bakgrund för hela sidan */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.1), rgba(0,0,0,0.3)), url("{bg_url}") !important;
            background-size: cover !important;
            background-attachment: fixed !important;
        }}

        /* RENSA ALLA BAKGRUNDER - DENNA ÄR KRITISK */
        div[data-testid="stVerticalBlock"], 
        div[data-testid="stHorizontalBlock"], 
        div[data-testid="stExpander"], 
        div[data-baseweb="textarea"], 
        div[data-baseweb="input"], 
        div[data-baseweb="base-input"],
        .stTextArea, .stTextInput, .stSelectbox, .stNumberInput,
        textarea, input {{
            background-color: transparent !important;
            background: transparent !important;
            box-shadow: none !important;
        }}

        /* SKAPA GLAS-EFFEKTEN ENBART PÅ RAMEN */
        textarea, input, .stSelectbox div[data-baseweb="select"] {{
            backdrop-filter: blur(20px) !important;
            border: 1px solid rgba(0, 242, 255, 0.5) !important;
            color: #00f2ff !important;
            font-family: 'Orbitron', sans-serif;
            border-radius: 0px !important;
        }}

        /* Sidomeny sync */
        [data-testid="stSidebar"] {{
            background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url("{bg_url}") !important;
            background-size: cover !important;
        }}

        /* Knappar */
        .stButton>button {{
            background: rgba(0, 242, 255, 0.05) !important;
            color: #00f2ff !important;
            border: 1px solid #00f2ff !important;
            font-family: 'Orbitron';
            text-transform: uppercase;
        }}
        
        .logo-text {{
            font-family: 'Orbitron'; font-size: 3.5rem; font-weight: 900; 
            color: #fff; text-align: center; letter-spacing: 10px;
            text-shadow: 0 0 20px #00f2ff;
        }}
        
        h1, h2, h3, p, label {{ color: white !important; font-family: 'Orbitron'; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. MISSION CONTROL ---
with st.sidebar:
    st.markdown("## 🛰️ CONTROL")
    artist_id = st.text_input("ID:", "ANONYM").upper()
    if artist_id not in st.session_state.user_db: st.session_state.user_db[artist_id] = 10
    st.markdown(f"# {st.session_state.user_db[artist_id]} UNITS")
    
    if st.button("🚀 SYNC SPACE"):
        res = replicate.run("black-forest-labs/flux-schnell", input={"prompt": "Deep space nebula 8k"})
        st.session_state.app_bg = str(res[0] if isinstance(res, list) else res)
        st.rerun()

# --- 4. MAIN INTERFACE ---
apply_design()
st.markdown('<div class="logo-text">MAXIMUSIKAI</div>', unsafe_allow_html=True)

if not st.session_state.agreed:
    if st.button("INITIALIZE STUDIO", use_container_width=True): 
        st.session_state.agreed = True; st.rerun()
    st.stop()

os.environ["REPLICATE_API_TOKEN"] = st.secrets.get("REPLICATE_API_TOKEN", "")

tabs = st.tabs(["🪄 MAGI", "🎬 REGI", "📚 ARKIV"])

with tabs[0]:
    col1, col2 = st.columns(2)
    # VISIONARY INPUT - Nu helt rensad från bakgrundsfärg
    prompt = col1.text_area("VISIONARY INPUT", placeholder="Skriv här...")
    aspect = col2.selectbox("RATIO", ["1:1", "16:9"])
    if st.button("🔥 GENERATE"):
        with st.status("Synthesizing..."):
            img = replicate.run("black-forest-labs/flux-schnell", input={"prompt": f"Space: {prompt}", "aspect_ratio": aspect})
            img_url = str(img[0] if isinstance(img, list) else img)
            st.session_state.gallery.append({"artist": artist_id, "name": prompt, "url": img_url})
            st.session_state.user_db[artist_id] -= 1
            st.rerun()

with tabs[1]:
    my_imgs = [p for p in st.session_state.gallery if p["artist"] == artist_id]
    if my_imgs:
        sel = st.selectbox("SOURCE", [p["name"][:30] for p in my_imgs])
        target = next(p for p in my_imgs if p["name"][:30] == sel)
        st.image(target["url"], use_container_width=True)
        if st.button("🎬 RENDER VIDEO"):
            vid = replicate.run("luma-ai/luma-dream-machine", input={"image_url": target["url"]})
            st.video(str(vid))

with tabs[2]:
    my_stuff = [p for p in st.session_state.gallery if p["artist"] == artist_id]
    cols = st.columns(3)
    for idx, p in enumerate(reversed(my_stuff)):
        with cols[idx % 3]:
            st.image(p["url"])
            if st.button("SET BG", key=f"bg_{idx}"):
                st.session_state.app_bg = p["url"]; st.rerun()

